from __future__ import annotations
import os, zipfile, glob

def build_llm_bundle(zip_path: str, include_globs: list[str], exclude_globs: list[str] | None = None, max_files: int = 50):
    exclude = set()
    if exclude_globs:
        for g in exclude_globs:
            for p in glob.glob(g, recursive=True):
                exclude.add(os.path.normpath(p))

    files = []
    for g in include_globs:
        for p in glob.glob(g, recursive=True):
            p_norm = os.path.normpath(p)
            if os.path.isdir(p_norm): 
                continue
            if p_norm in exclude:
                continue
            files.append(p_norm)

    files = sorted(set(files))[:max_files]
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in files:
            arc = f.replace(os.path.sep, "/")
            z.write(f, arcname=arc)
    return files
