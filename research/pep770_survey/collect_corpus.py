#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://pypi.sbomify.com"
USER_AGENT = "spira-trust-pep770-survey/0.1 (+https://github.com/snir-spira37/spira-trust)"
METHODOLOGY_PATH = "research/pep770_survey/methodology.v3.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect a reproducible PEP 770 survey corpus manifest.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output", required=True, help="Path for corpus manifest JSON.")
    parser.add_argument("--download-dir", help="Optional directory for selected wheels.")
    parser.add_argument("--max-pages", type=int, help="Limit pypi-tea package-list pages for smoke runs.")
    parser.add_argument("--limit-packages", type=int, help="Limit selected packages after grouping for pilot runs.")
    parser.add_argument("--sleep", type=float, default=0.15, help="Delay between HTTP requests.")
    parser.add_argument("--methodology", default=METHODOLOGY_PATH)
    parser.add_argument("--resume", action="store_true", help="Resume from an existing output manifest.")
    parser.add_argument("--checkpoint-every", type=int, default=1, help="Write manifest every N selected packages.")
    args = parser.parse_args(argv)

    output = Path(args.output)
    download_dir = Path(args.download_dir) if args.download_dir else None
    if download_dir:
        download_dir.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    package_versions, pages_seen, total_pages = collect_package_versions(
        args.base_url, max_pages=args.max_pages, sleep=args.sleep
    )
    grouped = group_versions(package_versions)
    manifest = build_manifest(
        created_at=started_at,
        methodology=args.methodology,
        base_url=args.base_url,
        pages_seen=pages_seen,
        total_pages=total_pages,
        package_versions=package_versions,
        grouped=grouped,
        limit_packages=args.limit_packages,
        max_pages=args.max_pages,
        packages=[],
    )
    if args.resume and output.exists():
        existing = json.loads(output.read_text(encoding="utf-8"))
        existing_packages = existing.get("packages", [])
        if not isinstance(existing_packages, list):
            raise SystemExit(f"cannot resume: {output} has no package list")
        manifest["created_at"] = existing.get("created_at", manifest["created_at"])
        manifest["resumed_at"] = started_at
        manifest["packages"] = existing_packages
    selected = manifest["packages"]
    completed = {str(item.get("package")) for item in selected if isinstance(item, dict)}
    for index, (name, versions) in enumerate(sorted(grouped.items()), start=1):
        if args.limit_packages and index > args.limit_packages:
            break
        if name in completed:
            continue
        entry = select_package_wheel(args.base_url, name, versions, sleep=args.sleep)
        if download_dir and entry.get("selected_wheel"):
            download_selected_wheel(entry, download_dir)
        selected.append(entry)
        if args.checkpoint_every > 0 and len(selected) % args.checkpoint_every == 0:
            write_manifest(output, manifest)
    manifest["completed_at"] = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    write_manifest(output, manifest)
    print(f"wrote {output} with {len(selected)} selected package entries")
    return 0


