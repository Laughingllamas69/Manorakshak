# app_ui.py
import streamlit as st

def inject_css():
    """Inject custom CSS for the ManoRakshak UI."""
    st.markdown("""
        <style>
        /* Main Container Styling */
        .stTabs [data-testid="stTabs"] {
            display: flex;
            flex-direction: row;
            justify-content: center;
            font-weight: bold;
        }
        
        /* Question Card Styling */
        .mr-qcard {
            background-color: #f0f2f6;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid #2E86DE;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .mr-domain {
            color: #2E86DE;
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .mr-qtext {
            font-size: 1.1rem;
            color: #333;
            line-height: 1.6;
        }
        
        /* AI Debrief Letter Styling */
        .mr-letter {
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            font-style: italic;
            font-size: 1.05rem;
            line-height: 1.6;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .sig {
            text-align: right;
            font-weight: bold;
            margin-top: 10px;
            color: #555;
        }
        
        /* Crisis Banner Styling */
        .mr-crisis {
            background-color: #fff3f3;
            border: 1px solid #ffcccc;
            padding: 15px;
            border-radius: 8px;
            color: #d63031;
            font-size: 1rem;
            line-height: 1.5;
        }
        
        /* Sidebar Styling */
        .sidebar .stMarkdown {
            font-size: 0.9rem;
        }
        
        /* Button Styling */
        .stButton > button {
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

def hero_header(title, subtitle, chips):
    """Render the hero header section for unauthenticated users."""
    chips_html = "".join([f'<span style="background:#f0f2f6; padding: 5px 15px; border-radius: 20px; font-size: 0.9rem; margin-right: 10px; display: inline-block;">{chip}</span>' for chip in chips])
    
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 2rem; padding: 20px; border-radius: 8px;'>
            <h1 style='color: #2E86DE; margin-bottom: 0.5rem;'>{title}</h1>
            <p style='font-size: 1.2rem; color: #555; margin-bottom: 1.5rem;'>{subtitle}</p>
            <div style='margin-top: 1.5rem; display: flex; justify-content: center; flex-wrap: wrap; gap: 10px;'>
                {chips_html}
            </div>
        </div>
    """, unsafe_allow_html=True)
