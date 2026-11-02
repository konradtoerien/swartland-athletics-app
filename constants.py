import os
import streamlit as st

# Laerskool Swartland Tema Kleure
NAVY_HEADER = "0A192F"
NAVY_BG = "112240"
GOLD_ACCENT = "F4C430"
WHITE_TEXT = "FFFFFF"
ZEBRA_FILL = "112240"

AGE_GROUPS = ["6", "7", "8", "9", "10", "11", "12", "13"]

# Pad na skool-logo
LOGO_PATH = "LSS LOGO - small.png"

def normalize_age_group(val) -> str:
    s = str(val).strip().lower().replace("u/", "").replace("u", "")
    return s if s in AGE_GROUPS else "13"

def get_events_for_age_and_gender(age_group: str, gender: str) -> list[str]:
    age = normalize_age_group(age_group)
    is_girls = str(gender).strip().lower().startswith(("d", "g", "f"))
    
    events = []
    if age == "6":
        events = ["50m"]
    elif age in ["7", "8"]:
        events = ["60m", "80m"]
    elif age == "9":
        events = ["60m", "80m", "100m", "1200m", "Long Jump", "High Jump", "Shot Put"]
    elif age in ["10", "11"]:
        events = ["60m", "80m", "100m", "1200m", "70m Hurdles", "Long Jump", "High Jump", "Shot Put"]
    elif age == "12":
        events = [
            "60m", "80m", "100m", "150m", "1200m", 
            "75m Hurdles", "150m Hurdles", 
            "Long Jump", "High Jump", "Shot Put", "Discus", "Javelin", "1500m Walk"
        ]
    elif age == "13":
        hurdle = "75m Hurdles" if is_girls else "80m Hurdles"
        events = [
            "80m", "100m", "200m", "1500m", 
            hurdle, "200m Hurdles", 
            "Long Jump", "High Jump", "Shot Put", "Discus", "Javelin", "1500m Walk"
        ]
    
    events.append("4x100m Relay")
    return events

ALL_DISCIPLINES = [
    "50m", "60m", "80m", "100m", "150m", "200m", 
    "1200m", "1500m", "1500m Walk", "4x100m Relay",
    "70m Hurdles", "75m Hurdles", "80m Hurdles", "150m Hurdles", "200m Hurdles", 
    "Long Jump", "High Jump", "Shot Put", "Discus", "Javelin"
]

def apply_swartland_theme():
    """LSS Tema en Vertoning van Logo op die Kantlyn (Sidebar)."""
    st.markdown("""
        <style>
            .stApp {
                background-color: #0A192F !important;
                color: #FFFFFF !important;
            }
            div[data-testid="stSidebar"] {
                background-color: #020C1B !important;
                border-right: 2px solid #F4C430;
            }
            div[data-testid="stSidebar"] * {
                color: #F4C430 !important;
            }
            h1, h2, h3, h4, label, span {
                color: #F4C430 !important;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            p, div, td, th {
                color: #E6F1FF !important;
            }
            .stTextInput>div>div>input, .stSelectbox>div>div>div, .stMultiSelect>div {
                background-color: #112240 !important;
                color: #FFFFFF !important;
                border: 1px solid #F4C430 !important;
            }
            .stButton>button {
                background-color: #F4C430 !important;
                color: #0A192F !important;
                font-weight: bold !important;
                border: 2px solid #F4C430 !important;
                border-radius: 6px;
            }
            .stButton>button:hover {
                background-color: #0A192F !important;
                color: #F4C430 !important;
            }
            div[data-testid="stSidebar"] img {
                margin-bottom: 10px;
                border-radius: 4px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Vertoon die skool-logo bo-aan die kantlyn
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, width=180)
    else:
        st.sidebar.warning(f"Logo nie gevind nie ({LOGO_PATH})")
        
    st.sidebar.markdown("### Laerskool Swartland")