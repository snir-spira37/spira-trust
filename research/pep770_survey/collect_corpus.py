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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect a reproducible PEP 770 survey corpus manifest.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output", required=True, help="Path for corpus manifest JSON.")
    parser.add_argument("--download-dir", help="Optional directory for selected wheels.")
    parser.add_argument("--max-pages", type=int, help="Limit pypi-tea package-list pages for smoke runs.")
    parser.add_argument("--limit-packages", type=int, help="Limit selected packages after grouping for pilot runs.")
    parser.add_argument("--sleep", type=float, default=0.15, help="Delay between HTTP requests.")
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
    selected = []
    for index, (name, versions) in enumerate(sorted(grouped.items()), start=1):
        if args.limit_packages and index > args.limit_packages:
            break
        entry = select_package_wheel(args.base_url, name, versions, sleep=args.sleep)
        if download_dir and entry.get("selected_wheel"):
            download_selected_wheel(entry, download_dir)
        selected.append(entry)

    manifest = {
        "schema": "SPIRA_PEP770_SURVEY_CORPUS_MANIFEST_V1",
        "created_at": started_at,
        "methodology": "research/pep770_survey/methodology.v1.json",
        "source": {
            "base_url": args.base_url,
            "package_listing_pages_seen": pages_seen,
            "package_listing_total_pages_reported": total_pages,
            "package_versions_seen": len(package_versions),
            "packages_grouped": len(grouped),
            "limit_packages": args.limit_packages,
            "max_pages": args.max_pages,
        },
        "selection_rule": "For each package, use pypi-tea package pages to identify wheel filenames with embedded SBOMs, then select the newest x86_64/amd64 wheel by PyPI upload time, falling back to newest py3-none-any wheel.",
        "packages": selected,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {output} with {len(selected)} selected package entries")
    return 0


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
    selected["embedded_sbom_paths"] = embedded_sbom_paths(target)
    selected["embedded_sbom_count"] = len(selected["embedded_sbom_paths"])


def embedded_sbom_paths(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        return sorted(
            name
            for name in archive.namelist()
            if ".dist-info/sboms/" in name and not name.endswith("/")
        )


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
