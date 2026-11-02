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

1. **📋 Setup & Import:** Laai atletelyste in via Excel met afsonderlike **Seuns (M)** en **Dogters (F)** tabs, of voeg individuele laat-inskrywings by.
2. **📄 Draw Sheets:** Bekyk amptelike lotingslyste in 'n snelbesigtigings-venster of druk dit as PDF met 'n ingeboude uitslaeblok.
3. **⏱️ Officiating:** Aangepaste punte- en tydsfunksie met snel-knoppies vir items, dinamiese heats vir die baan, en 'n hoogte-skuiwer vir hoogspring.
4. **🏆 Rekords:** Bestuur, voer in of uit via Excel, en bekyk alle amptelike byeenkomsrekords.
5. **📊 Live Feed:** Regstreekse uitslae vir ouers, onderwysers en spanbestuurders met outomatiese herlaai.
6. **🥇 Medaljes:** Outomatiese Prysdeling-tafel wat die Top 4 vir alle gefinaliseerde items vertoon.
7. **🖨️ Reports:** Totale spanpunte, Victor & Victrix Ludorum en amptelike PDF Uitslagboekie.
8. **📅 Program:** Bestuur die tydrooster van die dag, voer uit na PDF/Excel en hou vordering op die terrein dop.
""")

st.info("💡 **Lokale / Wolk Modus:** SQLite hanteer data plaaslik. Koppel Supabase in `.streamlit/secrets.toml` vir intydse sinchronisasie tussen verskeie fone en tablette op die veld.")
