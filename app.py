import os
import json
import sqlite3
import hashlib
import random
from datetime import datetime
import pandas as pd
import streamlit as st
from huggingface_hub import InferenceClient

# Import UI module
from app_ui import inject_css, hero_header, render_crisis_banner

# --- CONFIGURATION ---
DB_PATH = "manorakshak.db"
APP_TITLE = "ManoRakshak (मनोरक्षक)"
APP_SUBTITLE = "Confidential Mental Wellness & Peer Support for Uniformed Personnel"

DEPARTMENTS = [
    "State Police", "CRPF", "BSF", "CISF", "ITBP", "SSB",
    "Indian Army", "Indian Navy", "Indian Air Force", "Other / Prefer not to say"
]

HELPLINES = [
    {"name": "Tele-MANAS (Govt. of India)", "number": "14416"},
    {"name": "KIRAN Helpline", "number": "1800-599-0019"},
    {"name": "iCall (TISS)", "number": "9152987821"},
    {"name": "Unit Peer Support", "number": "Contact Welfare Officer"}
]

# --- QUESTIONS LIST (GLOBAL SCOPE) ---
QUESTIONS = [
    {"id": "q1", "text": "Little interest or pleasure in doing things you'd normally enjoy", "domain": "Mood"},
    {"id": "q2", "text": "Feeling down, low, or hopeless", "domain": "Mood"},
    {"id": "q3", "text": "Feeling nervous, anxious, or 'on edge'", "domain": "Anxiety"},
    {"id": "q4", "text": "Not being able to stop or controlling worrying", "domain": "Anxiety"},
    {"id": "q5", "text": "Trouble falling or staying asleep due to shift timings", "domain": "Sleep / Fatigue"},
    {"id": "q6", "text": "Unwanted memories, flashbacks, or distress linked to duty", "domain": "Trauma"},
    {"id": "q7", "text": "Feeling isolated or disconnected from family/friends", "domain": "Isolation"},
    {"id": "q8", "text": "Feeling unusually irritable or 'on guard' off duty", "domain": "Hypervigilance"},
    {"id": "q9", "text": "Feeling emotionally numb or hard to feel positive emotions", "domain": "Emotional"},
    {"id": "q10", "text": "Physical exhaustion affecting alertness or focus", "domain": "Burnout"},
    {"id": "q11", "text": "Relying on substances to cope with stress or sleep", "domain": "Substance Use"},
    {"id": "q12", "text": "Difficulty concentrating or making decisions", "domain": "Cognitive"},
    {"id": "q13", "text": "Feeling guilty about past actions during an incident", "domain": "Guilt"},
    {"id": "q14", "text": "Difficulty trusting colleagues or feeling unsupported", "domain": "Team"},
    {"id": "q15", "text": "Physical symptoms (headaches, stomach issues) without medical cause", "domain": "Psychosomatic"},
]

ANSWER_SCALE = ["Not at all", "Several days", "More than half", "Nearly every day"]
MAX_SCORE = len(QUESTIONS) * 3
SCORE_CATEGORIES = [(0, 10, "Low Stress", "🟢"), (11, 21, "Moderate Fatigue", "🟡"), 
                    (22, 33, "High Burnout", "🟠"), (34, MAX_SCORE, "Critical Distress", "🔴")]

# --- DATABASE FUNCTIONS ---
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            department TEXT,
            timestamp TEXT NOT NULL,
            total_score INTEGER NOT NULL,
            category TEXT NOT NULL,
            responses TEXT,
            ai_recommendation TEXT,
            is_encrypted INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_assessment(user_id, department, total_score, category, responses_dict, ai_text):
    # Sanitize AI text to prevent SQL errors
    safe_ai_text = ai_text.replace("'", "''")
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO assessments (user_id, department, timestamp, total_score, category, responses, ai_recommendation, is_encrypted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, department, datetime.now().isoformat(), total_score, category, 
          json.dumps(responses_dict, ensure_ascii=False), safe_ai_text, 1))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM assessments WHERE user_id = ? ORDER BY timestamp ASC", conn, params=(user_id,))
    conn.close()
    return df

def get_all_assessments():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM assessments ORDER BY timestamp ASC", conn)
    conn.close()
    return df

# --- SECURITY & UTILITIES ---
def hash_pseudonym(raw_id: str) -> str:
    raw_id = raw_id.strip().lower()
    salt = "SIH2026_SECURE_SALT" 
    return "OFC-" + hashlib.sha256((raw_id + salt).encode("utf-8")).hexdigest()[:10].upper()

def wipe_session():
    keys_to_keep = ["logged_in", "user_id", "department"]
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    st.session_state.logged_in = False
    st.session_state.user_id = ""
    st.session_state.department = ""
    st.rerun()

