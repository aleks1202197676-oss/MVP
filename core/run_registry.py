from __future__ import annotations

import datetime as dt
import os


def new_run_id(fmt: str = "%Y%m%d_%H%M%S") -> str:
    return dt.datetime.now().strftime(fmt)


def ensure_run_folders(output_root: str, run_id: str) -> dict[str, str]:
    latest = os.path.join(output_root, "latest")
    history = os.path.join(output_root, "history", run_id)
    os.makedirs(latest, exist_ok=True)
    os.makedirs(history, exist_ok=True)
    return {"latest": latest, "history": history}
