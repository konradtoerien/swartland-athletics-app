import streamlit as st

st.set_page_config(
page_title="Swartland Athletics Portal",
page_icon="🏃",
layout="wide",
initial_sidebar_state="expanded"
)

st.title("🏃 Swartland Athletics Portal")
st.subheader("Meet Management & Real-Time Officiating System")

st.markdown("""
Welcome to the Athletics Meet Management System. Select a module from the left sidebar to get started:

1. **📋 Setup & Import:** Register athletes via CSV/Excel template or add individual late entries.

2. **📄 Draw Sheets:** View, manage, and print official lane/event draw sheets with auto-added late entries.

3. **⏱️ Officiating (Coming Next):** Record field attempts and track times live from officials' devices.

4. **📊 Live Feed (Coming Next):** Public mobile-friendly view for parents, coaches, and team managers.

5. **🖨️ Reports (Coming Next):** Aggregated team scores, Victor/Victrix Ludorum, and official PDF result summaries.
   """)

st.info("💡 **Local Mode Active:** SQLite is currently handling local data. To sync multiple devices across the track in real-time, connect Supabase credentials in `.streamlit/secrets.toml`.")