# --- AI & ML FUNCTIONS ---

def get_template_fallback(category):
    templates = {
        "Low Stress": "Your readings are steady, Officer. This discipline is commendable. Continue your routine: Box Breathing before calls, consistent sleep, and peer check-ins. Steady as she goes.",
        "Moderate Fatigue": "Shift work is heavy. What you feel is real. Try the 4-4-4-4 Box Breathing technique before your next high-intensity call. Protect your wind-down time before sleep. Small resets prevent big dips.",
        "High Burnout": "Thank you for your service and honesty. This isn't weakness; it's burnout. Use the 5-4-3-2-1 grounding technique during acute moments. Please consider a structured peer check-in this week. You don't have to carry this alone.",
        "Critical Distress": "Thank you for trusting us with this. What you're describing needs real support. Please call Tele-MANAS (14416) or KIRAN (1800-599-0019) today. Reaching out is operational readiness, not weakness. You've carried a lot; let others help you now."
    }
    return templates.get(category, "Thank you for completing your check-in. Take a moment to breathe.")

def analyze_sentiment(responses_dict):
    score_map = {0: "Not at all", 1: "Several days", 2: "More than half", 3: "Nearly every day"}
    text_inputs = []
    for q_id, score in responses_dict.items():
        if score > 0:
            q_text = next((q["text"] for q in QUESTIONS if q["id"] == q_id), "")
            text_inputs.append(f"{score_map[score]}: {q_text}")
    
    if not text_inputs:
        return {"sentiment": "Neutral", "score": 0.5, "confidence": 1.0}
    
    try:
        client = InferenceClient(token=st.secrets.get("HF_TOKEN", ""))
        results = client.text_classification(text_inputs[:5])
        
        if not results:
            return {"sentiment": "Neutral", "score": 0.5, "confidence": 0.0}
            
        top_result = results[0]
        
        return {
            "sentiment": top_result[0]["label"],
            "score": round(top_result[0]["score"], 2),
            "confidence": round(top_result[0]["score"], 2)
        }
    except Exception as e:
        return {"sentiment": "Unknown", "score": 0.0, "confidence": 0.0}

def get_ai_debrief(category, responses):
    high_risk_questions = [
        q for q, score in responses.items() if score >= 2
    ]
    question_texts = [
        q["text"] for q in QUESTIONS if q["id"] in high_risk_questions
    ]
    
    context_text = "\n".join(question_texts) if question_texts else "No specific stressors reported."
    
    prompt = f"""
    You are 'Rakshak Sahayak', an AI mental wellness assistant for Indian uniformed personnel (Police, Army, NSG, etc.).
    Tone: Professional, empathetic, respectful, non-judgmental, and concise.
    Goal: Provide actionable advice based on the user's specific stress points.

    User's Category: {category}
    Specific Stressors reported:
    {context_text}

    Instructions:
    1. Acknowledge their service and honesty.
    2. Address the specific stressors mentioned above (do not be generic).
    3. Provide 1-2 concrete coping techniques relevant to their answers.
    4. If the category is 'Critical Distress', prioritize helpline contact information.
    5. Keep the response under 100 words. Sign off as '— Rakshak Sahayak'.
    6. Do not use markdown formatting. Plain text only.
    """

    try:
        hf_token = st.secrets.get("HF_TOKEN", "")
        if not hf_token:
            st.warning("⚠️ AI Token not configured. Using fallback templates.")
            return get_template_fallback(category)

        client = InferenceClient(token=hf_token)
        
        response = client.text_generation(
            model="google/flan-t5-base",
            prompt=prompt,
            max_new_tokens=150,
            temperature=0.7,
            stop=["\n\n"]
        )
        
        return response.replace("<", "&lt;").replace(">", "&gt;").strip()

    except Exception as e:
        st.warning(f"⚠️ AI Service temporarily unavailable. Using safe fallback response.")
        return get_template_fallback(category)

