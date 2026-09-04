# app_ui.py
import streamlit as st

def inject_css():
    """
    Injects custom CSS for a calm, professional, and secure UI.
    Call this immediately after st.set_page_config() in app.py.
    """
    st.markdown("""
    <style>
        /* --- 1. GLOBAL CALM THEME --- */
        /* Soft off-white background to reduce eye strain */
        .stApp {
            background-color: #f8f9fa; 
            color: #2d3748;
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }

        /* Hide default Streamlit branding for a cleaner look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Reduce header clutter */
        header {
            background-color: transparent;
            padding-top: 1rem;
        }

        /* --- 2. TYPOGRAPHY --- */
        h1, h2, h3 {
            color: #2c5282; /* Deep, trustworthy blue */
            font-weight: 600;
            letter-spacing: -0.5px;
        }

        p, li {
            line-height: 1.6;
            color: #4a5568; /* Soft dark grey instead of black */
        }

        /* --- 3. CARDS & CONTAINERS --- */
        /* Generic Card Style */
        .mr-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            transition: transform 0.2s ease;
        }

        /* Question Card (Used in Survey) */
        .mr-qcard {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid #4299e1; /* Softer blue accent */
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .mr-domain {
            color: #4299e1;
            font-weight: 700;
            margin-bottom: 8px;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .mr-qtext {
            font-size: 1.1rem;
            color: #2d3748;
            line-height: 1.5;
        }

        /* Debrief Letter (AI Output) */
        .mr-letter {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            font-family: 'Georgia', serif; /* Serif for a personal letter feel */
            font-size: 1.05rem;
            line-height: 1.7;
            color: #4a5568;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .sig {
            text-align: right;
            font-weight: bold;
            margin-top: 15px;
            color: #718096;
            font-style: italic;
        }

        /* --- 4. CRISIS & ALERTS --- */
        /* Soft Crisis Banner (Not aggressive red, but visible) */
        .mr-crisis {
            background-color: #fff5f5;
            border: 1px solid #feb2b2;
            border-left: 5px solid #c53030;
            padding: 16px 20px;
            border-radius: 8px;
            color: #742a2a;
            margin-bottom: 20px;
        }
        .mr-crisis h4 {
            margin: 0 0 8px 0;
            color: #c53030;
            font-size: 1.1rem;
        }
        .mr-crisis p {
            margin: 0;
            font-size: 0.95rem;
        }

        /* --- 5. BUTTONS & INTERACTIONS --- */
        /* Primary Action Button (Teal/Blue) */
        .stButton > button, .stFormSubmitButton > button {
            background-color: #3182ce;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            background-color: #2b6cb0;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(49, 130, 206, 0.2);
        }

        /* Secondary/Logout Button */
        .stButton > button[kind="secondary"] {
            background-color: #edf2f7;
            color: #4a5568;
            border: 1px solid #cbd5e0;
        }

        /* --- 6. TABS & NAVIGATION --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #e2e8f0;
            border-radius: 6px 6px 0 0;
            padding: 8px 16px;
            font-weight: 500;
            color: #4a5568;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3182ce;
            color: white;
        }

        /* --- 7. SIDEBAR --- */
        section[data-testid="stSidebar"] {
            background-color: #f1f5f9;
            border-right: 1px solid #e2e8f0;
        }
        .sidebar .stMarkdown {
            font-size: 0.9rem;
            color: #718096;
        }
    </style>
    """, unsafe_allow_html=True)


def hero_header(title, subtitle, chips):
    """
    Renders the calm, centered hero section for the landing page.
    """
    chips_html = "".join([
        f'<div style="background:#ffffff; padding: 6px 16px; border-radius: 20px; '
        f'font-size: 0.85rem; color: #4a5568; border: 1px solid #e2e8f0; '
        f'box-shadow: 0 1px 2px rgba(0,0,0,0.05); display: inline-block; margin: 4px;">'
        f'{chip}</div>' 
        for chip in chips
    ])
    
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 3rem; padding: 2rem 1rem;'>
            <h1 style='color: #2c5282; font-size: 2.8rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -1px;'>
                {title}
            </h1>
            <p style='font-size: 1.2rem; color: #718096; max-width: 600px; margin: 0 auto 1.5rem auto; line-height: 1.6;'>
                {subtitle}
            </p>
            <div style='margin-top: 2rem; display: flex; justify-content: center; flex-wrap: wrap; gap: 10px;'>
                {chips_html}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_crisis_banner(helplines):
    """
    Renders a calm but visible crisis support section.
    Args:
        helplines (list): List of dicts with 'name' and 'number'.
    """
    st.markdown("""
    <div class="mr-crisis">
        <h4>🚨 Immediate Support Available</h4>
        <p>You are not alone. If you or a colleague are in crisis, please reach out:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render helplines in a clean grid
    if helplines:
        cols = st.columns(min(2, len(helplines)))
        for i, h in enumerate(helplines):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="background: #fff; padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #feb2b2;">
                    <strong style="color:#c53030;">{h['name']}</strong><br>
                    <span style="font-size:1.1rem; font-weight:600;">📞 {h['number']}</span>
                </div>
                """, unsafe_allow_html=True)


def render_question_card(domain, question_text):
    """
    Helper to render a single survey question card.
    """
    st.markdown(f"""
        <div class="mr-qcard">
            <div class="mr-domain">{domain}</div>
            <div class="mr-qtext">{question_text}</div>
        </div>
    """, unsafe_allow_html=True)
