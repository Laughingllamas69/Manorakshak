# app_ui.py
# This file contains the custom CSS styles for the Manorakshak app
import streamlit as st
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+Devanagari:wght@400;600&display=swap');

/* --- General Layout --- */
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1100px; }
#MainMenu, footer { visibility: hidden; }

/* --- Typography --- */
html, body, [class*="css"] { font-family: 'Inter', 'Noto Sans Devanagari', sans-serif; }
h1, h2, h3 { letter-spacing: -0.02em; font-weight: 600 !important; }

/* --- Hero Header --- */
.mr-hero {
  padding: 2.2rem 2.4rem;
  border-radius: 18px;
  background:
    radial-gradient(120% 140% at 0% 0%, rgba(232,163,61,.16) 0%, rgba(232,163,61,0) 55%),
    linear-gradient(135deg, #131C2B 0%, #0E1420 100%);
  border: 1px solid #24304455;
  margin-bottom: 1.6rem;
}
.mr-hero h1 { margin: 0 0 .35rem 0; font-size: 2.1rem !important; }
.mr-hero p  { margin: 0; color: #9FB0C6; font-size: 1.02rem; font-weight: 300; }
.mr-chip {
  display: inline-block; font-size: .72rem; letter-spacing: .12em;
  text-transform: uppercase; color: #E8A33D; font-weight: 600;
  border: 1px solid #E8A33D44; border-radius: 999px; padding: .22rem .7rem;
  margin-bottom: .9rem;
}
.mr-trust { display:flex; gap:.6rem; flex-wrap:wrap; margin-top:1.1rem; }
.mr-trust span {
  font-size:.78rem; color:#9FB0C6; background:#16202F;
  border:1px solid #24304488; padding:.3rem .75rem; border-radius:8px;
}

/* --- Question Card --- */
.mr-qcard {
  background:#131C2B; border:1px solid #24304488; border-radius:16px;
  padding:1.8rem 2rem; margin-bottom:1rem;
}
.mr-domain {
  font-size:.7rem; letter-spacing:.14em; text-transform:uppercase;
  color:#7FB2E5; font-weight:600; margin-bottom:.55rem;
}
.mr-qtext { font-size:1.28rem; font-weight:500; line-height:1.45; color:#E6EAF0; }

/* --- Debrief Letter --- */
.mr-letter {
  background: linear-gradient(180deg,#141E2E 0%, #111926 100%);
  border:1px solid #2A3547; border-left:4px solid #E8A33D;
  border-radius:14px; padding:1.7rem 1.9rem; line-height:1.72; color:#D8E1EC;
}
.mr-letter .sig {
  margin-top:1.1rem; padding-top:.9rem; border-top:1px solid #2A3547;
  font-size:.82rem; color:#8FA2BA; letter-spacing:.04em;
}

/* --- Crisis Banner --- */
.mr-crisis {
  background:#2A1518; border:1px solid #7F2B3366; border-left:4px solid #E0525F;
  border-radius:12px; padding:1.1rem 1.4rem; color:#F3C7CC;
}

/* --- Metrics --- */
div[data-testid="stMetric"] {
  background:#131C2B; border:1px solid #24304488; border-radius:12px;
  padding:.9rem 1.1rem;
}
div[data-testid="stMetricValue"] { font-size:1.6rem; font-weight:600; }

/* --- Buttons --- */
button[kind="primary"] {
  background:linear-gradient(135deg,#E8A33D,#D4881F) !important;
  border:none !important; color:#0E1420 !important; font-weight:600 !important;
}
button[kind="primary"]:hover { filter:brightness(1.08); }

/* --- Sidebar --- */
section[data-testid="stSidebar"] { border-right:1px solid #1C2637; }

/* --- Hide Deploy Button --- */
#deploy-button, .stDeployButton { display:none; }
</style>
"""

def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)

def hero_header(title, subtitle, chips=None):
    chips = chips or []
    chip_html = "".join(f"<span>{c}</span>" for c in chips)
    st.markdown(
        f"""
        <div class="mr-hero">
          <div class="mr-chip">Confidential · No real name required</div>
          <h1>{title}</h1>
          <p>{subtitle}</p>
          <div class="mr-trust">{chip_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
