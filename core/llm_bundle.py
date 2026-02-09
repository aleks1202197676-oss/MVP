from __future__ import annotations

import glob
import os
import zipfile
from pathlib import Path


def _expand_globs(include_globs: list[str], exclude_globs: list[str] | None = None) -> list[str]:
    excluded: set[str] = set()
    for pattern in sorted(exclude_globs or []):
        for matched in glob.glob(pattern, recursive=True):
            normalized = os.path.normpath(matched)
            if os.path.isfile(normalized):
                excluded.add(normalized)

    files: set[str] = set()
    for pattern in sorted(include_globs):
        for matched in glob.glob(pattern, recursive=True):
            normalized = os.path.normpath(matched)
            if not os.path.isfile(normalized):
                continue
            if normalized in excluded:
                continue
            files.add(normalized)

    return sorted(files)


def build_llm_bundle(
    zip_path: str,
    include_globs: list[str],
    exclude_globs: list[str] | None = None,
) -> list[str]:
    files = _expand_globs(include_globs=include_globs, exclude_globs=exclude_globs)

    Path(zip_path).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            archive.write(file_path, arcname=file_path.replace(os.path.sep, "/"))
    return files
