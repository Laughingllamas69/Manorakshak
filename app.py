"""
===============================================================================
 ManoRakshak (मनोरक्षक) — Mental Health & Wellness Support Portal
 For Police Personnel & Armed Forces
===============================================================================

WHAT THIS FILE IS:
A single-file Streamlit application. Frontend + backend + database logic
all live here on purpose, so the whole prototype can be run with one
command and deployed with zero build steps.

FOR NON-PROGRAMMERS WHO WANT TO EDIT THIS APP:
- All screener questions live in the QUESTIONS list (search "SECTION 2").
- All on-screen text / labels live near the top in the TEXT dictionary
  and in the SECTION headers below — edit the strings, not the logic.
- Helpline numbers / resources live in the RESOURCES section.
- To plug in your Gemini API key, see "SECTION 4: AI COMPANION" below.
===============================================================================
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime

import pandas as pd
import streamlit as st

# Gemini SDK is optional at import time — the app must still run (in
# "offline template mode") even if the package or API key isn't set up yet.
try:
    import google.generativeai as genai
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    GEMINI_SDK_AVAILABLE = False


# ==============================================================================
# SECTION 0: APP-WIDE CONFIGURATION
# ==============================================================================

DB_PATH = "manorakshak.db"

APP_TITLE = "ManoRakshak | मनोरक्षक"
APP_SUBTITLE = "Confidential Mental Wellness Support for Police & Armed Forces Personnel"

# Departments shown at login — used ONLY for anonymized unit-level admin
# analytics. Edit this list to match your organization's structure.
DEPARTMENTS = [
    "State Police", "CRPF", "BSF", "CISF", "ITBP", "SSB",
    "Indian Army", "Indian Navy", "Indian Air Force", "Other / Prefer not to say",
]

# Change this before any real deployment. Best practice: set it via
# st.secrets["ADMIN_PASSWORD"] instead of hardcoding it here.
DEFAULT_ADMIN_PASSWORD = "manorakshak_admin"

# Confidential crisis resources shown throughout the app.
HELPLINES = [
    {"name": "Tele-MANAS (Govt. of India Mental Health Helpline)", "number": "14416"},
    {"name": "KIRAN Mental Health Helpline (Ministry of Social Justice)", "number": "1800-599-0019"},
    {"name": "iCall Psychosocial Helpline (TISS)", "number": "9152987821"},
    {"name": "Department In-house Peer Support Cell", "number": "Contact your unit welfare officer"},
]


# ==============================================================================
# SECTION 1: DATABASE LAYER (SQLite)
# ==============================================================================
# Everything the app persists lives in one table. Keeping it flat and simple
# makes it easy for a non-DBA to inspect with any SQLite viewer.

def get_connection():
    """Open a fresh connection. SQLite connections are cheap, so we open
    one per operation rather than keeping a long-lived global connection —
    this avoids thread-safety issues inside Streamlit's execution model."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def init_db():
    """Create the assessments table if it does not already exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            department TEXT,
            timestamp TEXT NOT NULL,
            total_score INTEGER NOT NULL,
            category TEXT NOT NULL,
            responses TEXT,
            ai_recommendation TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_assessment(user_id, department, total_score, category, responses_dict, ai_text):
    """Persist one completed assessment."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO assessments (user_id, department, timestamp, total_score, category, responses, ai_recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            department,
            datetime.now().isoformat(timespec="seconds"),
            total_score,
            category,
            json.dumps(responses_dict, ensure_ascii=False),
            ai_text,
        ),
    )
    conn.commit()
    conn.close()


def get_user_history(user_id):
    """Return all past assessments for one anonymous user, oldest first."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM assessments WHERE user_id = ? ORDER BY timestamp ASC",
        conn,
        params=(user_id,),
    )
    conn.close()
    return df


def get_all_assessments():
    """Return every assessment in the system — used only by the admin panel."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM assessments ORDER BY timestamp ASC", conn)
    conn.close()
    return df


def hash_pseudonym(raw_id: str) -> str:
    """Turn whatever the officer types (badge number, nickname, etc.) into
    a stable but non-reversible pseudonym for storage. This means even the
    admin panel / raw database never stores the literal badge number."""
    raw_id = raw_id.strip().lower()
    return "OFC-" + hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:10].upper()