def build_manifest(
    *,
    created_at: str,
    methodology: str,
    base_url: str,
    pages_seen: int,
    total_pages: int | None,
    package_versions: set[tuple[str, str]],
    grouped: dict[str, set[str]],
    limit_packages: int | None,
    max_pages: int | None,
    packages: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": "SPIRA_PEP770_SURVEY_CORPUS_MANIFEST_V3",
        "created_at": created_at,
        "methodology": methodology,
        "source": {
            "base_url": base_url,
            "live_stats": fetch_live_stats(base_url),
            "package_listing_pages_seen": pages_seen,
            "package_listing_total_pages_reported": total_pages,
            "package_versions_seen": len(package_versions),
            "packages_grouped": len(grouped),
            "limit_packages": limit_packages,
            "max_pages": max_pages,
        },
        "selection_rule": "For each PyPI project, use pypi-tea package pages to identify wheel filenames with embedded SBOMs, then select the newest x86_64/amd64 wheel by PyPI upload time, falling back to newest py3-none-any wheel.",
        "packages": packages,
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def collect_package_versions(base_url: str, *, max_pages: int | None, sleep: float) -> tuple[set[tuple[str, str]], int, int | None]:
    package_versions: set[tuple[str, str]] = set()
    page = 1
    pages_seen = 0
    total_pages: int | None = None
    while True:
        if max_pages and page > max_pages:
            break
        body = http_get_text(f"{base_url.rstrip('/')}/packages?page={page}")
        pages_seen += 1
        if total_pages is None:
            total_pages = parse_total_pages(body)
        links = parse_package_links(body)
        if not links:
            break
        package_versions.update(links)
        if total_pages is not None and page >= total_pages:
            break
        page += 1
        time.sleep(sleep)
    return package_versions, pages_seen, total_pages


def parse_total_pages(body: str) -> int | None:
    match = re.search(r"Page\s+\d+\s+of\s+(\d+)", body)
    return int(match.group(1)) if match else None


def parse_package_links(body: str) -> set[tuple[str, str]]:
    links = set()
    for raw_name, raw_version in re.findall(r'href="/package/([^"/]+)/([^"/]+)"', body):
        name = urllib.parse.unquote(html.unescape(raw_name))
        version = urllib.parse.unquote(html.unescape(raw_version))
        links.add((name, version))
    return links


def group_versions(package_versions: set[tuple[str, str]]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = {}
    for name, version in package_versions:
        grouped.setdefault(name, set()).add(version)
    return grouped


def select_package_wheel(base_url: str, name: str, versions: set[str], *, sleep: float) -> dict[str, Any]:
    pypi = http_get_json(f"https://pypi.org/pypi/{urllib.parse.quote(name)}/json")
    candidates: list[dict[str, Any]] = []
    errors = []
    for version in sorted(versions):
        try:
            page = http_get_text(f"{base_url.rstrip('/')}/package/{urllib.parse.quote(name)}/{urllib.parse.quote(version)}")
            sbom_wheel_filenames = parse_wheel_filenames(page)
            release_files = pypi.get("releases", {}).get(version, [])
            by_filename = {item.get("filename"): item for item in release_files if item.get("packagetype") == "bdist_wheel"}
            for filename in sbom_wheel_filenames:
                file_info = by_filename.get(filename)
                if not file_info:
                    continue
                candidates.append(candidate_from_file(name, version, filename, file_info))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append({"version": version, "error": str(exc)})
        time.sleep(sleep)

    selected = choose_candidate(candidates)
    entry: dict[str, Any] = {
        "package": name,
        "versions_with_sbom_seen": sorted(versions),
        "candidate_wheel_count": len(candidates),
        "selection_errors": errors,
        "selected_wheel": selected,
    }
    if selected is None:
        entry["selection_status"] = "NO_MATCHING_X86_64_OR_PY3_NONE_ANY_WHEEL"
    else:
        entry["selection_status"] = "SELECTED"
    return entry


def parse_wheel_filenames(body: str) -> set[str]:
    return {html.unescape(item) for item in re.findall(r"([A-Za-z0-9_.+-]+\.whl)", body)}


def candidate_from_file(name: str, version: str, filename: str, file_info: dict[str, Any]) -> dict[str, Any]:
    digests = file_info.get("digests") or {}
    return {
        "package": name,
        "version": version,
        "filename": filename,
        "url": file_info.get("url"),
        "sha256": digests.get("sha256"),
        "upload_time_iso_8601": file_info.get("upload_time_iso_8601"),
        "size": file_info.get("size"),
        "yanked": bool(file_info.get("yanked")),
        "platform_class": platform_class(filename),
    }


def platform_class(filename: str) -> str:
    lowered = filename.lower()
    if "x86_64" in lowered or "amd64" in lowered:
        return "x86_64"
    if "py3-none-any" in lowered:
        return "py3-none-any"
    return "other"


def choose_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    supported = [item for item in candidates if item.get("platform_class") in {"x86_64", "py3-none-any"}]
    if not supported:
        return None
    x86 = [item for item in supported if item.get("platform_class") == "x86_64"]
    pool = x86 or supported
    return max(pool, key=lambda item: str(item.get("upload_time_iso_8601") or ""))


def download_selected_wheel(entry: dict[str, Any], download_dir: Path) -> None:
    selected = entry.get("selected_wheel")
    if not selected:
        return
    filename = selected["filename"]
    target = download_dir / filename
    data = http_get_bytes(selected["url"])
    digest = hashlib.sha256(data).hexdigest()
    selected["downloaded_path"] = str(target)
    selected["downloaded_sha256"] = digest
    selected["download_sha256_matches_pypi"] = digest == selected.get("sha256")
    target.write_bytes(data)
    selected["embedded_sboms"] = embedded_sbom_records(target)
    selected["embedded_sbom_paths"] = [item["path"] for item in selected["embedded_sboms"]]
    selected["embedded_sbom_count"] = len(selected["embedded_sboms"])
    selected["sbom_generators"] = summarize_generators(selected["embedded_sboms"])


def embedded_sbom_records(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        records = []
        for name in sorted(archive.namelist()):
            if ".dist-info/sboms/" not in name or name.endswith("/"):
                continue
            data = archive.read(name)
            records.append(
                {
                    "path": name,
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "format_hint": sbom_format_hint(name),
                    "generator_tools_raw": extract_generator_tools(data, name),
                }
            )
        for record in records:
            record["generator_families"] = generator_families(record.get("generator_tools_raw") or [])
        return records


def sbom_format_hint(path: str) -> str:
    lowered = path.lower()
    if lowered.endswith(".json"):
        return "json"
    if lowered.endswith(".spdx"):
        return "spdx"
    if lowered.endswith(".xml"):
        return "xml"
    return "unknown"


def extract_generator_tools(data: bytes, path: str) -> list[dict[str, Any]]:
    if sbom_format_hint(path) != "json":
        return []
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [{"family": "UNPARSEABLE"}]
    if not isinstance(payload, dict) or payload.get("bomFormat") != "CycloneDX":
        return []
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        return []
    tools = metadata.get("tools")
    return normalize_tools(tools)


def normalize_tools(tools: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if isinstance(tools, list):
        for item in tools:
            if isinstance(item, dict):
                records.append({key: item.get(key) for key in ("vendor", "name", "version") if item.get(key)})
        return records
    if isinstance(tools, dict):
        nested = []
        for key in ("components", "services", "tools"):
            value = tools.get(key)
            if isinstance(value, list):
                nested.extend(value)
        if nested:
            return normalize_tools(nested)
        if any(tools.get(key) for key in ("vendor", "name", "version")):
            records.append({key: tools.get(key) for key in ("vendor", "name", "version") if tools.get(key)})
    return records


def generator_families(tools: list[dict[str, Any]]) -> list[str]:
    if any(tool.get("family") == "UNPARSEABLE" for tool in tools):
        return ["UNPARSEABLE"]
    names = " ".join(
        str(tool.get("name") or "") + " " + str(tool.get("vendor") or "")
        for tool in tools
    ).lower()
    if not names.strip():
        return ["UNKNOWN"]
    families = []
    if "auditwheel" in names:
        families.append("AUDITWHEEL")
    if "maturin" in names:
        families.append("MATURIN")
    if "cargo-cyclonedx" in names or "cyclonedx-rust-cargo" in names:
        families.append("CARGO_CYCLONEDX")
    if "sbomify" in names:
        families.append("SBOMIFY")
    if "syft" in names:
        families.append("SYFT")
    if "cyclonedx-py" in names or "cyclonedx-python" in names:
        families.append("CYCLONEDX_PYTHON")
    return sorted(set(families or ["OTHER"]))


def summarize_generators(sboms: list[dict[str, Any]]) -> dict[str, Any]:
    generators: list[dict[str, Any]] = []
    families_set = set()
    for item in sboms:
        for family in item.get("generator_families") or ["UNKNOWN"]:
            families_set.add(str(family))
        for tool in item.get("generator_tools_raw") or []:
            generators.append(
                {
                    "sbom_path": item.get("path"),
                    "family": item.get("generator_families") or ["UNKNOWN"],
                    "tool": tool,
                }
            )
    families = sorted(families_set or {"UNKNOWN"})
    if not families:
        primary = "UNKNOWN"
    elif len(families) == 1:
        primary = families[0]
    else:
        primary = "MIXED"
    return {
        "summary": primary,
        "families": families,
        "tools": generators,
    }


def fetch_live_stats(base_url: str) -> dict[str, Any] | None:
    try:
        return http_get_json(f"{base_url.rstrip('/')}/stats")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def http_get_json(url: str) -> dict[str, Any]:
    return json.loads(http_get_text(url))


def http_get_text(url: str) -> str:
    return http_get_bytes(url).decode("utf-8")


def http_get_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


if __name__ == "__main__":
    raise SystemExit(main())
