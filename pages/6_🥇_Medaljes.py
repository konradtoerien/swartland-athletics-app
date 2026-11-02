import streamlit as st
import pandas as pd
from db import fetch_all_results
from constants import apply_swartland_theme

st.set_page_config(page_title="Medaljes", page_icon="🥇", layout="wide")
apply_swartland_theme()

st.title("🥇 Medaljetafel & Prysdeling")
st.caption("Hierdie bladsy vertoon outomaties die Top 4 atlete vir alle afgehandelde items vir maklike medalje-oorhandiging.")

results_df = fetch_all_results()

if not results_df.empty:
    # Groepeer volgens item, geslag en ouderdom
    grouped = results_df.groupby(['event_name', 'gender', 'age_group'])
    
    st.subheader("🏆 Items Gereed vir Prysdeling")
    
    for (event_name, gender, age_group), group in grouped:
        top4 = group.sort_values(by='place').head(4)
        
        with st.expander(f"🥇 O/{age_group} {gender} - {event_name}", expanded=True):
            cols = st.columns(4)
            labels = ["🥇 1ste Plek (Goud)", "🥈 2de Plek (Silwer)", "🥉 3de Plek (Brons)", "4️⃣ 4de Plek"]
            
            for idx, (_, row) in enumerate(top4.iterrows()):
                if idx < 4:
                    with cols[idx]:
                        st.markdown(f"**{labels[idx]}**")
                        st.markdown(f"### {row['athlete_name']}")
                        st.markdown(f"**Skool:** {row['school']}")
                        st.markdown(f"**Uitslag:** {row['result_value']} ({row['asa_points']} pt)")
                        
            st.button(f"✅ Merk Prysdeling as Voltooi ({event_name})", key=f"med_{event_name}_{gender}_{age_group}")
else:
    st.info("Nog geen items gefinaliseer vir medalje-oorhandiging nie.")
