import sqlite3
import streamlit as st
import pandas as pd
from db import fetch_athletes, fetch_event_record, save_event_results, fetch_event_results, get_local_connection
from constants import AGE_GROUPS, get_events_for_age_and_gender, apply_swartland_theme

st.set_page_config(page_title="Beoordeling", page_icon="⏱️", layout="wide")
apply_swartland_theme()

st.title("⏱️ Beoordeling & Uitslae")

col1, col2, col3 = st.columns(3)
with col1:
    selected_age = st.selectbox("Ouderdomsgroep", AGE_GROUPS, index=7)
with col2:
    selected_gender = st.selectbox("Geslag", ["Seuns", "Dogters"])
with col3:
    available_events = get_events_for_age_and_gender(selected_age, selected_gender)
    selected_event = st.selectbox("Item / Dissipline", available_events if available_events else ["Geen items"])

st.divider()

def parse_result_to_numeric(raw_val: str, event_name: str) -> float:
    if not raw_val:
        return 0.0
    clean_str = str(raw_val).strip().replace(" ", "")
    parts = clean_str.split(",")
    try:
        if len(parts) == 1:
            return float(parts[0])
        elif len(parts) == 2:
            return float(f"{parts[0]}.{parts[1]}")
        elif len(parts) >= 3:
            mins = float(parts[0])
            secs = float(parts[1])
            ms = float(parts[2]) / 100.0 if len(parts[2]) <= 2 else float(parts[2]) / 1000.0
            return (mins * 60.0) + secs + ms
    except ValueError:
        return 0.0
    return 0.0

def calculate_asa_points(event: str, parsed_val: float) -> int:
    if parsed_val <= 0:
        return 0
    is_track = any(m in event for m in ["m", "Hurdles", "Walk", "Relay"]) and not any(f in event for f in ["Jump", "Put", "Discus", "Javelin"])
    if is_track:
        pts = int(1000 - ((parsed_val - 10.0) * 35))
        return max(10, min(1200, pts))
    else:
        pts = int(parsed_val * 180)
        return max(10, min(1200, pts))

def delete_single_athlete_result(event_name, gender, age_group, athlete_id):
    """Verwyder presies EEN spesifieke atleet se uitslag."""
    conn = get_local_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM event_results 
        WHERE event_name = ? AND gender = ? AND age_group = ? AND athlete_id = ?
    ''', (event_name, gender, age_group, athlete_id))
    conn.commit()
    conn.close()

if selected_event and selected_event != "Geen items":
    record_info = fetch_event_record(selected_event, selected_gender, selected_age)
    if record_info:
        st.info(f"🏆 **Huidige Rekord:** {record_info['record_value']} deur {record_info['holder']} ({record_info['year']})")
    else:
        st.caption("Geen bestaande rekord aangeteken vir hierdie item nie.")

    athletes = fetch_athletes({"gender": selected_gender, "age_group": selected_age})
    if not athletes.empty:
        athletes = athletes[athletes['events'].str.contains(selected_event, case=False, na=False)].copy()

    if not athletes.empty:
        st.subheader(f"Uitslae: O/{selected_age} {selected_gender} - {selected_event}")
        st.caption("💡 Tik waardes aan die regterkant in met 'n komma (bv. `4,52` vir veld of `3,45,55` vir langafstande). Druk dan die geel knoppie onderaan.")
        
        results_data = []
        
        # Netjiese Invoerrooster: Atleetbesonderhede links, Invoer velde regskant
        with st.form("bulk_results_entry_form"):
            # Tabelopskrifte vir die Form
            hdr1, hdr2, hdr3 = st.columns([3, 2, 1])
            hdr1.markdown("**Atleet & Skool**")
            hdr2.markdown("**Invoer Uitslag**")
            hdr3.markdown("**ASA Punte**")
            st.divider()
            
            for idx, row in athletes.iterrows():
                c_left, c_middle, c_right = st.columns([3, 2, 1])
                with c_left:
                    st.markdown(f"**{row['first_name']} {row['last_name']}**  \n`{row['school']}`")
                
                with c_middle:
                    raw_input = st.text_input(
                        label=f"res_{row['id']}", 
                        key=f"res_{row['id']}", 
                        placeholder="bv. 4,52 of 12,45", 
                        label_visibility="collapsed"
                    )
                
                parsed_num = parse_result_to_numeric(raw_input, selected_event)
                pts = calculate_asa_points(selected_event, parsed_num)
                
                with c_right:
                    st.markdown(f"**{pts}** Punte" if pts > 0 else "-")
                
                results_data.append({
                    "athlete_id": row['id'],
                    "name": f"{row['first_name']} {row['last_name']}",
                    "school": row['school'],
                    "result_value": raw_input,
                    "parsed_val": parsed_num,
                    "asa_points": pts
                })
                st.markdown("<hr style='margin:4px 0px; border-color:#112240;'>", unsafe_allow_html=True)

            submit = st.form_submit_button("🔒 Stuur & Rangskik Uitslae", type="primary")
            if submit:
                is_track = any(m in selected_event for m in ["m", "Hurdles", "Walk", "Relay"]) and not any(f in selected_event for f in ["Jump", "Put", "Discus", "Javelin"])
                valid_results = [r for r in results_data if r["parsed_val"] > 0]
                valid_results.sort(key=lambda x: x["parsed_val"], reverse=not is_track)
                
                for rank, res in enumerate(valid_results, 1):
                    res["place"] = rank
                    
                if valid_results:
                    save_event_results(selected_event, selected_gender, selected_age, valid_results)
                    st.success("Uitslae suksesvol gesinkroniseer en gerangskik!")
                    st.rerun()
                else:
                    st.warning("Tik ten minste een uitslag in voor stuur.")

    # Netjiese Uitslae Tabel met Enkel Atleet Skrap-knoppie
    st.divider()
    st.subheader("🥇 Outomatiese Ranglys & Uitslae Bestuur")
    
    captured_df = fetch_event_results(selected_event, selected_gender, selected_age)
    if not captured_df.empty:
        # Vertoon netjiese geregistreerde tabel
        st.dataframe(captured_df, use_container_width=True)
        
        # Enkele Skrap Aksie-afdeling
        with st.expander("🗑️ Skrap 'n Enkele Atleet se Uitslag"):
            col_sel, col_act = st.columns([3, 1])
            with col_sel:
                athlete_to_del = st.selectbox(
                    "Kies atleet om hul uitslag te verwyder:",
                    options=captured_df['Atleet Naam'].tolist()
                )
            with col_act:
                if st.button("Skrap Hierdie Uitslag"):
                    # Vind athlete_id vanaf die athletes lys
                    match_ath = athletes[athletes.apply(lambda r: f"{r['first_name']} {r['last_name']}" == athlete_to_del, axis=1)]
                    if not match_ath.empty:
                        ath_id = match_ath.iloc[0]['id']
                        delete_single_athlete_result(selected_event, selected_gender, selected_age, ath_id)
                        st.success(f"Uitslag vir {athlete_to_del} verwyder!")
                        st.rerun()
    else:
        st.info("Nog geen uitslae ingedien nie.")