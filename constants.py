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
    """LSS Tema met voorgeskrewe kontras en versteekte Streamlit menus."""
    st.markdown("""
        <style>
            /* 1. Verberg die Boonste Header (Drie kolletjies & Running indicator) en Onderste Footer */
            header[data-testid="stHeader"] {
                visibility: hidden !important;
                height: 0px !important;
            }
            footer {
                visibility: hidden !important;
                height: 0px !important;
            }
            #MainMenu {
                visibility: hidden !important;
            }

            /* 2. Hoof Toepassing Agtergrond */
            .stApp {
                background-color: #0A192F !important;
                color: #FFFFFF !important;
            }
            
            /* 3. Dwing die Kantlyn (Sidebar) na Donkerblou */
            [data-testid="stSidebar"], 
            section[data-testid="stSidebar"],
            div[data-testid="stSidebarContent"] {
                background-color: #020C1B !important;
                border-right: 2px solid #F4C430 !important;
            }

            /* 4. Dwing alle Teks en Skakels in die Sidebar om Geel & Wit te wees */
            [data-testid="stSidebar"] * {
                color: #FFFFFF !important;
            }
            
            /* Sidebar Navigasie-skakels en Teks (Streamlit Nav) */
            [data-testid="stSidebarNav"] ul li a,
            [data-testid="stSidebarNav"] ul li a * {
                background-color: transparent !important;
                color: #F4C430 !important;
                font-weight: bold !important;
                font-size: 1.05rem !important;
            }

            /* Aktiewe / Geselekteerde Bladsy in Sidebar */
            [data-testid="stSidebarNav"] ul li a[aria-current="page"] {
                background-color: #112240 !important;
                border-left: 4px solid #F4C430 !important;
                border-radius: 4px;
            }
            [data-testid="stSidebarNav"] ul li a[aria-current="page"] * {
                color: #FFFFFF !important;
            }

            /* 5. Hoofskerm Opskrifte en Teks */
            h1, h2