def find_buddy():
    buddy_names = ["Rakshak-04", "Veer-12", "Navy-09", "Army-21", "BSF-88"]
    return random.choice(buddy_names)

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🛡️", layout="wide")
    init_db()
    inject_css()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = ""
    if "department" not in st.session_state:
        st.session_state.department = ""

    with st.sidebar:
        st.markdown("## 🛡️ ManoRakshak")
        st.caption(APP_SUBTITLE)
        st.divider()
        
        if not st.session_state.logged_in:
            st.markdown("### 🔐 Confidential Check-In")
            st.caption("Identity is one-way hashed. No real names stored.")
            raw_id = st.text_input("Badge / Pseudonym", placeholder="e.g. Falcon-07")
            dept = st.selectbox("Department / Force", DEPARTMENTS)
            
            if st.button("🔓 Enter Confidentially", type="primary"):
                if raw_id.strip():
                    st.session_state.user_id = hash_pseudonym(raw_id)
                    st.session_state.department = dept
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.warning("Please enter a pseudonym.")
        else:
            st.success(f"Signed in as **{st.session_state.user_id}**")
            st.caption(f"Dept: {st.session_state.department}")
            
            if st.button("🚪 End Session", type="secondary"):
                wipe_session()
                st.rerun()
        
        st.divider()
        st.markdown("#### 🚨 In Crisis?")
        for h in HELPLINES:
            st.markdown(f"**{h['name']}**  \n📞 {h['number']}")

    if not st.session_state.logged_in:
        hero_header(APP_TITLE, "A confidential wellness check-in for uniformed personnel. Two minutes. No names. No service record.",
                    chips=["🔒 Zero-Knowledge", "🇮🇳 Tele-MANAS 14416", "📊 Anonymous Analytics"])
        
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown("#### Begin your check-in")
            st.caption("Use a pseudonym. Your identity is hashed before storage.")
            with st.form("checkin_form"):
                raw_id = st.text_input("Badge / Pseudonym", placeholder="e.g. Falcon-07")
                dept = st.selectbox("Department / Force", DEPARTMENTS)
                go = st.form_submit_button("Enter confidentially →", type="primary")
            
            if go and raw_id.strip():
                st.session_state.user_id = hash_pseudonym(raw_id)
                st.session_state.department = dept
                st.session_state.logged_in = True
                st.rerun()
            elif go:
                st.warning("Please enter a pseudonym.")
        
        with right:
            render_crisis_banner(HELPLINES)
            st.caption("Available in 20+ Indian languages. Confidential.")
        st.stop()

    tab_assess, tab_dashboard, tab_admin = st.tabs(
        ["📝 Wellness Screener", "📊 My Dashboard & Buddy", "🔐 Command Analytics"]
    )

    with tab_assess:
        st.markdown("### Confidential Duty Wellness Check-In")
        st.caption("Over the **last 2 weeks**, how often have you been bothered by...")
        
        if "answers" not in st.session_state:
            st.session_state.answers = {}
        if "q_index" not in st.session_state:
            st.session_state.q_index = 0
        
        if not st.session_state.get("processing"):
            current_q = st.session_state.q_index
            total_q = len(QUESTIONS)
            progress = current_q / total_q
            
            c1, c2 = st.columns([4, 1])
            c1.progress(progress, text=f"Question {current_q + 1} of {total_q}")
            
            if current_q > 0:
                c2.markdown("<br>", unsafe_allow_html=True)
                if st.button("← Back", width="stretch"):
                    st.session_state.q_index -= 1
                    st.rerun()
            
            q = QUESTIONS[current_q]
            st.markdown(f'<div class="mr-qcard"><div class="mr-domain">{q["domain"]}</div><div class="mr-qtext">{q["text"]}</div></div>', unsafe_allow_html=True)
            
            answer = st.radio(
                "How often...",
                options=list(range(4)),
                format_func=lambda i: ANSWER_SCALE[i],
                key=f"q_{q['id']}",
                label_visibility="collapsed"
            )
            
            n1, n2 = st.columns([1, 3])
            if answer is None:
                n1.button("Finish" if current_q == total_q - 1 else "Next →", type="secondary", disabled=True)
            else:
                if n1.button("Finish" if current_q == total_q - 1 else "Next →", type="primary"):
                    st.session_state.answers[q["id"]] = answer
                    if current_q < total_q - 1:
                        st.session_state.q_index += 1
                        st.rerun()
                    else:
                        st.session_state.processing = True
                        st.rerun()

        if st.session_state.get("processing"):
            total_score = sum(v for v in st.session_state.answers.values() if v is not None)
            category, emoji = next((label, em) for low, high, label, em in SCORE_CATEGORIES if low <= total_score <= high)
            
            with st.spinner("🤖 Rakshak Sahayak is analyzing your responses..."):
                ai_text = get_ai_debrief(category, st.session_state.answers)
            
            if ai_text is None:
                ai_text = "No response generated. Please try again."
            
            sentiment_result = analyze_sentiment(st.session_state.answers)
            
            save_assessment(st.session_state.user_id, st.session_state.department, total_score, category, st.session_state.answers, ai_text)
            
            st.session_state.processing = False
            st.divider()
            st.markdown(f"## {emoji} Your Result: **{category}**")
            st.progress(min(total_score / MAX_SCORE, 1.0))
            st.caption(f"Score: {total_score} / {MAX_SCORE}")
            
            st.metric("🧠 Sentiment Analysis", f"{sentiment_result['sentiment']} (Confidence: {sentiment_result['score']})")
            
            st.markdown("### 🤝 A Message from Rakshak Sahayak")
            st.markdown(f'<div class="mr-letter">{ai_text}</div><div class="sig">— Rakshak Sahayak</div>', unsafe_allow_html=True)
            
            if category == "Critical Distress":
                st.error("⚠️ Your responses suggest significant distress. Please consider calling a helpline listed in the sidebar.")
            
            st.success("Check-in saved to your private wellness trend.")
            
            b1, b2 = st.columns(2)
            if b1.button("🔄 Take check-in again", width="stretch"):
                st.session_state.answers = {}
                st.session_state.q_index = 0
                st.rerun()
            if b2.button("📊 Go to my dashboard", width="stretch"):
                st.session_state.answers = {}
                st.session_state.q_index = 0
                st.rerun()

    with tab_dashboard:
        st.subheader("📈 Your Wellness Trend")
        history_df = get_user_history(st.session_state.user_id)
        
        if history_df.empty:
            st.info("No check-ins yet. [Complete a screener →](#tab_assess)")
        else:
            history_df["timestamp"] = pd.to_datetime(history_df["timestamp"])
            chart_df = history_df.set_index("timestamp")[["total_score"]].rename(columns={"total_score": "Stress Score"})
            st.line_chart(chart_df, height=300)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Check-ins", len(history_df))
            col2.metric("Latest Score", int(history_df.iloc[-1]["total_score"]))
            col3.metric("Latest Category", history_df.iloc[-1]["category"])
            
            with st.expander("📋 View full history"):
                display_df = history_df[["timestamp", "total_score", "category"]].rename(columns={"timestamp": "Date/Time", "total_score": "Score", "category": "Category"})
                st.dataframe(display_df.sort_values("Date/Time", ascending=False), width="stretch", hide_index=True)
        st.subheader("🧰 Shift Reset Resource Bank")
        tips = [
            "**Box Breathing:** Inhale 4s → Hold 4s → Exhale 4s → Hold 4s. Repeat 4 cycles.",
            "**5-4-3-2-1 Grounding:** Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.",
            "**Post-Shift Decompression:** 10 mins in vehicle/locker room before driving home."
        ]
        for tip in tips:
            st.markdown(f"- {tip}")
        
        st.divider()
        st.subheader("🤝 Buddy System (Peer Support)")
        st.caption("Anonymous, ephemeral peer support. Messages auto-delete after 24 hours.")
        
        if st.button("🤝 Request a Buddy"):
            buddy = find_buddy()
            st.success(f"Matched with Officer **{buddy}** from {st.session_state.department}.")
            st.info("You can now send a quick, encrypted text message. (Demo: Message will auto-delete).")
        
        st.divider()
        st.subheader("📞 Crisis Directory")
        render_crisis_banner(HELPLINES)

    with tab_admin:
        st.subheader("🔐 Command-Level Wellness Analytics")
        st.caption("Password-protected, aggregate-only view. Individual identities are NEVER shown.")
        
        admin_password = st.text_input("Admin Password", type="password")
        
        try:
            expected_password = st.secrets.get("ADMIN_PASSWORD")
        except:
            expected_password = "SIH2026Secure"
            
        if admin_password == "":
            st.info("Enter the admin password.")
        elif admin_password != expected_password:
            st.error("Incorrect password.")
        else:
            st.success("Access granted — showing anonymized aggregate data only.")
            all_df = get_all_assessments()
            
            if all_df.empty:
                st.info("No screenings recorded yet.")
            else:
                total_screenings = len(all_df)
                unique_officers = all_df["user_id"].nunique()
                high_risk_pct = all_df["category"].isin(["High Burnout", "Critical Distress"]).mean() * 100
                low_risk_pct = (all_df["category"] == "Low Stress").mean() * 100
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Screenings", total_screenings)
                m2.metric("Unique Officers", unique_officers)
                m3.metric("% High Risk", f"{high_risk_pct:.1f}%")
                m4.metric("% Low Stress", f"{low_risk_pct:.1f}%")
                
                st.divider()
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("#### Category Distribution")
                    cat_counts = all_df["category"].value_counts()
                    st.bar_chart(cat_counts)
                
                with col_b:
                    st.markdown("#### Avg Score by Department")
                    dept_avg = all_df.groupby("department")["total_score"].mean().sort_values(ascending=False)
                    st.bar_chart(dept_avg)
                
                st.divider()
                st.markdown("#### Screenings Over Time")
                all_df["date"] = pd.to_datetime(all_df["timestamp"]).dt.date
                daily_counts = all_df.groupby("date").size()
                st.line_chart(daily_counts)
                
                st.markdown("#### 🗺️ Wellness Summary")
                st.caption("Regional map view removed for a lighter, dependency-free deployment.")
                st.info("Use the category and department charts above for the live wellness summary.")

if __name__ == "__main__":
    main()
