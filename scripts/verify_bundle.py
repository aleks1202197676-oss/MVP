#!/usr/bin/env python3
"""Verify required paths exist in the generated bundle zip."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile

REQUIRED_PATHS = [
    "contracts/meta/START_HERE.md",
    "contracts/meta/project_state.yml",
    "contracts/meta/COMPILED_MEMORY.md",
    "pipelines/run_all.py",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bundle_path",
        nargs="?",
        default="data/ai_contract/latest/latest_bundle.zip",
        help="Path to bundle zip (default: %(default)s)",
    )
    parser.add_argument(
        "--preview-count",
        type=int,
        default=30,
        help="How many archive entries to print for diagnostics on failure.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle_path = Path(args.bundle_path)

    if not bundle_path.exists():
        print(f"[ERROR] Bundle not found: {bundle_path}")
        return 1

    with ZipFile(bundle_path) as bundle:
        names = bundle.namelist()
        names_set = set(names)

    missing = [path for path in REQUIRED_PATHS if path not in names_set]
    if missing:
        print(f"[ERROR] Missing required bundle entries in {bundle_path}:")
        for path in missing:
            print(f"  - {path}")

        preview_count = max(0, args.preview_count)
        if preview_count:
            print(f"\n[INFO] First {min(preview_count, len(names))} archive entries:")
            for name in names[:preview_count]:
                print(f"  - {name}")
        return 1

    print(
        f"[OK] Bundle verification passed for {bundle_path} "
        f"({len(REQUIRED_PATHS)} required entries present)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
