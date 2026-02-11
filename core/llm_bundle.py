from __future__ import annotations

import glob
import os
import zipfile


def build_llm_bundle(
    zip_path: str,
    include_globs: list[str],
    exclude_globs: list[str] | None = None,
    max_files: int = 50,
) -> list[str]:
    exclude = set()
    if exclude_globs:
        for pattern in exclude_globs:
            for path in glob.glob(pattern, recursive=True):
                exclude.add(os.path.normpath(path))

    files: list[str] = []
    for pattern in include_globs:
        for path in glob.glob(pattern, recursive=True):
            path_norm = os.path.normpath(path)
            if os.path.isdir(path_norm):
                continue
            if path_norm in exclude:
                continue
            if not os.path.isfile(path_norm):
                continue
            files.append(path_norm)

    files = sorted(set(files))[:max_files]
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            arcname = file_path.replace(os.path.sep, "/")
            archive.write(file_path, arcname=arcname)

    return files
