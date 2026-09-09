import streamlit as st
import html

def inject_css():
    """Injects custom CSS for a secure, warm, and professional UI."""
    st.markdown("""
    <style>
        /* --- 1. CORE THEME (Dark, Calming, Professional) --- */
        .stApp {
            background-color: #0E1420;
            color: #E6EAF0;
            font-family: 'Inter', 'Noto Sans Devanagari', sans-serif;
        }
        
        /* Hide default branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background-color: transparent;}

        /* --- 2. TYPOGRAPHY & COLORS --- */
        h1, h2, h3 { color: #E8A33D; font-weight: 600; letter-spacing: -0.5px; }
        h4 { color: #7FB2E5; }
        p, li { line-height: 1.7; color: #9FB0C6; }

        /* --- 3. CARDS & CONTAINERS --- */
        .mr-card {
            background-color: #131C2B;
            border: 1px solid #24304455;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        /* Question Card */
        .mr-qcard {
            background: linear-gradient(135deg, #1A263A 0%, #131C2B 100%);
            border-left: 5px solid #E8A33D;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .mr-domain {
            color: #7FB2E5;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .mr-qtext {
            font-size: 1.1rem;
            color: #E6EAF0;
            font-weight: 500;
        }

        /* AI Debrief Letter */
        .mr-letter {
            background: #141E2E;
            border: 1px solid #2A3547;
            border-left: 4px solid #E8A33D;
            border-radius: 14px;
            padding: 24px;
            font-family: 'Georgia', serif;
            font-size: 1.05rem;
            line-height: 1.8;
            color: #D8E1EC;
        }
        .sig {
            text-align: right;
            color: #8FA2BA;
            font-style: italic;
            margin-top: 15px;
            font-weight: 600;
        }

        /* Crisis Banner */
        .mr-crisis {
            background: #2A1518;
            border: 1px solid #7F2B3366;
            border-left: 4px solid #E0525F;
            border-radius: 12px;
            padding: 16px;
            color: #F3C7CC;
            margin-bottom: 20px;
        }

        /* Buttons */
        .stButton > button {
            background-color: #E8A33D;
            color: #0E1420;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            background-color: #D4881F;
            transform: translateY(-2px);
        }
        .stButton > button[disabled] {
            background-color: #2A3547;
            color: #5D6D7E;
            cursor: not-allowed;
        }

        /* Voice Button */
        .voice-btn {
            background: linear-gradient(135deg, #7FB2E5, #5D6D7E);
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(127, 178, 229, 0.3);
            transition: all 0.3s;
        }
        .voice-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 15px rgba(127, 178, 229, 0.5);
        }
        .voice-btn.listening {
            background: #E0525F;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(224, 82, 95, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(224, 82, 95, 0); }
            100% { box-shadow: 0 0 0 0 rgba(224, 82, 95, 0); }
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] { gap: 12px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #16202F;
            border-radius: 8px;
            color: #9FB0C6;
        }
        .stTabs [aria-selected="true"] {
            background-color: #E8A33D;
            color: #0E1420;
            font-weight: 600;
        }

        /* Metric Cards */
        div[data-testid="stMetric"] {
            background: #131C2B;
            border: 1px solid #24304455;
            border-radius: 12px;
            padding: 12px;
        }
        div[data-testid="stMetricValue"] { font-size: 1.5rem; color: #E8A33D; }
    </style>
    """, unsafe_allow_html=True)

def hero_header(title, subtitle, chips):
    """Renders the secure, centered hero section."""
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    chips_html = "".join([
        f'<div style="background:#16202F; padding: 6px 16px; border-radius: 20px; '
        f'font-size: 0.8rem; color: #7FB2E5; border: 1px solid #24304455; '
        f'box-shadow: 0 2px 4px rgba(0,0,0,0.2); display: inline-block; margin: 4px;">'
        f'{html.escape(chip)}</div>' 
        for chip in chips
    ])

    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 3rem; padding: 2rem 1rem;'>
            <h1 style='color: #E8A33D; font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem;'>
                {safe_title}
            </h1>
            <p style='font-size: 1.2rem; color: #9FB0C6; max-width: 700px; margin: 0 auto 2rem auto;'>
                {safe_subtitle}
            </p>
            <div style='margin-top: 2rem; display: flex; justify-content: center; flex-wrap: wrap; gap: 10px;'>
                {chips_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_crisis_banner(helplines):
    """Renders the emergency support banner."""
    st.markdown("""
    <div class="mr-crisis">
        <h4 style="margin-top:0;">🚨 In Immediate Crisis?</h4>
        <p style="margin-bottom:15px;">You do not need to complete a check-in to get help. Support is confidential and 24/7.</p>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, h in enumerate(helplines):
        col = cols[i % 2]
        with col:
            st.markdown(f"""
            <div style="background: #1A263A; padding: 15px; border-radius: 10px; border: 1px solid #24304455; text-align: center;">
                <strong style="color: #E0525F;">{html.escape(h['name'])}</strong><br>
                <a href="tel:{html.escape(h['number'])}" style="font-size: 1.3rem; font-weight: 700; color: #E8A33D; text-decoration: none;">
                    📞 {html.escape(h['number'])}
                </a>
            </div>
            """, unsafe_allow_html=True)
