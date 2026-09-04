# app_ui.py
import streamlit as st
import html  # For safely escaping user input

def inject_css():
    """
    Injects custom CSS for a warm, calming, and secure UI.
    Call this immediately after st.set_page_config() in app.py.
    """
    st.markdown("""
    <style>
        /* --- 1. WARM CALMING THEME --- */
        /* Creamy off-white background to reduce eye strain and feel organic */
        .stApp {
            background-color: #FDFBF7; 
            color: #4A4036; /* Warm charcoal, softer than black */
            font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
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
            color: #5D4037; /* Warm, earthy brown */
            font-weight: 600;
            letter-spacing: -0.5px;
            margin-bottom: 0.5rem;
        }

        p, li {
            line-height: 1.7; /* Increased for readability */
            color: #6D5E50; /* Soft warm grey-brown */
        }

        /* --- 3. CARDS & CONTAINERS (Warm & Soft) --- */
        /* Generic Card Style */
        .mr-card {
            background-color: #FFFFFF;
            border-radius: 16px; /* Softer corners */
            padding: 28px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(93, 64, 55, 0.06); /* Warm shadow tint */
            border: 1px solid #F0E6DC; /* Warm beige border */
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .mr-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(93, 64, 55, 0.1);
        }

        /* Question Card (Used in Survey) */
        .mr-qcard {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 18px;
            border-left: 5px solid #D4A373; /* Warm Clay Accent */
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }

        .mr-domain {
            color: #D4A373; /* Warm Clay */
            font-weight: 700;
            margin-bottom: 10px;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .mr-qtext {
            font-size: 1.1rem;
            color: #4A4036;
            line-height: 1.6;
        }

        /* Debrief Letter (AI Output) */
        .mr-letter {
            background-color: #FFFBF7; /* Very subtle warm tint */
            border: 1px solid #E8DCC4;
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
            font-family: 'Georgia', 'Times New Roman', serif; /* Serif for empathy */
            font-size: 1.1rem;
            line-height: 1.8;
            color: #4A4036;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        }

        .sig {
            text-align: right;
            font-weight: 600;
            margin-top: 20px;
            color: #8D6E63; /* Muted warm brown */
            font-style: italic;
        }

        /* --- 4. CRISIS & ALERTS (Safe & Supportive) --- */
        /* Soft Support Banner - Uses warm red/orange, not aggressive red */
        .mr-crisis {
            background-color: #FFF8F5; /* Very light warm peach */
            border: 1px solid #FECACA;
            border-left: 5px solid #EA580C; /* Warm amber/orange */
            padding: 20px 24px;
            border-radius: 12px;
            color: #7C2D12; /* Warm dark orange text */
            margin-bottom: 24px;
        }

        .mr-crisis h4 {
            margin: 0 0 8px 0;
            color: #EA580C;
            font-size: 1.15rem;
            font-weight: 600;
        }

        .mr-crisis p {
            margin: 0;
            font-size: 0.95rem;
            color: #9A3412;
        }

        /* --- 5. BUTTONS & INTERACTIONS (Warm & Inviting) --- */
        /* Primary Action Button (Warm Terracotta) */
        .stButton > button, .stFormSubmitButton > button {
            background-color: #D4A373; /* Warm Clay */
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 12px 28px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.25s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stButton > button:hover, .stFormSubmitButton > button:hover {
            background-color: #BC8A5F; /* Darker Clay */
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(212, 163, 115, 0.3);
        }

        /* Secondary/Logout Button */
        .stButton > button[kind="secondary"] {
            background-color: #FDF5E6; /* Light cream */
            color: #6D5E50;
            border: 1px solid #E8DCC4;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background-color: #F0E6DC;
        }

        /* --- 6. TABS & NAVIGATION --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #F5F0EB; /* Warm grey-beige */
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            font-weight: 500;
            color: #6D5E50;
            transition: all 0.2s ease;
        }

        .stTabs [aria-selected="true"] {
            background-color: #D4A373; /* Warm Clay */
            color: #FFFFFF;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* --- 7. SIDEBAR --- */
        section[data-testid="stSidebar"] {
            background-color: #F9F5F0; /* Warm off-white */
            border-right: 1px solid #E8DCC4;
        }

        .sidebar .stMarkdown {
            font-size: 0.9rem;
            color: #8D6E63;
        }
    </style>
    """, unsafe_allow_html=True)

def hero_header(title, subtitle, chips):
    """
    Renders the calm, centered hero section for the landing page.
    Uses HTML escaping for security against XSS attacks.
    """
    # SECURITY: Escape all user inputs to prevent HTML injection
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    
    # Safely render chips
    chips_html = "".join([
        f'<div style="background:#ffffff; padding: 8px 20px; border-radius: 24px; '
        f'font-size: 0.85rem; color: #6D5E50; border: 1px solid #E8DCC4; '
        f'box-shadow: 0 2px 4px rgba(0,0,0,0.04); display: inline-block; margin: 6px;">'
        f'{html.escape(chip)}</div>' 
        for chip in chips
    ])

    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 3.5rem; padding: 3rem 1rem;'>
            <h1 style='color: #5D4037; font-size: 3rem; font-weight: 700; margin-bottom: 0.8rem; letter-spacing: -1px;'>
                {safe_title}
            </h1>
            <p style='font-size: 1.25rem; color: #8D6E63; max-width: 700px; margin: 0 auto 2rem auto; line-height: 1.6;'>
                {safe_subtitle}
            </p>
            <div style='margin-top: 2.5rem; display: flex; justify-content: center; flex-wrap: wrap; gap: 12px;'>
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
        <h4>🌸 You Are Not Alone</h4>
        <p>If you or a colleague are in crisis, please reach out. Support is available 24/7.</p>
    </div>
    """, unsafe_allow_html=True)

    # Render helplines in a clean grid
    if helplines:
        # Ensure we don't break layout if list is empty or odd
        cols = st.columns(min(2, len(helplines)))
        
        safe_helplines = [h for h in helplines if 'name' in h and 'number' in h]
        
        for i, h in enumerate(safe_helplines):
            # SECURITY: Escape all input
            h_name = html.escape(h['name'])
            h_number = html.escape(h['number'])
            
            with cols[i % 2]:
                st.markdown(f"""
                <div style="background: #fff; padding: 16px; border-radius: 12px; margin-top: 10px; border: 1px solid #FECACA; text-align: center;">
                    <strong style="color:#EA580C; font-size: 1.1rem;">{h_name}</strong><br>
                    <span style="font-size:1.2rem; font-weight:600; color: #7C2D12;">📞 {h_number}</span>
                </div>
                """, unsafe_allow_html=True)

def render_question_card(domain, question_text):
    """
    Helper to render a single survey question card.
    """
    # SECURITY: Escape all HTML entities
    safe_domain = html.escape(domain)
    safe_question = html.escape(question_text)

    st.markdown(f"""
        <div class="mr-qcard">
            <div class="mr-domain">{safe_domain}</div>
            <div class="mr-qtext">{safe_question}</div>
        </div>
    """, unsafe_allow_html=True)