# ==============================================================================
# SECTION 2: THE SCREENER — QUESTIONS & SCORING LOGIC
# ==============================================================================
# This adapts the clinically standardized PHQ-4 (ultra-brief depression /
# anxiety screener) and adds duty-specific items inspired by occupational
# stress and Brief-COPE literature, tailored to law-enforcement / armed
# forces realities: shift fatigue, traumatic incident exposure, isolation
# from family, hypervigilance, and emotional suppression.
#
# NON-PROGRAMMERS: to add/remove/edit a question, just edit this list.
# Each question is answered on the same 0–3 scale, defined in ANSWER_SCALE.

ANSWER_SCALE = [
    "Not at all",
    "Several days",
    "More than half the days",
    "Nearly every day",
]

QUESTIONS = [
    # --- Adapted PHQ-4 core items (depression / anxiety) ---
    {
        "id": "q1",
        "text": "Little interest or pleasure in doing things you'd normally enjoy, on or off duty",
        "domain": "Mood",
    },
    {
        "id": "q2",
        "text": "Feeling down, low, or hopeless",
        "domain": "Mood",
    },
    {
        "id": "q3",
        "text": "Feeling nervous, anxious, or 'on edge'",
        "domain": "Anxiety",
    },
    {
        "id": "q4",
        "text": "Not being able to stop or control worrying",
        "domain": "Anxiety",
    },
    # --- Duty-specific items ---
    {
        "id": "q5",
        "text": "Trouble falling or staying asleep due to shift timings or a racing mind",
        "domain": "Sleep / Fatigue",
    },
    {
        "id": "q6",
        "text": "Unwanted memories, flashbacks, or distress linked to an incident on duty",
        "domain": "Trauma Exposure",
    },
    {
        "id": "q7",
        "text": "Feeling isolated or disconnected from family and friends because of work",
        "domain": "Isolation",
    },
    {
        "id": "q8",
        "text": "Feeling unusually irritable, quick to anger, or constantly 'on guard' even off duty",
        "domain": "Hypervigilance",
    },
    {
        "id": "q9",
        "text": "Feeling emotionally numb or finding it hard to feel positive emotions",
        "domain": "Emotional Suppression",
    },
    {
        "id": "q10",
        "text": "Physical exhaustion affecting your alertness, focus, or performance on duty",
        "domain": "Burnout",
    },
]

MAX_SCORE = len(QUESTIONS) * 3  # 30

# Category thresholds — tune these if your organization uses different cutoffs.
SCORE_CATEGORIES = [
    (0, 7, "Low Stress", "🟢"),
    (8, 14, "Moderate Fatigue", "🟡"),
    (15, 21, "High Burnout", "🟠"),
    (22, MAX_SCORE, "Critical Distress", "🔴"),
]


def score_to_category(total_score: int):
    """Map a total numeric score to a (label, emoji) category tuple."""
    for low, high, label, emoji in SCORE_CATEGORIES:
        if low <= total_score <= high:
            return label, emoji
    return "Unknown", "⚪"


# ==============================================================================
# SECTION 3: STATIC WELLNESS RESOURCES (shown on the Dashboard)
# ==============================================================================

SOP_RESETS = [
    "**Box Breathing (Tactical Reset):** Inhale 4s → Hold 4s → Exhale 4s → Hold 4s. Repeat 4–6 cycles before/after a high-stress call.",
    "**Post-Shift Decompression:** Take 10 minutes in the vehicle/locker room before driving home — change out of uniform mentally, not just physically.",
    "**5-4-3-2-1 Grounding:** Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste — use during acute stress spikes.",
    "**Sleep Hygiene for Rotating Shifts:** Blackout curtains, no screens 30 min before sleep, consistent wind-down ritual regardless of shift time.",
    "**Peer Check-In Protocol:** After a critical incident, a structured 10-minute peer debrief within 24–72 hours significantly reduces long-term impact.",
]


# ==============================================================================
# SECTION 4: AI OFFICER CARE COMPANION — "Rakshak Sahayak" (Gemini Integration)
# ==============================================================================
# HOW TO PLUG IN YOUR GEMINI API KEY:
#   Option A (recommended for Streamlit Cloud):
#     Create a file .streamlit/secrets.toml with:
#         GEMINI_API_KEY = "your-key-here"
#   Option B (local dev): set an environment variable before running:
#         export GEMINI_API_KEY="your-key-here"      (Mac/Linux)
#         set GEMINI_API_KEY="your-key-here"          (Windows)
#
# If no key is found, the app automatically falls back to a template-based
# "offline mode" response so the demo still works end-to-end.

