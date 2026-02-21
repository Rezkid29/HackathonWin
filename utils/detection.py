"""
utils/detection.py
------------------
Computer-vision helpers for:
  1. Running YOLO inference on a single image (PIL or numpy array).
  2. Drawing bounding boxes + labels on the result frame.
  3. Parsing the raw YOLO result into a tidy list of detections.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from ultralytics.engine.results import Results


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Detection:
    """A single detected object with its label, confidence, and bounding box."""
    class_id: int
    class_name: str
    confidence: float
    # Bounding box in pixel coordinates: (x_min, y_min, x_max, y_max)
    bbox: Tuple[int, int, int, int]


# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

# Pre-generate one BGR colour per COCO class index so boxes are consistent.
_RNG = np.random.default_rng(seed=42)
_PALETTE: List[Tuple[int, int, int]] = [
    tuple(int(c) for c in _RNG.integers(80, 230, 3)) for _ in range(80)
]


def _get_color(class_id: int) -> Tuple[int, int, int]:
    """Return a stable BGR colour for the given class index."""
    return _PALETTE[class_id % len(_PALETTE)]


# ---------------------------------------------------------------------------
# Core inference helper
# ---------------------------------------------------------------------------

def run_inference(
    model: YOLO,
    image: Image.Image | np.ndarray,
    confidence: float = 0.5,
) -> Tuple[np.ndarray, List[Detection]]:
    """
    Run YOLO inference on *image* and return an annotated frame together
    with a list of structured Detection objects.

    Computer-vision pipeline
    ────────────────────────
    1. Normalise the input to a BGR numpy array (OpenCV native format).
    2. Call model.predict() with the supplied confidence threshold.
       YOLO internally:
         a. Resizes the image to the model's input stride (e.g. 640×640).
         b. Runs convolutional forward pass.
         c. Applies Non-Maximum Suppression (NMS) to filter overlapping boxes.
    3. Iterate over the returned bounding boxes; for each detection collect
       the class label, confidence score, and pixel-space coordinates.
    4. Draw each bounding box with its label onto a copy of the original
       frame so the original is never mutated.

    Args:
        model:      Loaded Ultralytics YOLO instance.
        image:      Input image as PIL Image or numpy array (RGB or BGR).
        confidence: Minimum confidence threshold in [0.0, 1.0].

    Returns:
        annotated_frame: BGR numpy array with bounding boxes drawn.
        detections:      List of Detection dataclasses, sorted by descending
                         confidence for easy downstream display.
    """
    # ── Step 1: normalise to BGR numpy array ───────────────────────────────
    if isinstance(image, Image.Image):
        # PIL stores images as RGB; OpenCV expects BGR.
        frame_rgb = np.array(image.convert("RGB"))
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    else:
        # Assume caller provides BGR numpy array (webcam path).
        frame_bgr = image.copy()

    # ── Step 2: YOLO forward pass ──────────────────────────────────────────
    # verbose=False silences per-frame console logs in production.
    results: List[Results] = model.predict(
        source=frame_bgr,
        conf=confidence,
        verbose=False,
    )

    # ── Step 3 & 4: parse results and draw annotations ─────────────────────
    annotated_frame = frame_bgr.copy()
    detections: List[Detection] = []

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            # Extract scalar values from the YOLO tensor wrappers.
            cls_id = int(box.cls.item())
            conf   = float(box.conf.item())
            x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())

            # Resolve class name from the model's category map.
            class_name = result.names.get(cls_id, str(cls_id))

            detections.append(Detection(
                class_id=cls_id,
                class_name=class_name,
                confidence=conf,
                bbox=(x1, y1, x2, y2),
            ))

            # Draw bounding box rectangle.
            color = _get_color(cls_id)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness=2)

            # Draw label pill (filled rectangle + text).
            label = f"{class_name}  {conf:.0%}"
            (text_w, text_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1
            )
            # Background pill sits above the top-left corner of the box.
            pill_y1 = max(0, y1 - text_h - baseline - 6)
            pill_y2 = y1
            pill_x2 = x1 + text_w + 6
            cv2.rectangle(
                annotated_frame, (x1, pill_y1), (pill_x2, pill_y2), color, -1
            )
            cv2.putText(
                annotated_frame,
                label,
                (x1 + 3, pill_y2 - baseline - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                thickness=1,
                lineType=cv2.LINE_AA,
            )

    # Sort by confidence descending so the table is easy to read.
    detections.sort(key=lambda d: d.confidence, reverse=True)
    return annotated_frame, detections


# ---------------------------------------------------------------------------
# Format helpers
# ---------------------------------------------------------------------------

def bgr_to_pil(frame_bgr: np.ndarray) -> Image.Image:
    """Convert an OpenCV BGR frame to a PIL RGB Image for Streamlit display."""
    return Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
