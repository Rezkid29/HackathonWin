"""
utils/quest.py
--------------
Quest generation and detection checking for the Scavenger Hunt game mode.
"""

from __future__ import annotations

import random
from typing import List, Set

COCO_EMOJIS: dict[str, str] = {
    "person": "🧑",
    "bicycle": "🚲",
    "car": "🚗",
    "motorcycle": "🏍️",
    "airplane": "✈️",
    "bus": "🚌",
    "train": "🚂",
    "truck": "🚛",
    "boat": "⛵",
    "traffic light": "🚦",
    "fire hydrant": "🚒",
    "stop sign": "🛑",
    "parking meter": "🅿️",
    "bench": "🪑",
    "bird": "🐦",
    "cat": "🐱",
    "dog": "🐕",
    "horse": "🐴",
    "sheep": "🐑",
    "cow": "🐄",
    "elephant": "🐘",
    "bear": "🐻",
    "zebra": "🦓",
    "giraffe": "🦒",
    "backpack": "🎒",
    "umbrella": "☂️",
    "handbag": "👜",
    "tie": "👔",
    "suitcase": "🧳",
    "frisbee": "🥏",
    "skis": "⛷️",
    "snowboard": "🏂",
    "sports ball": "⚽",
    "kite": "🪁",
    "baseball bat": "🏏",
    "baseball glove": "🧤",
    "skateboard": "🛹",
    "surfboard": "🏄",
    "tennis racket": "🎾",
    "bottle": "🍶",
    "wine glass": "🍷",
    "cup": "☕",
    "fork": "🍴",
    "knife": "🔪",
    "spoon": "🥄",
    "bowl": "🥣",
    "banana": "🍌",
    "apple": "🍎",
    "sandwich": "🥪",
    "orange": "🍊",
    "broccoli": "🥦",
    "carrot": "🥕",
    "hot dog": "🌭",
    "pizza": "🍕",
    "donut": "🍩",
    "cake": "🎂",
    "chair": "🪑",
    "couch": "🛋️",
    "potted plant": "🪴",
    "bed": "🛏️",
    "dining table": "🍽️",
    "toilet": "🚽",
    "tv": "📺",
    "laptop": "💻",
    "mouse": "🖱️",
    "remote": "📡",
    "keyboard": "⌨️",
    "cell phone": "📱",
    "microwave": "📦",
    "oven": "🔥",
    "toaster": "🍞",
    "sink": "🚰",
    "refrigerator": "🧊",
    "book": "📚",
    "clock": "🕐",
    "vase": "🏺",
    "scissors": "✂️",
    "teddy bear": "🧸",
    "hair drier": "💨",
    "toothbrush": "🪥",
}

# Items biased toward things findable indoors / at school
PREFERRED_CLASSES: list[str] = [
    "person", "cat", "dog", "cup", "bottle", "book", "chair",
    "laptop", "cell phone", "keyboard", "mouse", "remote", "clock",
    "backpack", "teddy bear", "scissors", "toothbrush", "apple",
    "banana", "orange", "couch", "potted plant", "bowl", "spoon",
    "fork", "vase", "bed", "tv", "sink", "refrigerator", "umbrella",
    "cake", "pizza", "donut", "sandwich", "carrot",
]


def get_emoji(class_name: str) -> str:
    return COCO_EMOJIS.get(class_name, "❓")


def generate_quest(n: int = 5) -> List[str]:
    pool = list(PREFERRED_CLASSES)
    random.shuffle(pool)
    return pool[:n]


def check_detections(
    detected_names: List[str],
    quest_items: List[str],
    quest_found: Set[str],
) -> List[str]:
    """Return quest items newly detected that weren't already found."""
    return [
        name for name in detected_names
        if name in quest_items and name not in quest_found
    ]