def get_gemini_api_key():
    """Look for the API key in Streamlit secrets first, then env vars."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass  # st.secrets raises if no secrets.toml exists at all — that's fine
    return os.environ.get("GEMINI_API_KEY", "")


RAKSHAK_SAHAYAK_PERSONA = """
You are "Rakshak Sahayak", a warm, confidential, trauma-informed debriefing
companion built specifically for Indian police and armed forces personnel.

Your tone: respectful, calm, non-clinical, never condescending. You address
the officer as a professional who serves under real operational stress —
never as a "patient". You NEVER diagnose. You validate their service and
their feelings, then offer 2-3 concrete, actionable grounding or
tactical-reset techniques (e.g. box breathing, grounding exercises,
post-shift decompression routines). Keep the response under 220 words,
in plain conversational English (a few Hindi words like "himmat" or
"seva" are welcome if natural, but do not overdo it).

If the distress category is "Critical Distress", gently and non-alarmingly
encourage them to reach out to a confidential helpline or their peer
support contact, and mention that reaching out is a sign of operational
readiness, not weakness. Do not be preachy about this — one sentence is enough.
"""


def build_gemini_prompt(category: str, responses: dict) -> str:
    """Construct the prompt sent to Gemini, summarizing which duty-related
    challenges scored highest so the response feels specifically tailored."""
    # Identify the officer's top 3 highest-scoring (most concerning) domains
    scored_items = sorted(responses.items(), key=lambda kv: kv[1]["score"], reverse=True)
    top_concerns = scored_items[:3]
    concerns_text = "\n".join(
        f"- {item['domain']}: \"{item['question']}\" — reported as \"{ANSWER_SCALE[item['score']]}\""
        for _, item in top_concerns
    )

    prompt = f"""{RAKSHAK_SAHAYAK_PERSONA}

An officer has just completed a confidential wellness screener.
Overall result category: {category}

Their top reported challenge areas:
{concerns_text}

