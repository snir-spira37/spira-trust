#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_SEED = 77020260710


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Select a predeclared PEP 770 pilot set from a snapshot manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    selected = [
        item
        for item in manifest.get("packages", [])
        if item.get("selection_status") == "SELECTED" and item.get("selected_wheel")
    ]
    selected.sort(key=lambda item: (item["package"], item["selected_wheel"]["filename"]))

    picks: list[dict[str, Any]] = []
    used: set[str] = set()

    known_multi = next((item for item in selected if item.get("package") == "a3s-box"), None)
    if known_multi:
        add_pick(picks, used, known_multi, "known_multi_sbom_from_v3_smoke")

    for item in sorted(selected, key=lambda item: int(item["selected_wheel"].get("size") or 0), reverse=True):
        if count_reason(picks, "large_wheel") >= 3:
            break
        add_pick(picks, used, item, "large_wheel")

    for item in sorted(selected, key=lambda item: int(item["selected_wheel"].get("size") or 0)):
        if count_reason(picks, "small_wheel") >= 3:
            break
        add_pick(picks, used, item, "small_wheel")

    rng = random.Random(args.seed)
    remaining = [item for item in selected if item["package"] not in used]
    rng.shuffle(remaining)
    for item in remaining:
        if count_reason(picks, "seeded_random") >= 3:
            break
        add_pick(picks, used, item, "seeded_random")

    report = {
        "schema": "SPIRA_PEP770_SURVEY_PILOT_SELECTION_V1",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source_manifest": str(manifest_path).replace("\\", "/"),
        "methodology": manifest.get("methodology"),
        "seed": args.seed,
        "selection_rule": [
            "one known multi-SBOM smoke case when present: a3s-box",
            "three largest selected wheels by PyPI file size",
            "three smallest selected wheels by PyPI file size",
            "three seeded-random selected wheels from the remaining pool",
            "deduplicate by package name"
        ],
        "not_claimed": [
            "pilot is edge-case discovery, not a statistical sample",
            "pilot results are reported separately and never used as full-corpus statistics",
            "known multi-SBOM status comes from the pre-pilot V3 smoke run, not from the snapshot manifest"
        ],
        "picks": picks,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {output} with {len(picks)} pilot picks")
    return 0


def add_pick(picks: list[dict[str, Any]], used: set[str], item: dict[str, Any], reason: str) -> None:
    package = str(item["package"])
    if package in used:
        return
    wheel = item["selected_wheel"]
    picks.append(
        {
            "package": package,
            "version": wheel.get("version"),
            "filename": wheel.get("filename"),
            "url": wheel.get("url"),
            "sha256": wheel.get("sha256"),
            "size": wheel.get("size"),
            "platform_class": wheel.get("platform_class"),
            "selection_reason": reason,
        }
    )
    used.add(package)


def count_reason(picks: list[dict[str, Any]], reason: str) -> int:
    return sum(1 for item in picks if item.get("selection_reason") == reason)


if __name__ == "__main__":
    raise SystemExit(main())
