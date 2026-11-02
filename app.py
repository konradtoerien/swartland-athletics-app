import streamlit as st
from constants import apply_swartland_theme

st.set_page_config(
    page_title="Swartland Atletiek Portaal",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_swartland_theme()

st.title("🏆 Laerskool Swartland Atletiek Portaal")
st.subheader("Byeenkomsbestuur & Intydse Beoordelingsstelsel")

st.markdown("""
Welkom by die atletiekbestuurstelsel. Kies 'n module uit die kieslys aan die linkerkant om te begin:

1. **📋 Setup & Import:** Laai atletelyste in via Excel met **Seuns (M)** en **Dogters (F)** tabs.
2. **📄 Draw Sheets:** Bekyk amptelike lotingslyste in 'n snelbesigtigings-venster of druk dit as PDF.
3. **⏱️ Officiating:** Aangepaste punte- en tydsfunksie vir beamptes om resultate live aan te teken.
4. **🏆 Rekords:** Bestuur, voer in of uit via Excel, en bekyk alle amptelike byeenkomsrekords.
5. **📊 Live Feed:** Regstreekse uitslae vir ouers, onderwysers en spanbestuurders.
6. **🖨️ Reports:** Totale spanpunte, Victor/Victrix Ludorum en amptelike PDF uitslagopsommings.
7. **📅 Program:** Bestuur die tydrooster van die dag, voer uit na PDF/Excel en hou vordering dop.
""")

st.info("💡 **Lokale Modus Aktief:** SQLite hanteer op die oomblik data plaaslik. Koppel Supabase in `.streamlit/secrets.toml` vir intydse sinchronisasie tussen verskeie toestelle.")