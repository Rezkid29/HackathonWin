"""
app.py
======
MakeGyver
---------
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

import base64
import io
import time
from pathlib import Path
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
from utils.completed import save_completed_project, load_completed_projects, is_project_completed

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="MakeGyver",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;700;900&display=swap');

    :root {
        --glass-bg: rgba(255,255,255,0.5);
        --glass-border: rgba(255,255,255,0.6);
        --glass-shadow: 0 4px 30px rgba(0,0,0,0.08);
        --text-main: #1e293b;
        --text-muted: #64748b;
        --accent: #3b82f6;
        --good: #22c55e;
        --med: #f59e0b;
        --hard: #ef4444;
        --combo: #a855f7;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: #f1f5f9 !important;
        font-family: 'Inter', system-ui, sans-serif !important;
        color: var(--text-main);
    }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    footer { visibility: hidden; }
    section.main > div {
        max-width: 1180px;
        margin-left: auto;
        margin-right: auto;
        padding-top: 22px;
        padding-bottom: 84px;
    }
    div[data-testid="stMainBlockContainer"] {
        max-width: 1180px;
        margin-left: auto;
        margin-right: auto;
    }
    hr { border-color: rgba(0,0,0,0.08) !important; }

    /* ── Sticky: keep header + tabs + completed in view ───── */
    .game-header {
        position: sticky;
        top: 0;
        z-index: 200;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.7);
        border-radius: 16px;
        padding: 14px 18px;
        margin-bottom: 14px;
        gap: 10px;
        flex-wrap: wrap;
        box-shadow: 0 4px 30px rgba(0,0,0,0.08);
    }
    .header-spacer { flex: 1; min-width: 0; }
    .header-logo-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-shrink: 0;
    }
    .header-badges {
        display: flex;
        gap: 10px;
        align-items: center;
        flex-wrap: wrap;
        justify-content: flex-end;
    }
    .header-logo { height: 38px; width: auto; display: block; object-fit: contain; }
    .game-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text-main);
        letter-spacing: -0.02em;
    }
    .hud-nav { display: flex; align-items: center; gap: 16px; font-size: 0.8rem; font-weight: 600; color: var(--text-muted); }
    .hud-nav-item { padding: 4px 0; border-bottom: 2px solid transparent; }
    .hud-nav-item.active { color: var(--accent); border-bottom-color: var(--accent); }
    .hud-badges { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
    .hud-badge {
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.7);
        border-radius: 12px;
        padding: 8px 14px;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-main);
        white-space: nowrap;
        min-height: 44px;
        display: flex;
        align-items: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .hud-badge.streak { color: #ea580c; }
    .hud-badge.score  { color: var(--text-main); }
    .hud-badge.timer  { color: #0284c7; }

    /* ── Glass: Quest board ───────────────────────────────── */
    .quest-board {
        background: rgba(255,255,255,0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.65);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 30px rgba(0,0,0,0.08);
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
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-main);
    }
    .quest-progress-pill {
        background: rgba(255,255,255,0.6);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(255,255,255,0.8);
        border-radius: 20px;
        padding: 6px 12px;
        font-weight: 600;
        font-size: 0.85rem;
        color: var(--text-main);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
        background: rgba(255,255,255,0.6);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.7);
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .quest-tile-front:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    .quest-tile-back {
        background: rgba(255,255,255,0.7);
        border: 1px solid rgba(34,197,94,0.4);
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transform: rotateY(180deg);
    }
    .tile-emoji      { font-size: 2.2rem; line-height: 1; }
    .tile-name       { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
                       letter-spacing: 0.5px; color: var(--text-muted); text-align: center; }
    .tile-checkbox   { font-size: 1.1rem; color: var(--text-muted); }
    .tile-found-star { font-size: 2rem; line-height: 1; }
    .tile-found-label{ font-size: 0.7rem; font-weight: 700; color: #16a34a;
                       text-transform: uppercase; letter-spacing: 1px; }

    .quest-progress-bar {
        height: 8px;
        background: rgba(0,0,0,0.06);
        border-radius: 8px;
        margin-top: 14px;
        overflow: hidden;
    }
    .quest-progress-fill {
        height: 100%;
        background: var(--accent);
        border-radius: 8px;
        transition: width 0.6s ease;
    }

    /* ── Glass: Completion panel ───────────────────────────── */
    .completion-panel {
        background: rgba(255,255,255,0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.7);
        border-radius: 16px;
        padding: 22px 20px;
        text-align: center;
        margin-bottom: 14px;
        box-shadow: 0 4px 30px rgba(0,0,0,0.08);
    }
    .completion-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 6px;
    }
    .completion-stats {
        display: flex;
        justify-content: center;
        gap: 24px;
        flex-wrap: wrap;
        margin: 16px 0;
    }
    .stat-box {
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.7);
        border-radius: 12px;
        padding: 10px 18px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .stat-value { font-size: 1.5rem; font-weight: 700; color: var(--accent); }
    .stat-label { font-size: 0.75rem; color: var(--text-muted); }
    .new-trophy-row {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 12px;
    }
    .new-trophy-tag {
        background: rgba(255,255,255,0.5);
        border: 1px solid rgba(34,197,94,0.4);
        border-radius: 10px;
        padding: 6px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #16a34a;
    }

    /* ── Glass: Trophy case ───────────────────────────────── */
    .trophy-shell {
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 16px;
        padding: 14px 14px 8px;
        box-shadow: 0 4px 30px rgba(0,0,0,0.08);
    }
    .trophy-section-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 12px;
    }
    .trophy-shelf {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 24px;
    }
    .trophy-card {
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.7);
        border-radius: 12px;
        padding: 10px 16px;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-main);
        position: relative;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .trophy-card.locked {
        background: rgba(255,255,255,0.35);
        color: var(--text-muted);
        cursor: help;
    }
    .trophy-card.locked:hover::after {
        content: attr(data-hint);
        position: absolute;
        bottom: calc(100% + 8px);
        left: 50%;
        transform: translateX(-50%);
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(8px);
        color: var(--text-main);
        font-size: 0.75rem;
        font-weight: 600;
        padding: 6px 10px;
        border-radius: 8px;
        white-space: nowrap;
        z-index: 100;
        pointer-events: none;
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }

    /* ── Glass: Detection cards ───────────────────────────── */
    .det-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 12px;
        padding: 8px 14px;
        margin-bottom: 6px;
        min-height: 48px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .det-card.quest-hit { border-color: rgba(59,130,246,0.4); background: rgba(255,255,255,0.6); }
    .det-label { font-weight: 600; color: var(--text-main); font-size: 0.9rem; }
    .det-conf  { font-size: 0.82rem; color: var(--accent); font-weight: 600; }
    .det-bonus { font-size: 0.75rem; color: var(--text-muted); font-weight: 600; }

    /* ── Drag-zone upload ────────────────────────────────── */

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
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 8px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    .scan-overlay {
        position: absolute;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
        animation: scanDown 1.1s ease-in-out infinite;
        z-index: 10;
        opacity: 0.8;
    }
    .scan-label {
        position: relative;
        z-index: 11;
        color: var(--text-main);
        font-size: 1rem;
        font-weight: 700;
    }

    /* ── Glass: Project cards ─────────────────────────────── */
    .project-section-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-main);
        margin: 22px 0 10px 0;
    }
    .project-card {
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.6);
        border-left: 4px solid var(--good);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .project-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(0,0,0,0.1);
    }
    .project-card.easy   { border-left-color: var(--good); }
    .project-card.medium { border-left-color: var(--med); }
    .project-card.hard   { border-left-color: var(--hard); }
    .project-card.combo  { border-left-color: var(--combo); }
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
        font-size: 1.06rem;
        font-weight: 700;
        color: var(--text-main);
    }
    .project-difficulty-pill {
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        white-space: nowrap;
        flex-shrink: 0;
        min-height: 28px;
        display: flex;
        align-items: center;
    }
    .pill-easy   { background: rgba(34,197,94,0.12);  border: 1px solid var(--good); color: #16a34a; }
    .pill-medium { background: rgba(245,158,11,0.12); border: 1px solid var(--med); color: #b45309; }
    .pill-hard   { background: rgba(239,68,68,0.12);  border: 1px solid var(--hard); color: #dc2626; }
    .pill-combo  { background: rgba(168,85,247,0.12); border: 1px solid var(--combo); color: #7c3aed; }
    .project-tagline { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 12px; line-height: 1.5; }
    .project-divider  { border: none; border-top: 1px solid rgba(0,0,0,0.08); margin: 10px 0; }
    .project-meta {
        display: flex;
        gap: 16px;
        font-size: 0.85rem;
        color: var(--text-muted);
        flex-wrap: wrap;
        margin-bottom: 10px;
    }
    .project-meta strong { color: var(--text-main); }
    .project-steps { list-style: none; padding: 0; margin: 8px 0 14px 0; }
    .project-steps li {
        color: var(--text-main);
        font-size: 0.88rem;
        padding: 4px 0 4px 22px;
        position: relative;
        line-height: 1.5;
    }
    .project-steps li::before {
        content: attr(data-n) ".";
        position: absolute;
        left: 0;
        color: var(--accent);
        font-weight: 600;
    }
    .project-cta-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        background: var(--accent);
        color: #fff !important;
        font-size: 0.9rem;
        padding: 10px 20px;
        border-radius: 12px;
        border: none;
        cursor: default;
        text-decoration: none !important;
        min-height: 48px;
        margin-top: 10px;
        font-weight: 600;
        width: 100%;
    }
    .project-empty-state {
        text-align: center;
        padding: 28px 20px;
        background: rgba(255,255,255,0.4);
        border: 1px dashed rgba(0,0,0,0.12);
        border-radius: 14px;
        color: var(--text-muted);
        font-size: 0.95rem;
        margin-bottom: 14px;
    }
    .project-empty-icon { font-size: 2.5rem; margin-bottom: 8px; }
    .stem-badge {
        display: inline-flex;
        align-items: center;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        padding: 2px 9px;
        border-radius: 20px;
        border: 1px solid;
    }
    .project-learn {
        background: rgba(255,255,255,0.5);
        border: 1px solid rgba(255,255,255,0.6);
        border-left: 3px solid var(--accent);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.85rem;
        color: var(--text-main);
        margin: 10px 0 14px 0;
        line-height: 1.5;
    }
    .project-done-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(34,197,94,0.12);
        border: 1px solid #22c55e;
        color: #16a34a;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 8px 16px;
        border-radius: 10px;
        margin-top: 10px;
        width: 100%;
        justify-content: center;
    }
    /* ── Glass: Completed projects log panel ───────────────── */
    .cp-panel {
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 18px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    }
    .cp-panel-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 12px;
    }
    details.cp-row {
        border-radius: 8px;
        background: rgba(255,255,255,0.35);
        border: 1px solid rgba(255,255,255,0.5);
        margin-bottom: 7px;
        overflow: hidden;
        transition: border-color 0.15s;
    }
    details.cp-row:last-child { margin-bottom: 0; }
    details.cp-row[open] { border-color: rgba(59,130,246,0.4); }
    summary.cp-summary {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 10px;
        cursor: pointer;
        list-style: none;
        user-select: none;
    }
    summary.cp-summary::-webkit-details-marker { display: none; }
    summary.cp-summary::after {
        content: "›";
        margin-left: auto;
        font-size: 1.1rem;
        color: var(--text-muted);
        transition: transform 0.2s;
        flex-shrink: 0;
    }
    details.cp-row[open] > summary.cp-summary::after {
        transform: rotate(90deg);
        color: var(--accent);
    }
    summary.cp-summary:hover { background: rgba(59,130,246,0.06); }
    .cp-emoji { font-size: 1.4rem; flex-shrink: 0; }
    .cp-info  { flex: 1; min-width: 0; }
    .cp-title { font-weight: 700; color: var(--text-main); font-size: 0.9rem; }
    .cp-meta  { color: var(--text-muted); font-size: 0.75rem; margin-top: 2px; }
    .cp-stem  {
        font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px;
        text-transform: uppercase; padding: 2px 8px;
        border-radius: 20px; border: 1px solid; flex-shrink: 0;
    }
    .cp-detail {
        padding: 0 12px 12px 12px;
        border-top: 1px solid rgba(0,0,0,0.06);
    }
    .cp-tagline {
        font-size: 0.83rem;
        color: var(--text-muted);
        font-style: italic;
        margin: 8px 0 6px 0;
        line-height: 1.4;
    }
    .cp-learn {
        font-size: 0.8rem;
        color: var(--text-main);
        background: rgba(59,130,246,0.08);
        border-left: 3px solid var(--accent);
        border-radius: 0 6px 6px 0;
        padding: 5px 10px;
        margin-top: 6px;
        line-height: 1.5;
    }
    .cp-section-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: var(--accent);
        margin: 10px 0 5px 0;
    }
    .cp-mat-list { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 4px; }
    .cp-mat-chip {
        font-size: 0.73rem;
        color: var(--text-muted);
        background: rgba(255,255,255,0.5);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 20px;
        padding: 2px 9px;
    }
    .cp-steps {
        list-style: none;
        padding: 0;
        margin: 0 0 4px 0;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    .cp-step {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        font-size: 0.8rem;
        color: var(--text-main);
        line-height: 1.45;
    }
    .cp-step-n {
        flex-shrink: 0;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: rgba(59,130,246,0.12);
        border: 1px solid var(--accent);
        color: var(--accent);
        font-size: 0.65rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 1px;
    }
    div[data-testid="stButton"] button[kind="secondary"] {
        background: rgba(34,197,94,0.9) !important;
        border-color: #22c55e !important;
        color: #fff !important;
    }

    /* ── Glass: Streamlit buttons ─────────────────────────── */
    div.stButton > button, div.stDownloadButton > button {
        background: var(--accent) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-radius: 12px !important;
        min-height: 48px !important;
        font-weight: 600 !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        filter: brightness(1.05);
    }
    div[data-testid="stFileUploader"] > label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--text-main) !important;
    }
    div[data-testid="stFileUploader"] section {
        background: rgba(255,255,255,0.5) !important;
        backdrop-filter: blur(8px);
        border: 2px dashed rgba(0,0,0,0.12) !important;
        border-radius: 18px !important;
        padding: 20px 24px 24px !important;
        text-align: center;
        transition: border-color 0.2s ease;
    }
    div[data-testid="stFileUploader"] section:hover {
        border-color: var(--accent) !important;
    }
    /* Large camera icon injected above the native text */
    div[data-testid="stFileUploader"] section::before {
        content: "📷";
        display: block;
        font-size: 2.6rem;
        line-height: 1;
        margin-bottom: 8px;
    }
    /* Hide the repeated "Drag and drop file here" instruction text */
    div[data-testid="stFileUploader"] section > div > span {
        display: none !important;
    }
    /* ── Uploaded file chip — collapsible ────────────────── */
    div[data-testid="stFileUploader"] ul {
        list-style: none !important;
        padding: 0 !important;
        margin: 8px 0 0 0 !important;
    }
    div[data-testid="stFileUploader"] li {
        background: rgba(255,255,255,0.5) !important;
        border: 1px solid rgba(255,255,255,0.6) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    div[data-testid="stFileUploaderFile"] {
        cursor: pointer;
        padding: 6px 12px !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px;
        transition: background 0.15s;
    }
    div[data-testid="stFileUploaderFile"]:hover {
        background: rgba(59,130,246,0.08) !important;
    }
    div[data-testid="stFileUploaderFileData"] {
        flex: 1;
        min-width: 0;
    }
    div[data-testid="stFileUploaderFileName"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: var(--text-main) !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    div[data-testid="stFileUploader"] [role="progressbar"] {
        height: 3px !important;
        border-radius: 2px;
        background: rgba(0,0,0,0.08) !important;
    }
    div[data-testid="stFileUploader"] [role="progressbar"] > div {
        background: var(--accent) !important;
    }
    div[data-testid="stExpander"] details {
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 12px;
        padding: 6px 8px;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
        background-color: var(--accent) !important;
    }

    div[data-testid="stTabs"] {
        position: sticky;
        top: 72px;
        z-index: 150;
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 14px;
        padding: 8px 10px 10px;
        margin-top: 8px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    }
    .mobile-nav-bar { display: none; }

    details summary { color: var(--text-main) !important; font-size: 0.9rem; font-weight: 600; }

    .img-caption { text-align: center; color: var(--text-muted); font-size: 0.82rem; margin-top: 4px; }
    div[data-testid="stTabs"] button {
        font-weight: 600;
        font-size: 0.78rem;
    }
    /* Keep tab labels and expander summary visible in all states */
    div[data-testid="stTabs"] button p,
    div[data-testid="stTabs"] [data-cursor-element-id] {
        color: var(--text-main) !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] details summary {
        color: var(--text-main) !important;
        visibility: visible !important;
        opacity: 1 !important;
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
        body { padding-bottom: 64px; }

        .mobile-nav-bar {
            display: flex;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            background: rgba(255,255,255,0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-top: 1px solid rgba(255,255,255,0.8);
            padding: 8px 16px;
            justify-content: space-around;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            box-shadow: 0 -4px 24px rgba(0,0,0,0.06);
        }
        .nav-item         { display: flex; flex-direction: column; align-items: center; gap: 2px; color: var(--text-muted); }
        .nav-item.streak  { color: #ea580c; }
        .nav-item.score   { color: var(--text-main); }
        .nav-item.found   { color: #16a34a; }
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
    # Completed projects: set of titles for fast O(1) lookup
    if "completed_project_titles" not in st.session_state:
        st.session_state.completed_project_titles = {
            r["title"] for r in load_completed_projects()
        }


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

def _logo_data_uri() -> str:
    """Load MakeGyver logo as a data URI for embedding in the header."""
    logo_path = Path(__file__).parent / "assets" / "makegyver-logo.png"
    if not logo_path.exists():
        return ""
    raw = logo_path.read_bytes()
    b64 = base64.b64encode(raw).decode()
    return f"data:image/png;base64,{b64}"


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
    logo_src = _logo_data_uri()
    logo_img = f'<img src="{logo_src}" alt="MakeGyver" class="header-logo" />' if logo_src else ""
    st.markdown(
        f"""
        <div class="game-header">
            <div class="header-spacer"></div>
            <div class="header-logo-wrap">{logo_img}</div>
            <div class="header-spacer header-badges">
                <span class="hud-badge streak">🔥 Streak: {streak}</span>
                <span class="hud-badge score">⭐ {score} pts</span>
                {timer_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_header_simple() -> None:
    """Minimal header for Detect mode (no streak/timer/quest)."""
    logo_src = _logo_data_uri()
    logo_img = f'<img src="{logo_src}" alt="MakeGyver" class="header-logo" />' if logo_src else ""
    st.markdown(
        f"""
        <div class="game-header">
            <div class="header-spacer"></div>
            <div class="header-logo-wrap">{logo_img}</div>
            <div class="header-spacer"></div>
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

    draw.text((W // 2, 32), "🔍 MAKEGYVER", font=fnt_big, fill="#FFD700", anchor="mm")

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

    draw.text((W // 2, H - 18), "Made with MakeGyver 🔍", font=fnt_sm, fill="#334155", anchor="mm")

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


# ── Completed projects log ────────────────────────────────────────────────────

def _render_completed_log() -> None:
    """Render the completed projects expander panel with collapsible rows."""
    from utils.projects import PROJECT_MAP, COMBO_MAP

    # Build a flat title → project dict lookup for enriching stored records
    _all_projects: dict[str, dict] = {}
    for projects in PROJECT_MAP.values():
        for p in projects:
            _all_projects.setdefault(p["title"], p)
    for p in COMBO_MAP.values():
        _all_projects.setdefault(p["title"], p)

    records = load_completed_projects()

    _stem_colours = {
        "Science":     ("#1c3a55", "#38bdf8", "#9fdcff"),
        "Engineering": ("#3d1f00", "#ff6a00", "#ffd0aa"),
        "Technology":  ("#2d1a4a", "#a855f7", "#d4a7ff"),
        "Math":        ("#0f3020", "#22c55e", "#7cf2a8"),
    }

    label = f"📚 Completed Projects ({len(records)})"
    with st.expander(label, expanded=False):
        if not records:
            st.markdown(
                "<p style='color:#6b7f9a;font-size:0.9rem;margin:0;'>"
                "No projects completed yet — scan objects to get suggestions, then mark them done!</p>",
                unsafe_allow_html=True,
            )
            return

        rows_html = ""
        for r in records:
            stem = r.get("stem_tag", "")
            bg, border, color = _stem_colours.get(stem, ("#1a2236", "#64748b", "#94a3b8"))
            stem_pill = (
                f'<span class="cp-stem" style="background:{bg};border-color:{border};color:{color};">'
                f"{stem}</span>"
            ) if stem else ""

            dt_str = r.get("completed_at", "")[:10]
            diff   = r.get("difficulty", "")
            meta   = " · ".join(filter(None, [diff, r.get("time_est", ""), dt_str]))

            # Enrich from the canonical project definition
            full      = _all_projects.get(r.get("title", ""), {})
            tagline   = r.get("tagline") or full.get("tagline", "")
            learn     = full.get("learn", "")
            steps     = full.get("steps", [])
            materials = full.get("materials", [])

            tagline_html = (
                f'<div class="cp-tagline">"{tagline}"</div>'
            ) if tagline else ""

            learn_html = (
                f'<div class="cp-learn">💡 {learn}</div>'
            ) if learn else ""

            materials_html = ""
            if materials:
                chips = "".join(
                    f'<span class="cp-mat-chip">{m}</span>' for m in materials
                )
                materials_html = (
                    f'<div class="cp-section-label">📦 Materials</div>'
                    f'<div class="cp-mat-list">{chips}</div>'
                )

            steps_html = ""
            if steps:
                lis = "".join(
                    f'<li class="cp-step"><span class="cp-step-n">{i+1}</span>{s}</li>'
                    for i, s in enumerate(steps)
                )
                steps_html = (
                    f'<div class="cp-section-label">📋 Steps</div>'
                    f'<ol class="cp-steps">{lis}</ol>'
                )

            rows_html += f"""
            <details class="cp-row">
                <summary class="cp-summary">
                    <span class="cp-emoji">{r.get('emoji','🛠️')}</span>
                    <div class="cp-info">
                        <div class="cp-title">{r.get('title','')}</div>
                        <div class="cp-meta">{meta}</div>
                    </div>
                    {stem_pill}
                </summary>
                <div class="cp-detail">
                    {tagline_html}
                    {learn_html}
                    {materials_html}
                    {steps_html}
                </div>
            </details>"""

        st.markdown(
            f'<div class="cp-panel"><div class="cp-panel-title">🏅 Your STEM Lab Log</div>{rows_html}</div>',
            unsafe_allow_html=True,
        )


# ── Project cards renderer ────────────────────────────────────────────────────

def _render_project_cards(
    suggestions: list[dict],
    detected_names: list[str] | None = None,
    context: str = "default",
) -> None:
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

        stem_tag  = p.get("stem_tag", "")
        learn_txt = p.get("learn", "")

        _stem_colours = {
            "Science":     ("rgba(56,189,248,0.14)", "#38bdf8", "#9fdcff"),
            "Engineering": ("rgba(255,106,0,0.14)",  "#ff6a00", "#ffd0aa"),
            "Technology":  ("rgba(168,85,247,0.14)", "#a855f7", "#d4a7ff"),
            "Math":        ("rgba(34,197,94,0.14)",  "#22c55e", "#7cf2a8"),
        }
        s_bg, s_border, s_color = _stem_colours.get(
            stem_tag, ("rgba(100,116,139,0.14)", "#64748b", "#94a3b8")
        )
        stem_badge = (
            f'<span class="stem-badge" style="background:{s_bg};border-color:{s_border};color:{s_color};">'
            f'{stem_tag}</span>'
        ) if stem_tag else ""

        learn_block = (
            f'<div class="project-learn">💡 {learn_txt}</div>'
        ) if learn_txt else ""

        already_done = p["title"] in st.session_state.get("completed_project_titles", set())

        st.markdown(
            f"""
            <div class="project-card {card_cls}">
                <div class="project-header">
                    <div class="project-header-left">
                        <span class="project-emoji">{p['emoji']}</span>
                        <div>
                            <span class="project-title">{p['title']}</span>
                            <div style="margin-top:4px;">{stem_badge}</div>
                        </div>
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
                {learn_block}
                {"<div class='project-done-badge'>✅ Completed!</div>" if already_done else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not already_done:
            btn_key = f"complete_{context}_{p['title'].replace(' ', '_')}"
            if st.button("✅ Mark as Complete", key=btn_key, use_container_width=True):
                p["_objects_detected"] = detected_names or []
                save_completed_project(p)
                st.session_state.completed_project_titles.add(p["title"])
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════════

progress    = load_progress()
quest_items = st.session_state.quest_items
quest_found = st.session_state.quest_found
confidence  = st.session_state.scan_confidence
model_choice = st.session_state.scan_model
model      = load_model(model_choice)

tab_detect, tab_quest = st.tabs(["🔍 Detect", "🎯 Scavenger Hunt"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB: DETECT (core object detection, no quest)
# ═══════════════════════════════════════════════════════════════════════════════

with tab_detect:
    _render_header_simple()
    tab_img_d, tab_cam_d = st.tabs(["📸 Upload a Photo", "📷 Live Camera"])
    _render_completed_log()

    with tab_img_d:
        uploaded = st.file_uploader(
            "📷  Drag a photo here, or click to browse",
            type=["jpg", "jpeg", "png"],
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

        # Display results (persists across reruns while same file is uploaded)
        if (
            st.session_state.last_detections is not None
            and st.session_state.last_pil_img is not None
        ):
            img_orig_tab, img_det_tab = st.tabs(["🖼 Original", "🔍 Detected"])
            with img_orig_tab:
                st.image(st.session_state.last_pil_img, use_container_width=True)
                st.markdown('<p class="img-caption">Original photo</p>', unsafe_allow_html=True)
            with img_det_tab:
                if st.session_state.last_annotated_pil is not None:
                    st.image(st.session_state.last_annotated_pil, use_container_width=True)
                    st.markdown('<p class="img-caption">YOLO Detections</p>', unsafe_allow_html=True)

            st.markdown("---")
            _render_detections(st.session_state.last_detections, [])

            detected_names = [d.class_name for d in st.session_state.last_detections]
            suggestions    = get_project_suggestions(detected_names, max_results=3)
            _render_project_cards(suggestions, detected_names, context="img")

    with tab_cam_d:
        st.markdown("📷 **Point your camera** at objects to detect — no quest required.")

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

                    ann_rgb = cv2.cvtColor(ann_bgr, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(
                        ann_rgb,
                        channels="RGB",
                        use_container_width=True,
                        caption="Live YOLO Detections",
                    )

                    frame_count += 1
                    if frame_count % 60 == 0 and detections:
                        detected_names = [d.class_name for d in detections]
                        suggestions    = get_project_suggestions(detected_names, max_results=2)
                        with cam_projects_slot.container():
                            _render_project_cards(suggestions, detected_names, context="cam_live")

                    time.sleep(0.05)
            finally:
                cap.release()

        # Show project suggestions from last captured detections
        if not st.session_state.webcam_running and st.session_state.last_detections:
            detected_names = [d.class_name for d in st.session_state.last_detections]
            suggestions    = get_project_suggestions(detected_names, max_results=3)
            with cam_projects_slot.container():
                _render_project_cards(suggestions, detected_names, context="cam_stopped")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB: SCAVENGER HUNT (quest mode)
# ═══════════════════════════════════════════════════════════════════════════════

with tab_quest:
    _render_header(
        streak=progress.get("streak", 0),
        score=st.session_state.session_score,
        quest_start=st.session_state.quest_start_time,
        completed=st.session_state.quest_completed,
    )
    quest_board_slot = st.empty()
    sound_slot       = st.empty()
    with quest_board_slot.container():
        st.markdown(_quest_board_html(quest_items, quest_found), unsafe_allow_html=True)

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
            if st.button("🎲 New Quest!", use_container_width=True, type="primary", key="new_quest_btn"):
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
                key="share_card_btn",
            )

    if st.session_state.pending_sound:
        _inject_sound(st.session_state.pending_sound)
        st.session_state.pending_sound = None

    tab_img, tab_cam = st.tabs(["📸 Upload a Photo", "📷 Live Camera"])
    _render_completed_log()

    with tab_img:
        if st.session_state.quest_completed:
            st.info("Quest complete! Start a new quest above to keep scanning.")
        else:
            uploaded_q = st.file_uploader(
                "📷  Drag a photo here, or click to browse",
                type=["jpg", "jpeg", "png"],
                key="quest_upload",
            )
            if uploaded_q is not None:
                file_id = f"{uploaded_q.name}_{uploaded_q.size}"
                if file_id != st.session_state.last_img_id:
                    st.session_state.last_img_id = file_id
                    try:
                        raw = uploaded_q.read()
                        pil_img = Image.open(io.BytesIO(raw))
                        pil_img.verify()
                        pil_img = Image.open(io.BytesIO(raw)).convert("RGB")
                    except Exception as exc:
                        st.error(f"⚠️ Couldn't open image: `{exc}`")
                        st.stop()
                    scan_slot_q = st.empty()
                    scan_slot_q.markdown(
                        """<div class="scan-container"><div class="scan-overlay"></div><div class="scan-label">🔍&nbsp; Scanning for objects…</div></div>""",
                        unsafe_allow_html=True,
                    )
                    try:
                        annotated_bgr, detections = run_inference(model, pil_img, confidence)
                        annotated_pil = bgr_to_pil(annotated_bgr)
                    except Exception as exc:
                        scan_slot_q.empty()
                        st.error(f"⚠️ Inference failed: `{exc}`")
                        st.stop()
                    scan_slot_q.empty()
                    st.session_state.last_pil_img = pil_img
                    st.session_state.last_annotated_pil = annotated_pil
                    st.session_state.last_detections = detections
                    _handle_detections(detections, quest_board_slot, sound_slot)
            if (
                st.session_state.last_detections is not None
                and st.session_state.last_pil_img is not None
            ):
                img_orig_tab_q, img_det_tab_q = st.tabs(["🖼 Original", "🔍 Detected"])
                with img_orig_tab_q:
                    st.image(st.session_state.last_pil_img, use_container_width=True)
                    st.markdown('<p class="img-caption">Original photo</p>', unsafe_allow_html=True)
                with img_det_tab_q:
                    if st.session_state.last_annotated_pil is not None:
                        st.image(st.session_state.last_annotated_pil, use_container_width=True)
                        st.markdown('<p class="img-caption">YOLO Detections</p>', unsafe_allow_html=True)
                st.markdown("---")
                _render_detections(st.session_state.last_detections, quest_items)
                detected_names_q = [d.class_name for d in st.session_state.last_detections]
                suggestions_q = get_project_suggestions(detected_names_q, max_results=3)
                _render_project_cards(suggestions_q, detected_names_q, context="img_quest")

    with tab_cam:
        if st.session_state.quest_completed:
            st.info("Quest complete! Start a new quest above to keep scanning.")
        else:
            st.markdown("📷 **Point your camera** at objects around the room to find your quest items!")
            if "webcam_running" not in st.session_state:
                st.session_state.webcam_running = False
            c1, c2, _ = st.columns([1, 1, 4])
            with c1:
                start_btn_q = st.button("▶ Start", disabled=st.session_state.webcam_running, use_container_width=True, type="primary", key="cam_start_q")
            with c2:
                stop_btn_q = st.button("⏹ Stop", disabled=not st.session_state.webcam_running, use_container_width=True, key="cam_stop_q")
            if start_btn_q:
                st.session_state.webcam_running = True
                st.rerun()
            if stop_btn_q:
                st.session_state.webcam_running = False
                st.rerun()
            cam_status_q = (
                '<span style="color:#4ade80;font-weight:900">● Live</span>'
                if st.session_state.webcam_running
                else '<span style="color:#ef4444;font-weight:900">● Stopped</span>'
            )
            st.markdown(cam_status_q, unsafe_allow_html=True)
            frame_placeholder_q = st.empty()
            cam_projects_slot_q = st.empty()
            if st.session_state.webcam_running:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    st.error("⚠️ **Webcam not accessible.** Grant camera permission and try again.")
                    st.session_state.webcam_running = False
                    cap.release()
                    st.stop()
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                try:
                    frame_count_q = 0
                    while st.session_state.webcam_running:
                        ret, frame_bgr = cap.read()
                        if not ret:
                            time.sleep(0.1)
                            continue
                        ann_bgr, detections = run_inference(model, frame_bgr, confidence)
                        st.session_state.last_detections = detections
                        _handle_detections(detections, quest_board_slot, sound_slot)
                        ann_rgb = cv2.cvtColor(ann_bgr, cv2.COLOR_BGR2RGB)
                        frame_placeholder_q.image(ann_rgb, channels="RGB", use_container_width=True, caption="Live YOLO Detections")
                        frame_count_q += 1
                        if frame_count_q % 60 == 0 and detections:
                            dn = [d.class_name for d in detections]
                            with cam_projects_slot_q.container():
                                _render_project_cards(get_project_suggestions(dn, max_results=2), dn, context="cam_live")
                        if st.session_state.quest_completed:
                            break
                        time.sleep(0.05)
                finally:
                    cap.release()
            if not st.session_state.webcam_running and st.session_state.last_detections:
                dn = [d.class_name for d in st.session_state.last_detections]
                with cam_projects_slot_q.container():
                    _render_project_cards(get_project_suggestions(dn, max_results=3), dn, context="cam_stopped")

    st.markdown("---")
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
