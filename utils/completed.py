"""
utils/completed.py
------------------
Pseudo-database for completed STEM projects.

Storage: data/completed_projects.json  (a plain JSON array)

Upgrade path
------------
Only three public functions exist. Swap the JSON read/write for SQLite,
Supabase, or any other backend and the rest of the app is unchanged.

PUBLIC API
----------
  save_completed_project(project: dict) -> None
  load_completed_projects() -> list[dict]
  is_project_completed(title: str) -> bool
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_FILE     = os.path.join(_DATA_DIR, "completed_projects.json")


def _load_raw() -> list[dict[str, Any]]:
    """Load the raw list from disk, returning [] on any error."""
    os.makedirs(_DATA_DIR, exist_ok=True)
    if not os.path.exists(_FILE):
        return []
    try:
        with open(_FILE) as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_raw(records: list[dict[str, Any]]) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_FILE, "w") as f:
        json.dump(records, f, indent=2)


# ── Public API ────────────────────────────────────────────────────────────────

def save_completed_project(project: dict[str, Any]) -> None:
    """
    Append a project to the completed list.
    Duplicate titles are ignored (idempotent).
    """
    records = _load_raw()
    existing_titles = {r["title"] for r in records}
    if project.get("title") in existing_titles:
        return

    record: dict[str, Any] = {
        "title":            project.get("title", "Unknown"),
        "emoji":            project.get("emoji", "🛠️"),
        "stem_tag":         project.get("stem_tag", ""),
        "difficulty":       project.get("difficulty", ""),
        "time_est":         project.get("time_est", ""),
        "tagline":          project.get("tagline", ""),
        "completed_at":     datetime.now().isoformat(timespec="seconds"),
        "objects_detected": project.get("_objects_detected", []),
    }
    records.append(record)
    _save_raw(records)


def load_completed_projects() -> list[dict[str, Any]]:
    """Return all completed projects, newest first."""
    records = _load_raw()
    return list(reversed(records))


def is_project_completed(title: str) -> bool:
    """Return True if a project with this title has already been saved."""
    return any(r["title"] == title for r in _load_raw())
