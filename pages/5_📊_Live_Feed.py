import streamlit as st
import pandas as pd
from db import fetch_all_results
from constants import apply_swartland_theme, AGE_GROUPS

st.set_page_config(page_title="Live Feed", page_icon="📊", layout="wide")
apply_swartland_theme()

st.title("📊 Regstreekse Byeenkoms Uitslae (Live Feed)")

# Outomatiese herlaai opsie
auto_refresh = st.checkbox("🔄 Outomatiese Herlaai (elke 10 sekondes)", value=False)
if auto_refresh:
    st.empty()

results_df = fetch_all_results()

if not results_df.empty:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        school_filter = st.selectbox("Filter volgens Skool", ["Alle Skole"] + sorted(list(results_df['school'].dropna().unique())))
    with col_f2:
        age_filter = st.selectbox("Filter volgens Ouderdom", ["Alle Ouderdomme"] + AGE_GROUPS)

    filtered_df = results_df.copy()
    if school_filter != "Alle Skole":
        filtered_df = filtered_df[filtered_df['school'] == school_filter]
    if age_filter != "Alle Ouderdomme":
        filtered_df = filtered_df[filtered_df['age_group'] == age_filter]

    st.subheader(f"Regstreekse Resultate ({len(filtered_df)} items vasgelê)")
    
    clean_display = filtered_df[['place', 'athlete_name', 'school', 'event_name', 'age_group', 'gender', 'result_value', 'asa_points']].copy()
    clean_display.columns = ["Plek", "Atleet Naam", "Skool", "Item", "Ouderdom", "Geslag", "Uitslag", "ASA Punte"]
    
    st.dataframe(clean_display, use_container_width=True)
else:
    st.info("⏱️ Geen uitslae is nog vir vandag se byeenkoms ingedien nie. Uitslae sal hier verskyn sodra beamptes dit vasleg.")