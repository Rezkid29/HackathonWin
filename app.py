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

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Scavenger Hunt – YOLOVision",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;700;900&display=swap');

    /* ── Base ────────────────────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"] {
        background: #080c18 !important;
        font-family: 'Nunito', sans-serif;
    }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    footer { visibility: hidden; }

    /* ── Game header ─────────────────────────────────────── */
    .game-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(135deg, #0f1628 0%, #141e3d 100%);
        border: 2px solid #1e2d5c;
        border-radius: 18px;
        padding: 14px 24px;
        margin-bottom: 18px;
        gap: 12px;
    }
    .game-title {
        font-family: 'Fredoka One', cursive;
        font-size: 1.9rem;
        background: linear-gradient(90deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        white-space: nowrap;
    }
    .hud-badges {
        display: flex;
        gap: 12px;
        align-items: center;
        flex-wrap: wrap;
    }
    .hud-badge {
        background: #0d1627;
        border: 2px solid #1e2d5c;
        border-radius: 12px;
        padding: 6px 14px;
        font-size: 1rem;
        font-weight: 900;
        color: #e2e8f0;
        white-space: nowrap;
    }
    .hud-badge.streak   { border-color: #f97316; color: #fb923c; }
    .hud-badge.score    { border-color: #a855f7; color: #c084fc; }
    .hud-badge.timer    { border-color: #38bdf8; color: #7dd3fc; }

    /* ── Quest board ─────────────────────────────────────── */
    .quest-board {
        background: linear-gradient(135deg, #0f1628, #141e3d);
        border: 2px solid #1e2d5c;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 18px;
        animation: boardIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
    }
    @keyframes boardIn {
        from { transform: translateY(-30px) scale(0.95); opacity: 0; }
        to   { transform: translateY(0)     scale(1);    opacity: 1; }
    }
    .quest-board-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }
    .quest-board-title {
        font-family: 'Fredoka One', cursive;
        font-size: 1.3rem;
        color: #FFD700;
        letter-spacing: 1px;
    }
    .quest-progress-pill {
        background: #1a2240;
        border: 2px solid #2d3d80;
        border-radius: 20px;
        padding: 4px 16px;
        font-weight: 900;
        font-size: 1rem;
        color: #93c5fd;
    }
    .quest-tiles {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        justify-content: center;
    }
    /* ── Tile flip card ──────────────────────────────────── */
    .quest-tile-wrapper {
        perspective: 900px;
        width: 120px;
        height: 145px;
        flex-shrink: 0;
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
        background: linear-gradient(145deg, #1a2240, #1e2a50);
        border: 2px solid #2d3d80;
        box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    }
    .quest-tile-front:hover {
        border-color: #4c8eff;
        box-shadow: 0 4px 20px rgba(76,142,255,0.2);
    }
    .quest-tile-back {
        background: linear-gradient(145deg, #0d3b1f, #155a2e);
        border: 2px solid #22c55e;
        box-shadow: 0 4px 20px rgba(34,197,94,0.35);
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
        background: #1a2240;
        border-radius: 4px;
        margin-top: 18px;
        overflow: hidden;
    }
    .quest-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #22c55e, #4ade80);
        border-radius: 4px;
        transition: width 0.6s ease;
    }

    /* ── Completion panel ────────────────────────────────── */
    .completion-panel {
        background: linear-gradient(135deg, #0d2a0a, #0f3b12);
        border: 3px solid #22c55e;
        border-radius: 20px;
        padding: 28px 24px;
        text-align: center;
        margin-bottom: 20px;
        animation: completionPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
    }
    @keyframes completionPop {
        from { transform: scale(0.85); opacity: 0; }
        to   { transform: scale(1);    opacity: 1; }
    }
    .completion-title {
        font-family: 'Fredoka One', cursive;
        font-size: 2.4rem;
        color: #FFD700;
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
        background: #0a1f08;
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 10px 18px;
        text-align: center;
    }
    .stat-value { font-size: 1.8rem; font-weight: 900; color: #4ade80; }
    .stat-label { font-size: 0.75rem; color: #86efac; text-transform: uppercase; letter-spacing: 1px; }
    .new-trophy-row {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 12px;
    }
    .new-trophy-tag {
        background: #1a1000;
        border: 2px solid #FFD700;
        border-radius: 10px;
        padding: 6px 14px;
        font-size: 0.9rem;
        font-weight: 900;
        color: #FFD700;
    }

    /* ── Trophy case ─────────────────────────────────────── */
    .trophy-section-title {
        font-family: 'Fredoka One', cursive;
        font-size: 1.2rem;
        color: #FFD700;
        margin-bottom: 12px;
    }
    .trophy-shelf {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 24px;
    }
    .trophy-card {
        background: linear-gradient(145deg, #1a1000, #261800);
        border: 2px solid #b45309;
        border-radius: 12px;
        padding: 10px 16px;
        font-size: 0.9rem;
        font-weight: 700;
        color: #fbbf24;
    }
    .trophy-card.locked {
        background: #0d1120;
        border-color: #1e2d5c;
        color: #374151;
    }

    /* ── Detection result cards ──────────────────────────── */
    .det-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0f1628;
        border: 1px solid #1e2d5c;
        border-radius: 10px;
        padding: 8px 14px;
        margin-bottom: 6px;
    }
    .det-card.quest-hit { border-color: #22c55e; background: #0a1f08; }
    .det-label { font-weight: 700; color: #e2e8f0; font-size: 0.9rem; }
    .det-conf  { font-size: 0.82rem; color: #4ade80; font-weight: 900; }
    .det-bonus { font-size: 0.75rem; color: #6366f1; font-weight: 700; }

    /* ── Settings expander ───────────────────────────────── */
    details summary { color: #94a3b8 !important; font-size: 0.9rem; }

    /* ── Misc helpers ────────────────────────────────────── */
    .img-caption { text-align: center; color: #64748b; font-size: 0.82rem; margin-top: 4px; }
    div[data-testid="stTabs"] button { font-family: 'Nunito', sans-serif; font-weight: 900; }
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
        timer_html = f'<span class="hud-badge timer">⏱ {mins}:{secs:02d}</span>'

    st.markdown(
        f"""
        <div class="game-header">
            <span class="game-title">🔍 Scavenger Hunt</span>
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


def _render_trophy_case(trophies: list[str]) -> None:
    st.markdown('<div class="trophy-section-title">🏆 Trophy Case</div>', unsafe_allow_html=True)
    cards = ""
    for t in _ALL_TROPHIES:
        if t in trophies:
            cards += f'<div class="trophy-card">{t}</div>'
        else:
            cards += f'<div class="trophy-card locked">🔒 ???</div>'
    st.markdown(f'<div class="trophy-shelf">{cards}</div>', unsafe_allow_html=True)


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

    # Background gradient approximation
    for y in range(H):
        r = int(8  + (14 - 8)  * y / H)
        g = int(12 + (24 - 12) * y / H)
        b = int(23 + (55 - 23) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Title
    draw.text((W // 2, 32), "🔍 SCAVENGER HUNT", font=fnt_big, fill="#FFD700", anchor="mm")

    # Items grid
    x_start, y_start = 60, 90
    col_w = 180
    for i, item in enumerate(items):
        col, row = i % 3, i // 3
        x = x_start + col * col_w
        y = y_start + row * 72
        tick = "✅" if item in found else "⬜"
        emoji = get_emoji(item)
        draw.text((x, y),      f"{tick} {emoji} {item.title()}", font=fnt_med, fill="#e2e8f0")

    # Stats row
    y_stats = 268
    draw.rectangle([(40, y_stats - 8), (W - 40, y_stats + 52)], fill="#0f1628", outline="#1e2d5c", width=2)
    if comp_time is not None:
        mins, secs = divmod(int(comp_time), 60)
        t_str = f"⏱ {mins}m {secs}s" if mins else f"⏱ {secs}s"
    else:
        t_str = "⏱ In progress"
    draw.text((80,  y_stats + 18), t_str,         font=fnt_med, fill="#7dd3fc", anchor="lm")
    draw.text((W // 2, y_stats + 18), f"⭐ {score} pts", font=fnt_med, fill="#c084fc", anchor="mm")
    n_found = len(found & set(items))
    draw.text((W - 80, y_stats + 18), f"{n_found}/5 found", font=fnt_med, fill="#4ade80", anchor="rm")

    # Watermark
    draw.text((W // 2, H - 18), "Made with YOLOVision 🔍", font=fnt_sm, fill="#334155", anchor="mm")

    return img


# ── New quest helper ──────────────────────────────────────────────────────────

def _new_quest() -> None:
    st.session_state.quest_items       = generate_quest()
    st.session_state.quest_found       = set()
    st.session_state.quest_start_time  = time.time()
    st.session_state.quest_completed   = False
    st.session_state.quest_comp_time   = None
    st.session_state.new_trophies      = []
    st.session_state.last_img_id       = None
    st.session_state.pending_sound     = "whoosh"


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

    # Refresh board immediately via placeholder
    with quest_board_slot.container():
        st.markdown(
            _quest_board_html(quest_items, st.session_state.quest_found),
            unsafe_allow_html=True,
        )

    # Quest completion
    all_found = set(quest_items) <= st.session_state.quest_found
    if all_found and not st.session_state.quest_completed:
        st.session_state.quest_completed  = True
        comp_time = time.time() - st.session_state.quest_start_time
        st.session_state.quest_comp_time  = comp_time

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

    quest_hits    = [d for d in detections if d.class_name in quest_items]
    bonus_finds   = [d for d in detections if d.class_name not in quest_items]

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


# ════════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════════

progress     = load_progress()
quest_items  = st.session_state.quest_items
quest_found  = st.session_state.quest_found

# ── Header ────────────────────────────────────────────────────────────────────
_render_header(
    streak=progress.get("streak", 0),
    score=st.session_state.session_score,
    quest_start=st.session_state.quest_start_time,
    completed=st.session_state.quest_completed,
)

# ── Quest board (placeholder so we can update it in-place later) ──────────────
quest_board_slot = st.empty()
sound_slot       = st.empty()

with quest_board_slot.container():
    st.markdown(_quest_board_html(quest_items, quest_found), unsafe_allow_html=True)

# ── Completion panel + new quest button ───────────────────────────────────────
if st.session_state.quest_completed:
    comp_time = st.session_state.quest_comp_time or 0.0
    speed_run = comp_time <= 60
    _render_completion(
        comp_time=comp_time,
        score=st.session_state.session_score,
        new_trophies=st.session_state.new_trophies,
        speed_run=speed_run,
    )

    col_btn, col_share, _ = st.columns([1.2, 1.2, 3])
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

# ── Pending sound (plays after page renders) ──────────────────────────────────
if st.session_state.pending_sound:
    _inject_sound(st.session_state.pending_sound)
    st.session_state.pending_sound = None

# ── Scanner settings ──────────────────────────────────────────────────────────
with st.expander("⚙️ Scanner Settings", expanded=False):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        confidence = st.slider("Confidence", 0.10, 1.00, 0.45, 0.05)
    with col_s2:
        model_choice = st.selectbox(
            "YOLO Variant",
            ["yolo26n.pt", "yolo26s.pt", "yolo26m.pt", "yolo26l.pt", "yolo26x.pt"],
            index=0,
            help="n = fastest · x = most accurate",
        )

model = load_model(model_choice)

# ── Detection tabs ────────────────────────────────────────────────────────────
tab_img, tab_cam = st.tabs(["📸 Upload a Photo", "📷 Live Camera"])


# ══ TAB 1 – Image Upload ══════════════════════════════════════════════════════

with tab_img:
    if st.session_state.quest_completed:
        st.info("Quest complete! Start a new quest above to keep scanning.")
    else:
        st.markdown(
            "📸 **Take or upload a photo** of anything around you — "
            "the scanner will find your quest objects automatically!"
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
                    raw = uploaded.read()
                    pil_img = Image.open(io.BytesIO(raw))
                    pil_img.verify()
                    pil_img = Image.open(io.BytesIO(raw)).convert("RGB")
                except Exception as exc:
                    st.error(f"⚠️ Couldn't open image: `{exc}`")
                    st.stop()

                with st.spinner("🔍 Scanning for objects…"):
                    try:
                        annotated_bgr, detections = run_inference(model, pil_img, confidence)
                        annotated_pil = bgr_to_pil(annotated_bgr)
                    except Exception as exc:
                        st.error(f"⚠️ Inference failed: `{exc}`")
                        st.stop()

                st.session_state.last_detections = detections
                _handle_detections(detections, quest_board_slot, sound_slot)

            if st.session_state.last_detections is not None:
                col_orig, col_det = st.columns(2, gap="medium")
                with col_orig:
                    st.image(pil_img, use_container_width=True)
                    st.markdown('<p class="img-caption">Original</p>', unsafe_allow_html=True)
                with col_det:
                    try:
                        ann_bgr, _ = run_inference(model, pil_img, confidence)
                        st.image(bgr_to_pil(ann_bgr), use_container_width=True)
                    except Exception:
                        pass
                    st.markdown('<p class="img-caption">YOLO Detections</p>', unsafe_allow_html=True)

                st.markdown("---")
                _render_detections(st.session_state.last_detections, quest_items)


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

        frame_placeholder = st.empty()

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

                    if st.session_state.quest_completed:
                        break

                    time.sleep(0.05)
            finally:
                cap.release()

# ── Trophy case ───────────────────────────────────────────────────────────────
st.markdown("---")
progress = load_progress()
_render_trophy_case(progress.get("trophies", []))

# ── Footer ────────────────────────────────────────────────────────────────────
best = progress.get("best_time")
best_str = (
    f"{int(best // 60)}m {int(best % 60)}s" if best and best >= 60 else
    f"{int(best)}s" if best else "—"
)
total_q = progress.get("total_quests_completed", 0)
st.markdown(
    f"<p style='text-align:center;color:#334155;font-size:0.8rem;margin-top:8px;'>"
    f"Quests completed: {total_q} · Best time: {best_str} · "
    f"<a href='https://docs.ultralytics.com/models/yolo26/' "
    f"style='color:#334155'>YOLO26</a></p>",
    unsafe_allow_html=True,
)
