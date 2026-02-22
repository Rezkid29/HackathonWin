"""
utils/progress.py
-----------------
Persistent player progress: streak counter, trophies, and best time.
Stored in data/progress.json relative to the project root.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from typing import Any

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_FILE = os.path.join(_DATA_DIR, "progress.json")

_DEFAULTS: dict[str, Any] = {
    "streak": 0,
    "last_session_date": None,
    "trophies": [],
    "best_time": None,
    "total_quests_completed": 0,
}

# (threshold, trophy_label)
_STREAK_TROPHIES = [
    (3,  "Hot Streak 🔥"),
    (7,  "On Fire! 🔥🔥"),
    (30, "Legendary Streak 🌟"),
]
_QUEST_TROPHIES = [
    (1,  "First Quest! 🏆"),
    (5,  "Quest Master 🎯"),
    (10, "Explorer Elite 🌟"),
]


def load_progress() -> dict[str, Any]:
    os.makedirs(_DATA_DIR, exist_ok=True)
    if not os.path.exists(_FILE):
        return _DEFAULTS.copy()
    try:
        with open(_FILE) as f:
            data = json.load(f)
        for k, v in _DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return _DEFAULTS.copy()


def save_progress(data: dict[str, Any]) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_FILE, "w") as f:
        json.dump(data, f, indent=2)


def on_quest_completed(
    data: dict[str, Any],
    completion_time: float,
) -> tuple[dict[str, Any], list[str]]:
    """
    Call when the player completes a quest.

    Updates streak, best time, and unlocks trophies.
    Returns (updated_data, list_of_newly_unlocked_trophy_labels).
    """
    new_trophies: list[str] = []
    today_str = str(date.today())
    last_str = data.get("last_session_date")

    # Streak logic
    if last_str is None:
        data["streak"] = 1
    elif last_str == today_str:
        pass  # Same day – don't double-increment
    else:
        last_date = datetime.strptime(last_str, "%Y-%m-%d").date()
        gap = date.today() - last_date
        data["streak"] = (data.get("streak", 0) + 1) if gap == timedelta(days=1) else 1

    data["last_session_date"] = today_str
    data["total_quests_completed"] = data.get("total_quests_completed", 0) + 1

    # Best time
    best = data.get("best_time")
    if best is None or completion_time < best:
        data["best_time"] = completion_time
        if best is not None:
            _unlock(data, new_trophies, "New Record! ⚡")

    # Speed run (under 60 s)
    if completion_time <= 60:
        _unlock(data, new_trophies, "Speed Run Star ⭐")

    # Streak milestones
    for threshold, trophy in _STREAK_TROPHIES:
        if data["streak"] >= threshold:
            _unlock(data, new_trophies, trophy)

    # Quest count milestones
    for threshold, trophy in _QUEST_TROPHIES:
        if data["total_quests_completed"] >= threshold:
            _unlock(data, new_trophies, trophy)

    return data, new_trophies


def _unlock(data: dict[str, Any], new_list: list[str], trophy: str) -> None:
    if trophy not in data["trophies"]:
        data["trophies"].append(trophy)
        new_list.append(trophy)
