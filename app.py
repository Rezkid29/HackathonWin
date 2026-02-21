"""
app.py
======
YOLOVision – Real-Time Object Detection Web App
------------------------------------------------
A production-ready Streamlit application that exposes two detection modes:

  1. Image Upload  – Upload a JPG/PNG, run YOLO inference, view side-by-side
                     comparison (original vs. annotated), and browse detections.
  2. Live Webcam   – Stream webcam frames through YOLO in real-time with
                     start / stop controls and live detection list.

Architecture
------------
  app.py                 ← Streamlit UI (this file)
  utils/model.py         ← Cached YOLO model loader
  utils/detection.py     ← Inference pipeline + bounding-box renderer

Usage
-----
  streamlit run app.py
"""

from __future__ import annotations

import io
import time
from typing import List

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from utils.detection import Detection, bgr_to_pil, run_inference
from utils.model import load_model

# ---------------------------------------------------------------------------
# Page configuration – must be the very first Streamlit call.
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="YOLOVision – Object Detection",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS – dark, premium feel
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ── Base ──────────────────────────────────────────────── */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #1a1f2e 100%);
        border-right: 1px solid #30363d;
    }
    /* ── Header ─────────────────────────────────────────────── */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff, #79c0ff, #a5d6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        text-align: center;
        color: #8b949e;
        font-size: 1rem;
        margin-bottom: 1.8rem;
    }
    /* ── Detection result cards ─────────────────────────────── */
    .det-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        margin-bottom: 0.45rem;
        transition: border-color 0.2s;
    }
    .det-card:hover { border-color: #58a6ff; }
    .det-label { font-weight: 600; color: #e6edf3; font-size: 0.95rem; }
    .det-conf  { font-size: 0.85rem; color: #3fb950; font-weight: 700; }
    /* ── Status badge ───────────────────────────────────────── */
    .badge-on  { color: #3fb950; font-weight: 700; }
    .badge-off { color: #f85149; font-weight: 700; }
    /* ── Column image captions ──────────────────────────────── */
    .img-caption {
        text-align: center;
        color: #8b949e;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Hero header
# ---------------------------------------------------------------------------

st.markdown('<h1 class="hero-title">🎯 YOLOVision</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Real-Time Object Detection · Powered by Ultralytics YOLO</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar – shared controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚙️ Detection Settings")
    st.markdown("---")

    # Confidence threshold – shared across both tabs.
    confidence = st.slider(
        "Confidence Threshold",
        min_value=0.1,
        max_value=1.0,
        value=0.45,
        step=0.05,
        help=(
            "Only detections with a confidence score above this value are shown. "
            "Lower values reveal more (possibly noisier) detections; "
            "higher values show only the model's most certain predictions."
        ),
    )

    st.markdown("---")
    st.markdown("### 📦 Model")
    model_choice = st.selectbox(
        "YOLO Variant",
        options=["yolo11n.pt", "yolo11s.pt", "yolo11m.pt", "yolo11l.pt"],
        index=0,
        help="Larger models trade speed for accuracy. 'n' = nano (fastest).",
    )

    st.markdown("---")
    st.markdown(
        "<small>Ultralytics YOLO11 · COCO 80-class · "
        "[Docs](https://docs.ultralytics.com)</small>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Load model (cached – runs once per session)
# ---------------------------------------------------------------------------

model = load_model(model_choice)

# ---------------------------------------------------------------------------
# Helper: render detection list
# ---------------------------------------------------------------------------

def render_detection_list(detections: List[Detection], threshold: float) -> None:
    """
    Display a formatted list of detected objects below an inference result.

    Each row shows:
      • Object class name
      • Confidence score (as a percentage)

    Only detections above *threshold* are shown (the model already filters
    during inference, but we re-apply here in case the slider is moved after
    results are cached).

    Args:
        detections: List of Detection objects from run_inference().
        threshold:  Current sidebar confidence value.
    """
    visible = [d for d in detections if d.confidence >= threshold]

    if not visible:
        st.info("No objects detected above the current confidence threshold.")
        return

    st.markdown(f"### 📋 Detected Objects &nbsp; `{len(visible)} found`")

    for det in visible:
        pct = f"{det.confidence:.1%}"
        st.markdown(
            f"""
            <div class="det-card">
                <span class="det-label">🏷️ {det.class_name}</span>
                <span class="det-conf">{pct}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_image, tab_webcam = st.tabs(["🖼️  Image Upload", "📷  Live Webcam"])


# ══════════════════════════════════════════════════════════════════════════
# TAB 1 – Image Upload
# ══════════════════════════════════════════════════════════════════════════

with tab_image:
    st.markdown("### Upload an Image")
    st.markdown(
        "Upload a **JPG or PNG** file and the YOLO model will detect all objects "
        "above the configured confidence threshold."
    )

    # ── File uploader ──────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        label="Drop or browse an image here",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
        help="Supported formats: JPEG, PNG. Maximum upload size set by Streamlit config.",
    )

    if uploaded_file is not None:
        # ── Validate upload ────────────────────────────────────────────────
        # Guard against corrupted or non-image files that have valid extensions.
        try:
            raw_bytes = uploaded_file.read()
            if len(raw_bytes) == 0:
                st.error("⚠️ The uploaded file appears to be empty. Please try again.")
                st.stop()

            pil_image = Image.open(io.BytesIO(raw_bytes))
            # Force full decode so we catch truncated files early.
            pil_image.verify()
            # Re-open after verify() because verify() closes the internal stream.
            pil_image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")

        except Exception as exc:  # noqa: BLE001
            st.error(
                f"⚠️ Could not open the uploaded file as an image.\n\n"
                f"**Error:** `{exc}`\n\n"
                "Please upload a valid JPG or PNG image."
            )
            st.stop()

        # ── Run inference ──────────────────────────────────────────────────
        with st.spinner("Running YOLO inference…"):
            try:
                annotated_bgr, detections = run_inference(
                    model=model,
                    image=pil_image,
                    confidence=confidence,
                )
                annotated_pil = bgr_to_pil(annotated_bgr)
            except Exception as exc:  # noqa: BLE001
                st.error(f"⚠️ Inference failed: `{exc}`")
                st.stop()

        # ── Side-by-side display ───────────────────────────────────────────
        col_orig, col_det = st.columns(2, gap="medium")

        with col_orig:
            st.image(pil_image, use_container_width=True)
            st.markdown(
                '<p class="img-caption">Original Image</p>',
                unsafe_allow_html=True,
            )

        with col_det:
            st.image(annotated_pil, use_container_width=True)
            st.markdown(
                '<p class="img-caption">Detections</p>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # ── Detection list ─────────────────────────────────────────────────
        render_detection_list(detections, confidence)

    else:
        # Placeholder when nothing is uploaded yet.
        st.markdown(
            """
            <div style="
                border: 2px dashed #30363d;
                border-radius: 14px;
                padding: 3rem;
                text-align: center;
                color: #8b949e;
                margin-top:1rem;
            ">
                <div style="font-size:3rem">🖼️</div>
                <div style="font-size:1.1rem; margin-top:0.8rem;">
                    Upload an image above to get started
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════
# TAB 2 – Live Webcam
# ══════════════════════════════════════════════════════════════════════════

with tab_webcam:
    st.markdown("### Real-Time Webcam Detection")
    st.markdown(
        "Your browser will ask for **camera permission** when detection starts. "
        "Click **▶ Start Detection** to begin streaming frames through YOLO."
    )

    # ── Session state for webcam lifecycle ─────────────────────────────────
    # Streamlit re-runs the entire script on every interaction, so we persist
    # the running flag in st.session_state across re-runs.
    if "webcam_running" not in st.session_state:
        st.session_state.webcam_running = False
    if "last_detections" not in st.session_state:
        st.session_state.last_detections = []

    # ── Start / Stop controls ──────────────────────────────────────────────
    btn_col1, btn_col2, _ = st.columns([1, 1, 4])
    with btn_col1:
        start_btn = st.button(
            "▶ Start Detection",
            disabled=st.session_state.webcam_running,
            use_container_width=True,
            type="primary",
        )
    with btn_col2:
        stop_btn = st.button(
            "⏹ Stop",
            disabled=not st.session_state.webcam_running,
            use_container_width=True,
        )

    if start_btn:
        st.session_state.webcam_running = True
        st.rerun()

    if stop_btn:
        st.session_state.webcam_running = False
        st.rerun()

    # ── Status indicator ───────────────────────────────────────────────────
    if st.session_state.webcam_running:
        st.markdown(
            '<p class="badge-on">● Detection Active</p>', unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<p class="badge-off">● Detection Stopped</p>', unsafe_allow_html=True
        )

    # ── Live feed placeholder ──────────────────────────────────────────────
    frame_placeholder = st.empty()

    # ── Webcam inference loop ──────────────────────────────────────────────
    if st.session_state.webcam_running:
        # Attempt to open the default webcam (device index 0).
        # cv2.VideoCapture gracefully returns an object even if no camera is
        # present; we validate with .isOpened() before reading frames.
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            # ── Graceful permission / hardware error ───────────────────────
            st.error(
                "⚠️ **Webcam not accessible.**\n\n"
                "Possible causes:\n"
                "- Camera permission has not been granted to the browser or terminal.\n"
                "- Another application is using the camera.\n"
                "- No camera hardware was detected.\n\n"
                "**Fix:** Grant camera access in your OS System Settings → Privacy & Security → Camera, "
                "then click **▶ Start Detection** again."
            )
            st.session_state.webcam_running = False
            cap.release()
            st.stop()

        # Optionally reduce resolution for speed.
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        try:
            # Stream until the user clicks Stop (session state changes re-run).
            while st.session_state.webcam_running:
                ret, frame_bgr = cap.read()
                if not ret:
                    st.warning("⚠️ Failed to read a frame from the webcam. Retrying…")
                    time.sleep(0.1)
                    continue

                # ── Inference on the raw BGR frame ─────────────────────────
                # The CV pipeline (resize → forward-pass → NMS → draw) is the
                # same as the image-upload path; only the input type differs.
                annotated_bgr, detections = run_inference(
                    model=model,
                    image=frame_bgr,
                    confidence=confidence,
                )
                st.session_state.last_detections = detections

                # ── Render the annotated frame in the placeholder ───────────
                # Convert BGR → RGB for Streamlit (which expects RGB).
                annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(
                    annotated_rgb,
                    channels="RGB",
                    use_container_width=True,
                    caption="Live Feed with YOLO Detections",
                )

                # Brief sleep to throttle CPU usage; YOLO inference latency
                # already limits effective FPS on most hardware.
                time.sleep(0.03)

        finally:
            # Always release the camera handle, even on exception or Stop press.
            cap.release()

    # ── Detections from the last processed frame ───────────────────────────
    if st.session_state.last_detections:
        st.markdown("---")
        render_detection_list(st.session_state.last_detections, confidence)
    elif not st.session_state.webcam_running:
        if not st.session_state.last_detections:
            st.markdown(
                """
                <div style="
                    border: 2px dashed #30363d;
                    border-radius: 14px;
                    padding: 3rem;
                    text-align: center;
                    color: #8b949e;
                    margin-top:1rem;
                ">
                    <div style="font-size:3rem">📷</div>
                    <div style="font-size:1.1rem; margin-top:0.8rem;">
                        Press <strong>▶ Start Detection</strong> to activate your webcam
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