Write their confidential debrief now, addressed directly to them ("you").
"""
    return prompt


def get_ai_debrief(category: str, responses: dict) -> str:
    """Call Gemini for a personalized debrief. Falls back to a static,
    still-useful template if the SDK or API key is unavailable, so the
    prototype always produces a complete end-to-end experience."""
    api_key = get_gemini_api_key()

    if GEMINI_SDK_AVAILABLE and api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-3.6-flash")
            prompt = build_gemini_prompt(category, responses)
            result = model.generate_content(prompt)
            return result.text.strip()
        except Exception as e:
            return _offline_debrief(category) + f"\n\n*(AI companion note: live response unavailable — {e})*"

    return _offline_debrief(category)


def _offline_debrief(category: str) -> str:
    """Template-based fallback response, used when no Gemini API key is
    configured yet. Keeps the demo fully functional out of the box."""
    templates = {
        "Low Stress": (
            "Your readings look steady today — that's good, and it's worth "
            "acknowledging the discipline it takes to maintain that under duty "
            "pressure. Keep your routine: box breathing before high-stress calls, "
            "consistent sleep, and regular check-ins with your peers. Steady as she goes."
        ),
        "Moderate Fatigue": (
            "What you're carrying is real — shift work and duty pressure add up "
            "even when everything looks fine on the surface. Try box breathing "
            "(4s in, 4s hold, 4s out, 4s hold) before and after high-intensity calls, "
            "and protect a wind-down window before sleep. Small resets, done "
            "consistently, prevent bigger dips later."
        ),
        "High Burnout": (
            "Thank you for your service, and thank you for being honest here — "
            "that honesty takes real courage. What you're experiencing sounds like "
            "genuine burnout, not weakness. Try the 5-4-3-2-1 grounding technique "
            "during acute moments, and consider a structured peer check-in this week. "
            "You don't have to carry this alone."
        ),
        "Critical Distress": (
            "First — thank you for trusting this space with something difficult. "
            "What you're describing deserves real support, not just a breathing "
            "exercise. Please consider reaching out to Tele-MANAS (14416) or the "
            "KIRAN helpline (1800-599-0019) today — confidentially, and on your terms. "
            "Reaching out is operational readiness, not a weakness. You've carried a lot; "
            "you don't have to carry it alone."
        ),
    }
    return templates.get(category, "Thank you for completing your check-in. Take a moment to breathe.")


# ==============================================================================
# SECTION 5: STREAMLIT APP — PAGE CONFIG & SESSION STATE
# ==============================================================================

st.set_page_config(
    page_title="ManoRakshak",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "department" not in st.session_state:
    st.session_state.department = ""


# ==============================================================================
# SECTION 6: SIDEBAR — ANONYMOUS / PSEUDONYM LOGIN
# ==============================================================================

with st.sidebar:
    st.markdown("## 🛡️ ManoRakshak")
    st.caption(APP_SUBTITLE)
    st.divider()

    if not st.session_state.logged_in:
        st.markdown("### 🔐 Confidential Check-In")
        st.caption(
            "Use a badge number, service number, or any pseudonym you like. "
            "Your identity is one-way hashed before storage — nobody, "
            "including admins, can reverse it back to your real identity."
        )
        raw_id = st.text_input("Badge Number / Pseudonym", placeholder="e.g. Falcon-07")
        dept = st.selectbox("Department / Force", DEPARTMENTS)

        if st.button("🔓 Enter Confidentially", use_container_width=True, type="primary"):
            if raw_id.strip():
                st.session_state.user_id = hash_pseudonym(raw_id)
                st.session_state.department = dept
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.warning("Please enter a badge number or pseudonym to continue.")
    else:
        st.success(f"Signed in as **{st.session_state.user_id}**")
        st.caption(f"Department: {st.session_state.department}")
        if st.button("🚪 End Session", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = ""
            st.session_state.department = ""
            st.rerun()

    st.divider()
    st.markdown("#### 🚨 In Crisis Right Now?")
    for h in HELPLINES:
        st.markdown(f"**{h['name']}**  \n📞 {h['number']}")


# ==============================================================================
# SECTION 7: MAIN AREA
# ==============================================================================

st.title("🛡️ ManoRakshak (मनोरक्षक)")
st.caption(APP_SUBTITLE)

if not st.session_state.logged_in:
    st.info("👈 Please check in using the sidebar (a pseudonym is completely fine) to begin.")
    st.markdown(
        """
        ### About ManoRakshak
        ManoRakshak is a confidential, stigma-free wellness check-in tool built for
        police and armed forces personnel. It offers:
        - A **2-minute standardized wellness screener**, adapted for duty-related stress
        - An **AI debriefing companion** offering grounding techniques and support
        - A **personal wellness dashboard** to track your trend over time
        - Direct access to **national crisis helplines**

        No real names are ever required. Your privacy is the foundation of this tool.
        """
    )
    st.stop()

tab_assess, tab_dashboard, tab_admin = st.tabs(
    ["📝 Wellness Screener", "📊 My Dashboard & Resources", "🔐 Command Analytics (Admin)"]
)


# ------------------------------------------------------------------------------
# TAB 1: THE SCREENER + AI DEBRIEF
# ------------------------------------------------------------------------------
with tab_assess:
    st.subheader("Confidential Duty Wellness Check-In")
    st.caption(
        "Over the **last 2 weeks**, how often have you been bothered by any of "
        "the following? There are no right or wrong answers — answer honestly."
    )

    with st.form("screener_form"):
        responses = {}
        for q in QUESTIONS:
            answer_idx = st.radio(
                f"**{q['text']}**",
                options=list(range(4)),
                format_func=lambda i: ANSWER_SCALE[i],
                horizontal=True,
                key=f"radio_{q['id']}",
                index=None,
            )
            responses[q["id"]] = {
                "question": q["text"],
                "domain": q["domain"],
                "score": answer_idx,
            }

        submitted = st.form_submit_button("✅ Submit Confidential Check-In", type="primary", use_container_width=True)

    if submitted:
        # Validate every question was answered
        unanswered = [q["text"] for q in QUESTIONS if responses[q["id"]]["score"] is None]
        if unanswered:
            st.error("Please answer every question before submitting. You've missed: " + "; ".join(unanswered))
        else:
            total_score = sum(item["score"] for item in responses.values())
            category, emoji = score_to_category(total_score)

            with st.spinner("Rakshak Sahayak is preparing your confidential debrief..."):
                ai_text = get_ai_debrief(category, responses)

            save_assessment(
                st.session_state.user_id,
                st.session_state.department,
                total_score,
                category,
                responses,
                ai_text,
            )

            st.divider()
            st.markdown(f"## {emoji} Result: **{category}**")
            st.progress(min(total_score / MAX_SCORE, 1.0))
            st.caption(f"Score: {total_score} / {MAX_SCORE}")

            st.markdown("### 🤝 A Message from Rakshak Sahayak")
            st.info(ai_text)

            if category == "Critical Distress":
                st.error(
                    "⚠️ Your responses suggest you may be going through a significant "
                    "amount of distress. Please consider reaching out to a confidential "
                    "helpline listed in the sidebar, or your unit's peer support contact. "
                    "You do not have to face this alone."
                )

            st.success("This check-in has been saved to your private wellness trend below (see 'My Dashboard' tab).")


# ------------------------------------------------------------------------------
# TAB 2: PERSONAL DASHBOARD + RESOURCE BANK
# ------------------------------------------------------------------------------
with tab_dashboard:
    st.subheader("📈 Your Wellness Trend")

    history_df = get_user_history(st.session_state.user_id)

    if history_df.empty:
        st.info("No check-ins yet. Complete a screener in the first tab to start your trend.")
    else:
        history_df["timestamp"] = pd.to_datetime(history_df["timestamp"])
        chart_df = history_df.set_index("timestamp")[["total_score"]].rename(
            columns={"total_score": "Stress Score"}
        )
        st.line_chart(chart_df, height=300)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Check-ins", len(history_df))
        col2.metric("Latest Score", int(history_df.iloc[-1]["total_score"]), help=f"out of {MAX_SCORE}")
        col3.metric("Latest Category", history_df.iloc[-1]["category"])

        with st.expander("📋 View full check-in history"):
            display_df = history_df[["timestamp", "total_score", "category"]].rename(
                columns={"timestamp": "Date/Time", "total_score": "Score", "category": "Category"}
            )
            st.dataframe(display_df.sort_values("Date/Time", ascending=False), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🧰 Shift Reset Resource Bank")
    for tip in SOP_RESETS:
        st.markdown(f"- {tip}")

    st.divider()
    st.subheader("📞 Crisis & Peer Support Directory")
    hc1, hc2 = st.columns(2)
    for i, h in enumerate(HELPLINES):
        col = hc1 if i % 2 == 0 else hc2
        col.markdown(f"**{h['name']}**  \n📞 `{h['number']}`")


# ------------------------------------------------------------------------------
# TAB 3: ADMIN / COMMAND-LEVEL ANALYTICS (password protected, fully anonymized)
# ------------------------------------------------------------------------------
with tab_admin:
    st.subheader("🔐 Command-Level Wellness Analytics")
    st.caption(
        "Password-protected, aggregate-only view. Individual identities are "
        "never shown here — only unit-level patterns, to support proactive "
        "welfare planning without compromising any single officer's privacy."
    )

    admin_password = st.text_input("Admin Password", type="password", key="admin_pw")

    # Best practice: set ADMIN_PASSWORD in st.secrets rather than relying on
    # the hardcoded default below. Change DEFAULT_ADMIN_PASSWORD before any
    # real deployment.
    try:
        expected_password = st.secrets.get("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
    except Exception:
        expected_password = DEFAULT_ADMIN_PASSWORD

    if admin_password == "":
        st.info("Enter the admin password to view aggregate analytics.")
    elif admin_password != expected_password:
        st.error("Incorrect password.")
    else:
        all_df = get_all_assessments()

        if all_df.empty:
            st.info("No screenings recorded yet.")
        else:
            st.success("Access granted — showing anonymized aggregate data only.")

            total_screenings = len(all_df)
            unique_officers = all_df["user_id"].nunique()
            high_risk_pct = (
                all_df["category"].isin(["High Burnout", "Critical Distress"]).mean() * 100
            )
            low_risk_pct = (all_df["category"] == "Low Stress").mean() * 100

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Screenings", total_screenings)
            m2.metric("Unique Anonymous Officers", unique_officers)
            m3.metric("% High Burnout / Critical", f"{high_risk_pct:.1f}%")
            m4.metric("% Low Stress", f"{low_risk_pct:.1f}%")

            st.divider()
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("#### Category Distribution")
                cat_counts = all_df["category"].value_counts()
                st.bar_chart(cat_counts)

            with col_b:
                st.markdown("#### Average Score by Department")
                dept_avg = all_df.groupby("department")["total_score"].mean().sort_values(ascending=False)
                st.bar_chart(dept_avg)

            st.divider()
            st.markdown("#### Screenings Over Time")
            all_df["timestamp"] = pd.to_datetime(all_df["timestamp"])
            all_df["date"] = all_df["timestamp"].dt.date
            daily_counts = all_df.groupby("date").size()
            st.line_chart(daily_counts)

            with st.expander("📋 Raw anonymized records (no names, badge numbers hashed)"):
                safe_cols = ["user_id", "department", "timestamp", "total_score", "category"]
                st.dataframe(all_df[safe_cols], use_container_width=True, hide_index=True)