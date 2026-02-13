from __future__ import annotations

import glob
import os
import zipfile
from pathlib import Path
from typing import Iterable

_FIXED_ZIP_DATETIME = (1980, 1, 1, 0, 0, 0)
_FORBIDDEN_ENTRY_PARTS = {"...", "…", ""}


def _normalize_file_path(path: str) -> str:
    normalized = os.path.normpath(path)
    return normalized.lstrip("./") if normalized.startswith(f".{os.path.sep}") else normalized


def _is_forbidden_arcname(arcname: str) -> str | None:
    if not arcname:
        return "empty entry name"
    if arcname.startswith("/"):
        return "absolute path is not allowed"
    if "\\" in arcname:
        return "backslashes are not allowed in archive paths"

    parts = arcname.split("/")
    for part in parts:
        if part in _FORBIDDEN_ENTRY_PARTS:
            return f"placeholder path segment: {part!r}"
        if part in {".", ".."}:
            return f"relative traversal segment: {part!r}"
    return None


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


def _build_zip_info(archive_name: str, source_path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(filename=archive_name, date_time=_FIXED_ZIP_DATETIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    source_mode = os.stat(source_path).st_mode
    normalized_mode = 0o755 if (source_mode & 0o111) else 0o644
    info.external_attr = normalized_mode << 16
    info.create_system = 3
    return info


def _validate_entries(entries: Iterable[str]) -> None:
    invalid: list[str] = []
    for entry in entries:
        reason = _is_forbidden_arcname(entry)
        if reason:
            invalid.append(f"{entry!r} ({reason})")
    if invalid:
        raise ValueError("Forbidden bundle entries detected: " + ", ".join(invalid))


def build_llm_bundle(
    zip_path: str,
    include_globs: list[str],
    exclude_globs: list[str] | None = None,
) -> list[str]:
    files = _expand_globs(include_globs=include_globs, exclude_globs=exclude_globs)
    archive_names = [_normalize_file_path(file_path).replace(os.path.sep, "/") for file_path in files]
    _validate_entries(archive_names)

    Path(zip_path).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for file_path, archive_name in sorted(zip(files, archive_names), key=lambda item: item[1]):
            info = _build_zip_info(archive_name=archive_name, source_path=file_path)
            archive.writestr(info, Path(file_path).read_bytes())
    return files
