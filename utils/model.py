"""
utils/model.py
--------------
Handles YOLO model loading with Streamlit caching so the model is only
loaded once per session, avoiding expensive re-initialization on every
Streamlit re-run.
"""

import streamlit as st
from ultralytics import YOLO


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading YOLO26 model – this takes a moment…")
def load_model(model_name: str = "yolo11n.pt") -> YOLO:
    """
    Load and cache the Ultralytics YOLO model.

    The @st.cache_resource decorator ensures that the model weights are
    downloaded and loaded only once per Streamlit server session, even
    if the page re-runs (e.g. the user adjusts the confidence slider).

    Args:
        model_name: Ultralytics model identifier.  The library resolves
                    this to the correct weights file automatically.
                    We use 'yolo11n.pt' (YOLO v11 nano) as a fast default;
                    swap with 'yolo11s.pt', 'yolo11m.pt', etc. for accuracy.

    Returns:
        A loaded YOLO model instance ready for inference.
    """
    model = YOLO(model_name)
    return model
