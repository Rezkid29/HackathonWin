"""
app.py
======
YOLOVision – Scavenger Hunt Edition
------------------------------------
A kid-friendly (ages 9-13) gamified object-detection app built on Streamlit
and Ultralytics YOLO26.

Game loop
---------
  1. Five household objects are randomly selected as the session quest.
  2. The player uploads photos or uses the live webcam to find them.
  3. Each detection triggers a tile flip on the Quest Board + tick sound.
  4. Finding all 5 fires confetti, a fanfare, and saves progress.
  5. Trophies and streaks are persisted across sessions in data/progress.json.

Architecture
------------
  app.py              ← Streamlit UI + game logic (this file)
  utils/model.py      ← Cached YOLO model loader
  utils/detection.py  ← Inference pipeline + bounding-box renderer
  utils/quest.py      ← Quest generation, COCO emojis, detection checker
  utils/progress.py   ← Streak / trophy persistence
  utils/projects.py   ← Project Ideas Engine (DIY suggestions from detections)
"""

from __future__ import annotations

import io
import time
from typing import List, Set

import cv2
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageFont

from utils.detection import Detection, bgr_to_pil, run_inference
from utils.model import load_model
from utils.progress import load_progress, on_quest_completed, save_progress
from utils.quest import check_detections, generate_quest, get_emoji
from utils.projects import get_project_suggestions

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Scavenger Hunt – YOLOVision",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;700;900&display=swap');

    /* ── Base / chassis ──────────────────────────────────── */
    :root {
        --bg-main: #2b313f;
        --bg-shell: #11141c;
        --bg-panel: #171d2b;
        --bg-panel-2: #101521;
        --text-main: #e5e7eb;
        --text-muted: #8b96a9;
        --line: #2c3447;
        --line-soft: #222a3b;
        --accent: #ff6a00;
        --accent-soft: #ff8f3d;
        --accent-glow: rgba(255, 106, 0, 0.35);
        --good: #22c55e;
        --med: #f59e0b;
        --hard: #ef4444;
        --combo: #a855f7;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 20% -10%, #3c4457 0%, var(--bg-main) 46%, #222836 100%) !important;
        font-family: 'Nunito', sans-serif;
        color: var(--text-main);
    }
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 16px;
        border-radius: 22px;
        border: 1px solid #3a4358;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02), 0 14px 40px rgba(0,0,0,0.45);
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0));
        pointer-events: none;
        z-index: 0;
    }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    footer { visibility: hidden; }
    section.main > div {
        max-width: 1180px;
        padding-top: 22px;
        padding-bottom: 84px;
    }
    div[data-testid="stVerticalBlock"] > div:has(> .game-header),
    div[data-testid="stVerticalBlock"] > div:has(> .quest-board),
    div[data-testid="stVerticalBlock"] > div:has(> .completion-panel),
    div[data-testid="stVerticalBlock"] > div:has(> .trophy-shell) {
        position: relative;
        z-index: 1;
    }
    hr {
        border-color: var(--line) !important;
    }

    /* ── Top HUD shell ───────────────────────────────────── */
    .game-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        background: linear-gradient(155deg, #0f131d 0%, #171c29 65%, #10141f 100%);
        border: 1px solid #2d3548;
        border-radius: 18px;
        padding: 14px 18px;
        margin-bottom: 14px;
        gap: 10px;
        flex-wrap: wrap;
        box-shadow: 0 8px 28px rgba(0,0,0,0.42), inset 0 0 0 1px rgba(255,255,255,0.03);
    }
    .hud-left {
        display: flex;
        flex-direction: column;
        gap: 8px;
        min-width: 0;
    }
    .game-title {
        font-family: 'Nunito', sans-serif;
        font-size: 1.8rem;
        line-height: 1.05;
        letter-spacing: 1.2px;
        font-weight: 900;
        color: #f3f4f6;
        text-transform: uppercase;
        white-space: nowrap;
        text-shadow: 0 0 16px rgba(255,255,255,0.06);
    }
    .hud-nav {
        display: flex;
        align-items: center;
        gap: 16px;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.7px;
        text-transform: uppercase;
    }
    .hud-nav-item {
        color: #7f8aa0;
        padding: 4px 0;
        border-bottom: 2px solid transparent;
    }
    .hud-nav-item.active {
        color: #e5e7eb;
        border-bottom-color: var(--accent);
        text-shadow: 0 0 12px var(--accent-glow);
    }
    .hud-badges {
        display: flex;
        gap: 10px;
        align-items: center;
        flex-wrap: wrap;
        justify-content: flex-end;
    }
    .hud-badge {
        background: linear-gradient(145deg, #141a28, #101522);
        border: 1px solid #2a3244;
        border-radius: 12px;
        padding: 8px 14px;
        font-size: 0.95rem;
        font-weight: 900;
        color: var(--text-main);
        white-space: nowrap;
        min-height: 48px;
        display: flex;
        align-items: center;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
    }
    .hud-badge.streak { border-color: rgba(255,106,0,0.45); color: #ff9a52; }
    .hud-badge.score  { border-color: #4b556b; color: #d1d5db; }
    .hud-badge.timer  { border-color: rgba(56,189,248,0.35); color: #9fdcff; }

    /* ── Quest board panel ───────────────────────────────── */
    .quest-board {
        background: linear-gradient(155deg, #111621 0%, #171d2b 55%, #0f131e 100%);
        border: 1px solid #2d3548;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
        animation: boardIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
        box-shadow: 0 10px 26px rgba(0,0,0,0.45), inset 0 0 0 1px rgba(255,255,255,0.02);
    }
    @keyframes boardIn {
        from { transform: translateY(-30px) scale(0.95); opacity: 0; }
        to   { transform: translateY(0)     scale(1);    opacity: 1; }
    }
    .quest-board-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        gap: 10px;
        flex-wrap: wrap;
    }
    .quest-board-title {
        font-family: 'Nunito', sans-serif;
        font-size: 1.12rem;
        color: #f3f4f6;
        letter-spacing: 1.1px;
        text-transform: uppercase;
        font-weight: 900;
    }
    .quest-progress-pill {
        background: linear-gradient(145deg, #1a2233, #121928);
        border: 1px solid #2e394d;
        border-radius: 20px;
        padding: 6px 12px;
        font-weight: 900;
        font-size: 0.88rem;
        color: #f8fafc;
        box-shadow: inset 0 0 10px rgba(255,106,0,0.12);
    }

    /* ── Quest tiles grid ────────────────────────────────── */
    .quest-tiles {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
        gap: 12px;
        justify-items: center;
    }

    /* ── Tile flip card ──────────────────────────────────── */
    .quest-tile-wrapper {
        perspective: 900px;
        width: 100%;
        max-width: 140px;
        height: 145px;
    }
    .quest-tile-inner {
        width: 100%;
        height: 100%;
        position: relative;
        transform-style: preserve-3d;
        transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .quest-tile-wrapper.found .quest-tile-inner {
        transform: rotateY(180deg);
    }
    .quest-tile-front,
    .quest-tile-back {
        position: absolute;
        inset: 0;
        backface-visibility: hidden;
        -webkit-backface-visibility: hidden;
        border-radius: 14px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 5px;
        padding: 8px;
    }
    .quest-tile-front {
        background: linear-gradient(145deg, #191f2f, #121927);
        border: 1px solid #30384b;
        box-shadow: 0 6px 16px rgba(0,0,0,0.55), inset 0 0 0 1px rgba(255,255,255,0.02);
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .quest-tile-front:hover {
        transform: scale(1.04);
        border-color: rgba(255,106,0,0.58);
        box-shadow: 0 8px 26px var(--accent-glow), 0 0 0 1px rgba(255,106,0,0.18);
    }
    .quest-tile-back {
        background: linear-gradient(145deg, #1b2a1e, #10301b);
        border: 1px solid #2f7a49;
        box-shadow: 0 4px 20px rgba(34,197,94,0.25);
        transform: rotateY(180deg);
    }
    .tile-emoji      { font-size: 2.2rem; line-height: 1; }
    .tile-name       { font-size: 0.65rem; font-weight: 900; text-transform: uppercase;
                       letter-spacing: 0.5px; color: #94a3b8; text-align: center; }
    .tile-checkbox   { font-size: 1.1rem; color: #475569; }
    .tile-found-star { font-size: 2rem; line-height: 1; }
    .tile-found-label{ font-size: 0.7rem; font-weight: 900; color: #4ade80;
                       text-transform: uppercase; letter-spacing: 1.5px; }

    /* ── Progress bar ────────────────────────────────────── */
    .quest-progress-bar {
        height: 8px;
        background: #121827;
        border-radius: 4px;
        margin-top: 14px;
        overflow: hidden;
        border: 1px solid #222a3b;
    }
    .quest-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #ff6a00, #ff8f3d);
        border-radius: 4px;
        transition: width 0.6s ease;
        box-shadow: 0 0 12px rgba(255,106,0,0.45);
    }

    /* ── Completion panel ────────────────────────────────── */
    .completion-panel {
        background: linear-gradient(145deg, #161d2c, #111725);
        border: 1px solid #2f384b;
        border-radius: 20px;
        padding: 22px 20px;
        text-align: center;
        margin-bottom: 14px;
        animation: completionPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
        box-shadow: 0 10px 26px rgba(0,0,0,0.44), inset 0 0 0 1px rgba(255,255,255,0.02);
    }
    @keyframes completionPop {
        from { transform: scale(0.85); opacity: 0; }
        to   { transform: scale(1);    opacity: 1; }
    }
    .completion-title {
        font-family: 'Nunito', sans-serif;
        font-size: 2rem;
        color: #ffb27a;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 900;
        margin-bottom: 6px;
        text-shadow: 0 0 18px rgba(255,106,0,0.28);
    }
    .completion-stats {
        display: flex;
        justify-content: center;
        gap: 24px;
        flex-wrap: wrap;
        margin: 16px 0;
    }
    .stat-box {
        background: linear-gradient(145deg, #121a29, #0f1522);
        border: 1px solid #2c3548;
        border-radius: 12px;
        padding: 10px 18px;
        text-align: center;
    }
    .stat-value { font-size: 1.8rem; font-weight: 900; color: #ff8f3d; }
    .stat-label { font-size: 0.75rem; color: #a0aec0; text-transform: uppercase; letter-spacing: 1px; }
    .new-trophy-row {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 12px;
    }
    .new-trophy-tag {
        background: linear-gradient(145deg, #26160a, #1b1107);
        border: 1px solid #9a5b2c;
        border-radius: 10px;
        padding: 6px 14px;
        font-size: 0.9rem;
        font-weight: 900;
        color: #ffcc9d;
    }

    /* ── Trophy case ─────────────────────────────────────── */
    .trophy-shell {
        background: linear-gradient(145deg, #121826, #0f141f);
        border: 1px solid #2d3548;
        border-radius: 16px;
        padding: 14px 14px 8px;
        box-shadow: 0 10px 26px rgba(0,0,0,0.4), inset 0 0 0 1px rgba(255,255,255,0.02);
    }
    .trophy-section-title {
        font-family: 'Nunito', sans-serif;
        font-size: 1rem;
        color: #f3f4f6;
        letter-spacing: 1px;
        font-weight: 900;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .trophy-shelf {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 24px;
    }
    .trophy-card {
        background: linear-gradient(145deg, #28170c, #1b1109);
        border: 1px solid #8d5731;
        border-radius: 12px;
        padding: 10px 16px;
        font-size: 0.9rem;
        font-weight: 700;
        color: #ffd5aa;
        position: relative;
    }
    .trophy-card.locked {
        background: linear-gradient(145deg, #171e2e, #111724);
        border-color: #2b3448;
        color: #667085;
        cursor: help;
    }
    .trophy-card.locked:hover::after {
        content: attr(data-hint);
        position: absolute;
        bottom: calc(100% + 8px);
        left: 50%;
        transform: translateX(-50%);
        background: #1c2434;
        color: #cdd6e5;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 6px 10px;
        border-radius: 8px;
        white-space: nowrap;
        z-index: 100;
        pointer-events: none;
        border: 1px solid #35435c;
    }

    /* ── Detection result cards ──────────────────────────── */
    .det-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(145deg, #151c2a, #101622);
        border: 1px solid #2b3447;
        border-radius: 10px;
        padding: 8px 14px;
        margin-bottom: 6px;
        min-height: 48px;
    }
    .det-card.quest-hit { border-color: rgba(255,106,0,0.5); background: linear-gradient(145deg, #26170f, #17141b); }
    .det-label { font-weight: 700; color: #e2e8f0; font-size: 0.9rem; }
    .det-conf  { font-size: 0.82rem; color: #ff9a52; font-weight: 900; }
    .det-bonus { font-size: 0.75rem; color: #8da2c8; font-weight: 700; }

    /* ── Drag-zone upload ────────────────────────────────── */
    .drag-zone {
        border: 2px dashed #3b465f;
        border-radius: 18px;
        padding: 36px 24px;
        text-align: center;
        background: linear-gradient(145deg, #121926 0%, #0f1521 100%);
        margin-bottom: 12px;
        transition: border-color 0.2s ease, background 0.2s ease;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
    }
    .drag-zone:hover {
        border-color: #ff8f3d;
        background: linear-gradient(145deg, #171f31 0%, #121927 100%);
    }
    .drag-zone-icon  { font-size: 3rem; line-height: 1; margin-bottom: 10px; }
    .drag-zone-title {
        font-family: 'Nunito', sans-serif;
        font-size: 1.2rem;
        color: #e2e8f0;
        margin-bottom: 4px;
        letter-spacing: 1px;
        font-weight: 900;
        text-transform: uppercase;
    }
    .drag-zone-sub   { color: #98a4b9; font-size: 0.9rem; }

    /* ── Scan animation ──────────────────────────────────── */
    @keyframes scanDown {
        0%   { top: 0%; }
        100% { top: 100%; }
    }
    .scan-container {
        position: relative;
        overflow: hidden;
        border-radius: 14px;
        height: 76px;
        background: linear-gradient(145deg, #101623, #131a2a);
        border: 1px solid #303a4f;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 8px 0;
    }
    .scan-overlay {
        position: absolute;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #ff8f3d, transparent);
        animation: scanDown 1.1s ease-in-out infinite;
        z-index: 10;
        box-shadow: 0 0 14px rgba(255,143,61,0.85);
    }
    .scan-label {
        position: relative;
        z-index: 11;
        color: #ffd0aa;
        font-family: 'Nunito', sans-serif;
        font-size: 1.1rem;
        letter-spacing: 1.1px;
        text-transform: uppercase;
        font-weight: 900;
    }

    /* ── Project cards ───────────────────────────────────── */
    .project-section-title {
        font-family: 'Nunito', sans-serif;
        font-size: 1rem;
        color: #f3f4f6;
        margin: 22px 0 10px 0;
        font-weight: 900;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .project-card {
        background: linear-gradient(150deg, #151b29 0%, #101521 100%);
        border: 1px solid #2e374b;
        border-left: 4px solid var(--good);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.44), inset 0 0 0 1px rgba(255,255,255,0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .project-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.52);
    }
    .project-card.easy   { border-left-color: var(--good); }
    .project-card.medium { border-left-color: var(--med); }
    .project-card.hard   { border-left-color: var(--hard); }
    .project-card.combo  { border-left-color: var(--combo); border-color: #5f4b84; }
    .project-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 8px;
    }
    .project-header-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .project-emoji { font-size: 1.8rem; line-height: 1; flex-shrink: 0; }
    .project-title {
        font-family: 'Nunito', sans-serif;
        font-size: 1.06rem;
        color: #e2e8f0;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 900;
    }
    .project-difficulty-pill {
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 900;
        white-space: nowrap;
        flex-shrink: 0;
        min-height: 28px;
        display: flex;
        align-items: center;
    }
    .pill-easy   { background: rgba(34,197,94,0.14);  border: 1px solid var(--good); color: #7cf2a8; }
    .pill-medium { background: rgba(245,158,11,0.14); border: 1px solid var(--med); color: #ffcf8a; }
    .pill-hard   { background: rgba(239,68,68,0.14);  border: 1px solid var(--hard); color: #ff9ca0; }
    .pill-combo  { background: rgba(168,85,247,0.14); border: 1px solid var(--combo); color: #d4a7ff; }
    .project-tagline { color: #a8b2c4; font-size: 0.9rem; margin-bottom: 12px; line-height: 1.5; }
    .project-divider  { border: none; border-top: 1px solid #2a3347; margin: 10px 0; }
    .project-meta {
        display: flex;
        gap: 16px;
        font-size: 0.85rem;
        color: #64748b;
        flex-wrap: wrap;
        margin-bottom: 10px;
    }
    .project-meta strong { color: #c8d1df; }
    .project-steps { list-style: none; padding: 0; margin: 8px 0 14px 0; }
    .project-steps li {
        color: #cbd5e1;
        font-size: 0.88rem;
        padding: 4px 0 4px 22px;
        position: relative;
        line-height: 1.5;
    }
    .project-steps li::before {
        content: attr(data-n) ".";
        position: absolute;
        left: 0;
        color: var(--accent-soft);
        font-weight: 900;
    }
    .project-cta-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(90deg, #ff6a00, #ff8f3d);
        color: #fff !important;
        font-family: 'Nunito', sans-serif;
        font-size: 0.95rem;
        padding: 10px 20px;
        border-radius: 10px;
        border: none;
        cursor: pointer;
        text-decoration: none !important;
        min-height: 48px;
        float: right;
        margin-top: 4px;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        font-weight: 900;
        box-shadow: 0 6px 18px rgba(255,106,0,0.34);
    }
    .project-cta-btn:disabled {
        opacity: 0.92;
        cursor: default;
    }
    .project-cta-btn:hover { opacity: 0.95; transform: scale(1.02); }
    .project-empty-state {
        text-align: center;
        padding: 28px 20px;
        background: linear-gradient(145deg, #151c2b, #101621);
        border: 1px dashed #3a455e;
        border-radius: 14px;
        color: #9aa7bd;
        font-size: 0.95rem;
        margin-bottom: 14px;
    }
    .project-empty-icon { font-size: 2.5rem; margin-bottom: 8px; }

    /* ── Streamlit controls skin ─────────────────────────── */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(90deg, #ff6a00, #ff8f3d) !important;
        color: white !important;
        border: 1px solid #ff9a52 !important;
        border-radius: 12px !important;
        min-height: 48px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 6px 16px rgba(255,106,0,0.28);
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        filter: brightness(1.05);
        border-color: #ffc38f !important;
    }
    div[data-testid="stFileUploader"] > label,
    div[data-testid="stFileUploader"] section {
        background: linear-gradient(145deg, #131a28, #101621) !important;
        border: 1px solid #36425b !important;
        border-radius: 12px !important;
    }
    div[data-testid="stExpander"] details {
        background: linear-gradient(145deg, #131a27, #101621);
        border: 1px solid #2f394d;
        border-radius: 12px;
        padding: 6px 8px;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
        background-color: var(--accent) !important;
    }

    /* ── Tabs: dashboard strips ──────────────────────────── */
    div[data-testid="stTabs"] {
        background: linear-gradient(145deg, #121826, #0f141f);
        border: 1px solid #2d3548;
        border-radius: 14px;
        padding: 8px 10px 10px;
        margin-top: 8px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    }
    /* ── Bottom mobile nav ───────────────────────────────── */
    .mobile-nav-bar { display: none; }

    /* ── Settings expander ───────────────────────────────── */
    details summary { color: #d7deeb !important; font-size: 0.9rem; font-weight: 800; }

    /* ── Misc helpers ────────────────────────────────────── */
    .img-caption { text-align: center; color: #a0aec0; font-size: 0.82rem; margin-top: 4px; }
    div[data-testid="stTabs"] button {
        font-family: 'Nunito', sans-serif;
        font-weight: 900;
        text-transform: uppercase;
        font-size: 0.78rem;
        letter-spacing: 0.7px;
    }

    /* ── Mobile: 640px breakpoint ────────────────────────── */
    @media (max-width: 640px) {
        .game-title { font-size: 1.3rem; white-space: normal; }
        .hud-nav { gap: 10px; font-size: 0.66rem; }
        .hud-badge  { font-size: 0.82rem; padding: 5px 10px; }
        .quest-tiles {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
            gap: 8px;
        }
        .quest-tile-wrapper { width: 100%; max-width: 100%; height: 130px; }
        .project-card { padding: 14px 12px; }
        .completion-stats { gap: 12px; }
        .trophy-shelf { gap: 8px; }
        .trophy-card  { font-size: 0.78rem; padding: 8px 12px; }
        .drag-zone { padding: 24px 16px; }
        .drag-zone-title { font-size: 1.1rem; }
        body { padding-bottom: 64px; }

        /* Show bottom nav on mobile */
        .mobile-nav-bar {
            display: flex;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            background: rgba(14, 18, 28, 0.9);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-top: 1px solid #36435f;
            padding: 8px 16px;
            justify-content: space-around;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            font-weight: 900;
        }
        .nav-item         { display: flex; flex-direction: column; align-items: center; gap: 2px; color: #64748b; }
        .nav-item.streak  { color: #ffb27a; }
        .nav-item.score   { color: #e2e8f0; }
        .nav-item.found   { color: #86efac; }
        .nav-icon         { font-size: 1.1rem; }
    }

    /* ── Mobile: 360px breakpoint ────────────────────────── */
    @media (max-width: 360px) {
        .game-title { font-size: 1.1rem; }
        .hud-badge.timer .timer-label { display: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state init ────────────────────────────────────────────────────────

def _init_state() -> None:
    if "quest_items" not in st.session_state:
        st.session_state.quest_items        = generate_quest()
        st.session_state.quest_found        = set()
        st.session_state.quest_start_time   = time.time()
        st.session_state.quest_completed    = False
        st.session_state.quest_comp_time    = None
        st.session_state.session_score      = 0
        st.session_state.pending_sound      = None
        st.session_state.new_trophies       = []
        st.session_state.last_img_id        = None
        st.session_state.webcam_running     = False
        st.session_state.last_detections    = []
        st.session_state.last_pil_img       = None
        st.session_state.last_annotated_pil = None
    # Settings survive re-init (initialized separately)
    if "scan_confidence" not in st.session_state:
        st.session_state.scan_confidence = 0.45
    if "scan_model" not in st.session_state:
        st.session_state.scan_model = "yolo26n.pt"


_init_state()

# ── Sound helpers ─────────────────────────────────────────────────────────────

_SOUND_JS: dict[str, str] = {
    "tick": """
        var c=new(window.AudioContext||window.webkitAudioContext)(),
            o=c.createOscillator(),g=c.createGain();
        o.connect(g);g.connect(c.destination);
        o.type='sine';o.frequency.value=880;
        g.gain.setValueAtTime(0.28,c.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+0.18);
        o.start();o.stop(c.currentTime+0.18);
    """,
    "fanfare": """
        var c=new(window.AudioContext||window.webkitAudioContext)();
        [523,659,784,1047].forEach(function(f,i){
            var o=c.createOscillator(),g=c.createGain();
            o.connect(g);g.connect(c.destination);
            o.frequency.value=f;
            var t=c.currentTime+i*0.16;
            g.gain.setValueAtTime(0,t);
            g.gain.linearRampToValueAtTime(0.32,t+0.05);
            g.gain.exponentialRampToValueAtTime(0.001,t+0.4);
            o.start(t);o.stop(t+0.4);
        });
    """,
    "whoosh": """
        var c=new(window.AudioContext||window.webkitAudioContext)();
        var n=Math.floor(c.sampleRate*0.35),buf=c.createBuffer(1,n,c.sampleRate);
        var d=buf.getChannelData(0);
        for(var i=0;i<n;i++) d[i]=(Math.random()*2-1)*(1-i/n);
        var s=c.createBufferSource();s.buffer=buf;
        var f=c.createBiquadFilter();f.type='bandpass';
        f.frequency.setValueAtTime(300,c.currentTime);
        f.frequency.exponentialRampToValueAtTime(2200,c.currentTime+0.35);
        var g=c.createGain();
        g.gain.setValueAtTime(0.25,c.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+0.35);
        s.connect(f);f.connect(g);g.connect(c.destination);
        s.start();s.stop(c.currentTime+0.35);
    """,
    "thud": """
        var c=new(window.AudioContext||window.webkitAudioContext)(),
            o=c.createOscillator(),g=c.createGain();
        o.connect(g);g.connect(c.destination);
        o.type='sine';
        o.frequency.setValueAtTime(140,c.currentTime);
        o.frequency.exponentialRampToValueAtTime(40,c.currentTime+0.22);
        g.gain.setValueAtTime(0.55,c.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+0.28);
        o.start();o.stop(c.currentTime+0.28);
    """,
}


def _inject_sound(sound: str) -> None:
    js = _SOUND_JS.get(sound, "")
    if js:
        components.html(
            f"<script>try{{{js}}}catch(e){{}}</script>",
            height=1,
        )


# ── Quest board HTML ──────────────────────────────────────────────────────────

def _quest_board_html(items: List[str], found: Set[str]) -> str:
    tiles = ""
    for item in items:
        is_found = item in found
        emoji = get_emoji(item)
        cls = "found" if is_found else ""
        tiles += f"""
        <div class="quest-tile-wrapper {cls}">
            <div class="quest-tile-inner">
                <div class="quest-tile-front">
                    <div class="tile-emoji">{emoji}</div>
                    <div class="tile-name">{item}</div>
                    <div class="tile-checkbox">{'☑' if is_found else '□'}</div>
                </div>
                <div class="quest-tile-back">
                    <div class="tile-found-star">⭐</div>
                    <div class="tile-emoji">{emoji}</div>
                    <div class="tile-found-label">FOUND!</div>
                </div>
            </div>
        </div>"""

    n_found = len(found)
    n_total = len(items)
    pct = int(n_found / n_total * 100) if n_total else 0

    return f"""
    <div class="quest-board">
        <div class="quest-board-header">
            <span class="quest-board-title">🗒️ YOUR QUEST</span>
            <span class="quest-progress-pill">{n_found} / {n_total} found</span>
        </div>
        <div class="quest-tiles">{tiles}</div>
        <div class="quest-progress-bar">
            <div class="quest-progress-fill" style="width:{pct}%"></div>
        </div>
    </div>"""


# ── Game header ───────────────────────────────────────────────────────────────

def _render_header(streak: int, score: int, quest_start: float, completed: bool) -> None:
    if completed:
        timer_html = '<span class="hud-badge timer">✅ Done!</span>'
    else:
        elapsed = int(time.time() - quest_start)
        mins, secs = divmod(elapsed, 60)
        timer_html = (
            f'<span class="hud-badge timer">'
            f'<span class="timer-label">⏱&nbsp;</span>{mins}:{secs:02d}'
            f'</span>'
        )

    st.markdown(
        f"""
        <div class="game-header">
            <div class="hud-left">
                <span class="game-title">Scavenger Hunt</span>
                <div class="hud-nav">
                    <span class="hud-nav-item active">Dashboard</span>
                </div>
            </div>
            <div class="hud-badges">
                <span class="hud-badge streak">🔥 Streak: {streak}</span>
                <span class="hud-badge score">⭐ {score} pts</span>
                {timer_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Completion panel ──────────────────────────────────────────────────────────

def _render_completion(comp_time: float, score: int, new_trophies: list[str], speed_run: bool) -> None:
    mins, secs = divmod(int(comp_time), 60)
    time_str = f"{mins}m {secs}s" if mins else f"{secs}s"
    speed_badge = '<span class="new-trophy-tag">⚡ SPEED RUN!</span>' if speed_run else ""

    trophy_tags = "".join(
        f'<span class="new-trophy-tag">{t}</span>' for t in new_trophies
    )

    st.markdown(
        f"""
        <div class="completion-panel">
            <div class="completion-title">🎉 QUEST COMPLETE!</div>
            <div style="color:#86efac;font-size:1rem;margin-bottom:8px;">
                You found all 5 objects — amazing work!
            </div>
            <div class="completion-stats">
                <div class="stat-box">
                    <div class="stat-value">{time_str}</div>
                    <div class="stat-label">Time</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{score}</div>
                    <div class="stat-label">Score</div>
                </div>
            </div>
            <div class="new-trophy-row">{speed_badge}{trophy_tags}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Trophy case ───────────────────────────────────────────────────────────────

_ALL_TROPHIES = [
    "First Quest! 🏆",
    "Speed Run Star ⭐",
    "New Record! ⚡",
    "Hot Streak 🔥",
    "On Fire! 🔥🔥",
    "Legendary Streak 🌟",
    "Quest Master 🎯",
    "Explorer Elite 🌟",
]

_TROPHY_HINTS: dict[str, str] = {
    "First Quest! 🏆":       "Complete your very first quest",
    "Speed Run Star ⭐":     "Finish a quest in under 60 seconds",
    "New Record! ⚡":        "Beat your personal best completion time",
    "Hot Streak 🔥":         "Play on 3 consecutive days",
    "On Fire! 🔥🔥":         "Play on 7 consecutive days",
    "Legendary Streak 🌟":   "Play on 30 consecutive days",
    "Quest Master 🎯":       "Complete 5 quests total",
    "Explorer Elite 🌟":     "Complete 10 quests total",
}


def _render_trophy_case(trophies: list[str]) -> None:
    st.markdown('<div class="trophy-shell"><div class="trophy-section-title">🏆 Trophy Case</div>', unsafe_allow_html=True)
    cards = ""
    for t in _ALL_TROPHIES:
        if t in trophies:
            cards += f'<div class="trophy-card">{t}</div>'
        else:
            hint = _TROPHY_HINTS.get(t, "Keep playing to unlock!")
            cards += f'<div class="trophy-card locked" data-hint="{hint}">🔒 ???</div>'
    st.markdown(f'<div class="trophy-shelf">{cards}</div></div>', unsafe_allow_html=True)


# ── Share card (PIL) ──────────────────────────────────────────────────────────

def _make_share_card(
    items: List[str],
    found: Set[str],
    comp_time: float | None,
    score: int,
) -> Image.Image:
    W, H = 640, 380
    img = Image.new("RGB", (W, H), "#0d1117")
    draw = ImageDraw.Draw(img)

    try:
        fnt_big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        fnt_med = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        fnt_sm  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except Exception:
        fnt_big = fnt_med = fnt_sm = ImageFont.load_default()

    for y in range(H):
        r = int(8  + (14 - 8)  * y / H)
        g = int(12 + (24 - 12) * y / H)
        b = int(23 + (55 - 23) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    draw.text((W // 2, 32), "🔍 SCAVENGER HUNT", font=fnt_big, fill="#FFD700", anchor="mm")

    x_start, y_start = 60, 90
    col_w = 180
    for i, item in enumerate(items):
        col, row = i % 3, i // 3
        x = x_start + col * col_w
        y = y_start + row * 72
        tick = "✅" if item in found else "⬜"
        emoji = get_emoji(item)
        draw.text((x, y), f"{tick} {emoji} {item.title()}", font=fnt_med, fill="#e2e8f0")

    y_stats = 268
    draw.rectangle([(40, y_stats - 8), (W - 40, y_stats + 52)], fill="#0f1628", outline="#1e2d5c", width=2)
    if comp_time is not None:
        mins, secs = divmod(int(comp_time), 60)
        t_str = f"⏱ {mins}m {secs}s" if mins else f"⏱ {secs}s"
    else:
        t_str = "⏱ In progress"
    draw.text((80,  y_stats + 18), t_str,             font=fnt_med, fill="#7dd3fc", anchor="lm")
    draw.text((W // 2, y_stats + 18), f"⭐ {score} pts", font=fnt_med, fill="#c084fc", anchor="mm")
    n_found = len(found & set(items))
    draw.text((W - 80, y_stats + 18), f"{n_found}/5 found", font=fnt_med, fill="#4ade80", anchor="rm")

    draw.text((W // 2, H - 18), "Made with YOLOVision 🔍", font=fnt_sm, fill="#334155", anchor="mm")

    return img


# ── New quest helper ──────────────────────────────────────────────────────────

def _new_quest() -> None:
    st.session_state.quest_items        = generate_quest()
    st.session_state.quest_found        = set()
    st.session_state.quest_start_time   = time.time()
    st.session_state.quest_completed    = False
    st.session_state.quest_comp_time    = None
    st.session_state.new_trophies       = []
    st.session_state.last_img_id        = None
    st.session_state.last_pil_img       = None
    st.session_state.last_annotated_pil = None
    st.session_state.last_detections    = []
    st.session_state.pending_sound      = "whoosh"


# ── Quest detection handler ───────────────────────────────────────────────────

def _handle_detections(
    detections: List[Detection],
    quest_board_slot,
    sound_slot,
) -> None:
    """Update quest state from a list of detections; refresh board + sounds."""
    detected_names = [d.class_name for d in detections]
    quest_items = st.session_state.quest_items
    quest_found = st.session_state.quest_found

    newly_found = check_detections(detected_names, quest_items, quest_found)
    bonus_names = [n for n in detected_names if n not in quest_items]

    for name in newly_found:
        st.session_state.quest_found.add(name)
        st.session_state.session_score += 50

    st.session_state.session_score += len(bonus_names) * 5

    with quest_board_slot.container():
        st.markdown(
            _quest_board_html(quest_items, st.session_state.quest_found),
            unsafe_allow_html=True,
        )

    all_found = set(quest_items) <= st.session_state.quest_found
    if all_found and not st.session_state.quest_completed:
        st.session_state.quest_completed = True
        comp_time = time.time() - st.session_state.quest_start_time
        st.session_state.quest_comp_time = comp_time

        progress = load_progress()
        progress, new_trophies = on_quest_completed(progress, comp_time)
        save_progress(progress)

        st.session_state.new_trophies = new_trophies
        with sound_slot.container():
            _inject_sound("fanfare")
        st.balloons()
    elif newly_found:
        with sound_slot.container():
            _inject_sound("tick")


# ── Detection result list ─────────────────────────────────────────────────────

def _render_detections(detections: List[Detection], quest_items: List[str]) -> None:
    if not detections:
        st.info("No objects detected. Try a different angle or image!")
        return

    quest_hits  = [d for d in detections if d.class_name in quest_items]
    bonus_finds = [d for d in detections if d.class_name not in quest_items]

    if quest_hits:
        st.markdown("#### 🎯 Quest Objects Found!")
    for d in quest_hits:
        already = d.class_name in st.session_state.quest_found
        st.markdown(
            f"""<div class="det-card quest-hit">
                <span class="det-label">{get_emoji(d.class_name)} {d.class_name}
                {'✅' if already else '🆕'}</span>
                <span class="det-conf">{d.confidence:.0%}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    if bonus_finds:
        st.markdown("#### +5 pts each – Bonus Finds")
    for d in bonus_finds[:8]:
        st.markdown(
            f"""<div class="det-card">
                <span class="det-label">{get_emoji(d.class_name)} {d.class_name}</span>
                <span class="det-bonus">+5 pts</span>
            </div>""",
            unsafe_allow_html=True,
        )


# ── Project cards renderer ────────────────────────────────────────────────────

def _render_project_cards(suggestions: list[dict]) -> None:
    """Render project suggestion cards as styled craft-instruction cards."""
    if not suggestions:
        st.markdown(
            """
            <div class="project-empty-state">
                <div class="project-empty-icon">🎨</div>
                <div><strong style="color:#94a3b8;">Point your camera at more objects</strong><br>
                to unlock project ideas!</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<div class="project-section-title">🛠️ Project Ideas Unlocked!</div>',
        unsafe_allow_html=True,
    )

    for p in suggestions:
        is_combo = p.get("_is_combo", False)
        diff     = p.get("difficulty", "Easy").lower()

        if is_combo:
            card_cls = "combo"
            pill_cls = "combo"
            pill_lbl = "✨ Combo!"
        else:
            card_cls = diff
            pill_cls = diff
            pill_lbl = p.get("difficulty", "Easy")

        steps_html = "".join(
            f'<li data-n="{i + 1}">{step}</li>'
            for i, step in enumerate(p.get("steps", []))
        )
        materials_str = ", ".join(p.get("materials", []))

        st.markdown(
            f"""
            <div class="project-card {card_cls}">
                <div class="project-header">
                    <div class="project-header-left">
                        <span class="project-emoji">{p['emoji']}</span>
                        <span class="project-title">{p['title']}</span>
                    </div>
                    <span class="project-difficulty-pill pill-{pill_cls}">{pill_lbl}</span>
                </div>
                <div class="project-tagline">{p['tagline']}</div>
                <hr class="project-divider">
                <div class="project-meta">
                    <span>⏱ {p['time_est']}</span>
                    <span>📦 <strong>Materials:</strong> {materials_str}</span>
                </div>
                <hr class="project-divider">
                <ol class="project-steps">{steps_html}</ol>
                <button class="project-cta-btn" type="button" disabled>▶ Let's Make It! →</button>
                <div style="clear:both"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════════

progress    = load_progress()
quest_items = st.session_state.quest_items
quest_found = st.session_state.quest_found

# ── Read scanner settings from session state (set by expander below) ──────────
confidence   = st.session_state.scan_confidence
model_choice = st.session_state.scan_model

# ── Header ────────────────────────────────────────────────────────────────────
_render_header(
    streak=progress.get("streak", 0),
    score=st.session_state.session_score,
    quest_start=st.session_state.quest_start_time,
    completed=st.session_state.quest_completed,
)

# ── Quest board (placeholder for in-place updates) ────────────────────────────
quest_board_slot = st.empty()
sound_slot       = st.empty()

with quest_board_slot.container():
    st.markdown(_quest_board_html(quest_items, quest_found), unsafe_allow_html=True)

# ── Completion panel + action buttons ─────────────────────────────────────────
if st.session_state.quest_completed:
    comp_time = st.session_state.quest_comp_time or 0.0
    speed_run = comp_time <= 60
    _render_completion(
        comp_time=comp_time,
        score=st.session_state.session_score,
        new_trophies=st.session_state.new_trophies,
        speed_run=speed_run,
    )

    col_btn, col_share = st.columns(2, gap="small")
    with col_btn:
        if st.button("🎲 New Quest!", use_container_width=True, type="primary"):
            _new_quest()
            st.rerun()
    with col_share:
        card_img = _make_share_card(quest_items, quest_found, comp_time, st.session_state.session_score)
        buf = io.BytesIO()
        card_img.save(buf, format="PNG")
        st.download_button(
            label="📤 Save Card",
            data=buf.getvalue(),
            file_name="scavenger_hunt_result.png",
            mime="image/png",
            use_container_width=True,
        )

# ── Pending sound ─────────────────────────────────────────────────────────────
if st.session_state.pending_sound:
    _inject_sound(st.session_state.pending_sound)
    st.session_state.pending_sound = None

# ── Load model (uses settings from session state) ─────────────────────────────
model = load_model(model_choice)

# ── Detection tabs ────────────────────────────────────────────────────────────
tab_img, tab_cam = st.tabs(["📸 Upload a Photo", "📷 Live Camera"])


# ══ TAB 1 – Image Upload ══════════════════════════════════════════════════════

with tab_img:
    if st.session_state.quest_completed:
        st.info("Quest complete! Start a new quest above to keep scanning.")
    else:
        # Decorative drag zone (visual affordance; actual upload below)
        st.markdown(
            """
            <div class="drag-zone">
                <div class="drag-zone-icon">📷</div>
                <div class="drag-zone-title">Drag a photo here</div>
                <div class="drag-zone-sub">— or use the browse button below —</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Drop or browse an image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )

        if uploaded is not None:
            file_id = f"{uploaded.name}_{uploaded.size}"

            if file_id != st.session_state.last_img_id:
                st.session_state.last_img_id = file_id

                try:
                    raw     = uploaded.read()
                    pil_img = Image.open(io.BytesIO(raw))
                    pil_img.verify()
                    pil_img = Image.open(io.BytesIO(raw)).convert("RGB")
                except Exception as exc:
                    st.error(f"⚠️ Couldn't open image: `{exc}`")
                    st.stop()

                # Animated scan banner during inference
                scan_slot = st.empty()
                scan_slot.markdown(
                    """
                    <div class="scan-container">
                        <div class="scan-overlay"></div>
                        <div class="scan-label">🔍&nbsp; Scanning for objects…</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                try:
                    annotated_bgr, detections = run_inference(model, pil_img, confidence)
                    annotated_pil             = bgr_to_pil(annotated_bgr)
                except Exception as exc:
                    scan_slot.empty()
                    st.error(f"⚠️ Inference failed: `{exc}`")
                    st.stop()

                scan_slot.empty()

                # Persist results in session state for reruns
                st.session_state.last_pil_img       = pil_img
                st.session_state.last_annotated_pil = annotated_pil
                st.session_state.last_detections    = detections
                _handle_detections(detections, quest_board_slot, sound_slot)

        # Display results (persists across reruns while same file is uploaded)
        if (
            st.session_state.last_detections is not None
            and st.session_state.last_pil_img is not None
        ):
            # Image tabs (replaces two-column layout — stacks cleanly on mobile)
            img_orig_tab, img_det_tab = st.tabs(["🖼 Original", "🔍 Detected"])
            with img_orig_tab:
                st.image(st.session_state.last_pil_img, use_container_width=True)
                st.markdown('<p class="img-caption">Original photo</p>', unsafe_allow_html=True)
            with img_det_tab:
                if st.session_state.last_annotated_pil is not None:
                    st.image(st.session_state.last_annotated_pil, use_container_width=True)
                    st.markdown('<p class="img-caption">YOLO Detections</p>', unsafe_allow_html=True)

            st.markdown("---")
            _render_detections(st.session_state.last_detections, quest_items)

            # Project suggestions derived from detections
            detected_names = [d.class_name for d in st.session_state.last_detections]
            suggestions    = get_project_suggestions(detected_names, max_results=3)
            _render_project_cards(suggestions)


# ══ TAB 2 – Live Camera ═══════════════════════════════════════════════════════

with tab_cam:
    if st.session_state.quest_completed:
        st.info("Quest complete! Start a new quest above to keep scanning.")
    else:
        st.markdown(
            "📷 **Point your camera** at objects around the room to find your quest items!"
        )

        if "webcam_running" not in st.session_state:
            st.session_state.webcam_running = False

        c1, c2, _ = st.columns([1, 1, 4])
        with c1:
            start_btn = st.button(
                "▶ Start",
                disabled=st.session_state.webcam_running,
                use_container_width=True,
                type="primary",
            )
        with c2:
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

        cam_status = (
            '<span style="color:#4ade80;font-weight:900">● Live</span>'
            if st.session_state.webcam_running
            else '<span style="color:#ef4444;font-weight:900">● Stopped</span>'
        )
        st.markdown(cam_status, unsafe_allow_html=True)

        frame_placeholder   = st.empty()
        cam_projects_slot   = st.empty()

        if st.session_state.webcam_running:
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                st.error(
                    "⚠️ **Webcam not accessible.** "
                    "Grant camera permission in System Settings → Privacy → Camera, then try again."
                )
                st.session_state.webcam_running = False
                cap.release()
                st.stop()

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            try:
                frame_count = 0
                while st.session_state.webcam_running:
                    ret, frame_bgr = cap.read()
                    if not ret:
                        time.sleep(0.1)
                        continue

                    ann_bgr, detections = run_inference(model, frame_bgr, confidence)
                    st.session_state.last_detections = detections

                    _handle_detections(detections, quest_board_slot, sound_slot)

                    ann_rgb = cv2.cvtColor(ann_bgr, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(
                        ann_rgb,
                        channels="RGB",
                        use_container_width=True,
                        caption="Live YOLO Detections",
                    )

                    # Refresh project suggestions every 60 frames
                    frame_count += 1
                    if frame_count % 60 == 0 and detections:
                        detected_names = [d.class_name for d in detections]
                        suggestions    = get_project_suggestions(detected_names, max_results=2)
                        with cam_projects_slot.container():
                            _render_project_cards(suggestions)

                    if st.session_state.quest_completed:
                        break

                    time.sleep(0.05)
            finally:
                cap.release()

        # Show project suggestions from last captured detections
        if not st.session_state.webcam_running and st.session_state.last_detections:
            detected_names = [d.class_name for d in st.session_state.last_detections]
            suggestions    = get_project_suggestions(detected_names, max_results=3)
            with cam_projects_slot.container():
                _render_project_cards(suggestions)


# ── Trophy case ───────────────────────────────────────────────────────────────
st.markdown("---")
progress = load_progress()
_render_trophy_case(progress.get("trophies", []))

# ── ⚙️ Scanner Settings (power users find it; casual users never see it) ──────
with st.expander("⚙️ Scanner Settings", expanded=False):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.slider(
            "Confidence",
            min_value=0.10,
            max_value=1.00,
            step=0.05,
            key="scan_confidence",
        )
    with col_s2:
        st.selectbox(
            "YOLO Variant",
            ["yolo26n.pt", "yolo26s.pt", "yolo26m.pt", "yolo26l.pt", "yolo26x.pt"],
            help="n = fastest · x = most accurate",
            key="scan_model",
        )

# ── Footer ────────────────────────────────────────────────────────────────────
best     = progress.get("best_time")
best_str = (
    f"{int(best // 60)}m {int(best % 60)}s" if best and best >= 60 else
    f"{int(best)}s"                          if best               else "—"
)
total_q = progress.get("total_quests_completed", 0)
st.markdown(
    f"<p style='text-align:center;color:#334155;font-size:0.8rem;margin-top:8px;'>"
    f"Quests completed: {total_q} · Best time: {best_str} · "
    f"<a href='https://docs.ultralytics.com/models/yolo26/' "
    f"style='color:#334155'>YOLO26</a></p>",
    unsafe_allow_html=True,
)

# ── Mobile bottom nav bar (fixed, shown only on screens ≤640px via CSS) ───────
_streak  = progress.get("streak", 0)
_score   = st.session_state.session_score
_n_found = len(st.session_state.quest_found)

st.markdown(
    f"""
    <div class="mobile-nav-bar">
        <div class="nav-item streak">
            <span class="nav-icon">🔥</span>
            {_streak} streak
        </div>
        <div class="nav-item score">
            <span class="nav-icon">⭐</span>
            {_score} pts
        </div>
        <div class="nav-item found">
            <span class="nav-icon">🎯</span>
            {_n_found}/5 found
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
