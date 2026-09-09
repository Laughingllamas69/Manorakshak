import streamlit as st
import html

def inject_css():
    """Injects custom CSS for a clean, light, professional UI matching the reference design."""
    st.markdown("""
    <style>
        /* --- 1. CORE THEME (Light, Clean, Professional) --- */
        .stApp {
            background-color: #F4F6F8; /* Light Gray-Blue Background */
            color: #2C3E50; /* Dark Charcoal Text */
            font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
        }

        /* Hide default Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background-color: transparent;}

        /* --- 2. TYPOGRAPHY & COLORS --- */
        h1, h2, h3 { 
            color: #008080; /* Teal/Turquoise Accent */
            font-weight: 600; 
            letter-spacing: -0.5px; 
        }
        h4 { color: #008080; font-weight: 500; }
        p, li { 
            line-height: 1.7; 
            color: #4A5568; /* Soft Gray Text */
        }

        /* --- 3. CARDS & CONTAINERS (White with Shadow) --- */
        .mr-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0; /* Light Border */
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); /* Soft Shadow */
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .mr-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.08);
        }

        /* Question Card */
        .mr-qcard {
            background: #FFFFFF;
            border-left: 5px solid #008080; /* Teal Accent Line */
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        }
        .mr-domain {
            color: #008080;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .mr-qtext {
            font-size: 1.1rem;
            color: #2D3748;
            font-weight: 500;
        }

        /* AI Debrief Letter */
        .mr-letter {
            background: #FFFFFF;
            border: 1px solid #CBD5E0;
            border-left: 4px solid #008080; /* Teal Accent */
            border-radius: 8px;
            padding: 24px;
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 1.05rem;
            line-height: 1.8;
            color: #2D3748;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        }
        .sig {
            text-align: right;
            color: #008080;
            font-style: italic;
            margin-top: 15px;
            font-weight: 600;
        }

        /* Crisis Banner (Teal/Red Mix) */
        .mr-crisis {
            background: #FFF5F5; /* Very Light Red/White */
            border: 1px solid #FED7D7;
            border-left: 4px solid #E53E3E; /* Red Accent for Crisis */
            border-radius: 8px;
            padding: 16px;
            color: #C53030; /* Dark Red Text */
            margin-bottom: 20px;
        }

        /* Buttons (Teal Primary) */
        .stButton > button {
            background-color: #008080; /* Teal Primary */
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            background-color: #006666; /* Darker Teal */
            transform: translateY(-2px);
        }
        .stButton > button[disabled] {
            background-color: #E2E8F0;
            color: #A0AEC0;
            cursor: not-allowed;
        }

        /* Voice Button (Teal Gradient) */
        .voice-btn {
            background: linear-gradient(135deg, #008080, #006666);
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
            box-shadow: 0 4px 10px rgba(0, 128, 128, 0.3);
            transition: all 0.3s;
        }
        .voice-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 15px rgba(0, 128, 128, 0.5);
        }
        .voice-btn.listening {
            background: #E53E3E;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(229, 62, 62, 0); }
            100% { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0); }
        }

        /* Tabs (Teal Active) */
        .stTabs [data-baseweb="tab-list"] { gap: 12px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #EDF2F7; /* Light Gray Tab */
            border-radius: 8px;
            color: #4A5568;
        }
        .stTabs [aria-selected="true"] {
            background-color: #008080; /* Teal Active Tab */
            color: #FFFFFF;
            font-weight: 600;
        }

        /* Metric Cards (White with Border) */
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 12px;
        }
        div[data-testid="stMetricValue"] { font-size: 1.5rem; color: #008080; }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        .sidebar .stMarkdown {
            color: #4A5568;
        }
    </style>
    """, unsafe_allow_html=True)

def hero_header(title, subtitle, chips):
    """Renders the clean, centered hero section."""
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    chips_html = "".join([
        f'<div style="background:#FFFFFF; padding: 6px 16px; border-radius: 20px; '
        f'font-size: 0.8rem; color: #008080; border: 1px solid #008080; '
        f'box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: inline-block; margin: 4px;">'
        f'{html.escape(chip)}</div>' 
        for chip in chips
    ])

    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 3rem; padding: 2rem 1rem;'>
            <h1 style='color: #008080; font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem;'>
                {safe_title}
            </h1>
            <p style='font-size: 1.2rem; color: #4A5568; max-width: 700px; margin: 0 auto 2rem auto;'>
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
            <div style="background: #FFFFFF; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <strong style="color: #E53E3E;">{html.escape(h['name'])}</strong><br>
                <a href="tel:{html.escape(h['number'])}" style="font-size: 1.3rem; font-weight: 700; color: #008080; text-decoration: none;">
                    📞 {html.escape(h['number'])}
                </a>
            </div>
            """, unsafe_allow_html=True)
