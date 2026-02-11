from __future__ import annotations

import glob
import os
import zipfile
from typing import Iterable


def _expand_globs(patterns: Iterable[str]) -> set[str]:
    expanded: set[str] = set()
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            path_norm = os.path.normpath(path)
            if os.path.isdir(path_norm):
                continue
            expanded.add(path_norm)
    return expanded


def build_llm_bundle(
    zip_path: str,
    include_globs: list[str],
    exclude_globs: list[str] | None = None,
    max_files: int = 500,
) -> list[str]:
    exclude = _expand_globs(exclude_globs or [])
    files = sorted(_expand_globs(include_globs) - exclude)[:max_files]

    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for file_path in files:
            bundle.write(file_path, arcname=file_path.replace(os.path.sep, "/"))

    return files
