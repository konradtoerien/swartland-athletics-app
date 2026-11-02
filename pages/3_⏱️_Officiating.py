import sqlite3
import streamlit as st
import pandas as pd
from db import fetch_athletes, fetch_event_record, save_event_results, fetch_event_results, get_local_connection
from constants import AGE_GROUPS, get_events_for_age_and_gender, apply_swartland_theme, ALL_DISCIPLINES

st.set_page_config(page_title="Beoordeling", page_icon="⏱️", layout="wide")
apply_swartland_theme()

st.title("⏱️ Intydse Beoordeling & Uitslae")

# 1. Snel-knoppies vir Geslag & Ouderdom
col_g, col_a = st.columns(2)
with col_g:
    selected_gender = st.radio("Geslag", ["Seuns", "Dogters"], horizontal=True)
with col_a:
    selected_age = st.radio("Ouderdomsgroep", AGE_GROUPS, index=7, horizontal=True)

available_events = get_events_for_age_and_gender(selected_age, selected_gender)

st.write("**Kies Item (Snel-knoppies):**")
cols_ev = st.columns(min(len(available_events), 6))
if "active_event" not in st.session_state:
    st.session_state.active_event = available_events[0] if available_events else ""

for i, ev in enumerate(available_events):
    col_idx = i % 6
    if cols_ev[col_idx].button(ev, key=f"btn_ev_{ev}", type="primary" if st.session_state.active_event == ev else "secondary"):
        st.session_state.active_event = ev
        st.rerun()

selected_event = st.session_state.active_event
st.divider()
st.subheader(f"📌 Aktiewe Item: O/{selected_age} {selected_gender} - {selected_event}")

is_track = any(m in selected_event for m in ["m", "Hurdles", "Walk", "Relay"]) and not any(f in selected_event for f in ["Jump", "Put", "Discus", "Javelin"])
is_high_jump = "High Jump" in selected_event

athletes = fetch_athletes({"gender": selected_gender, "age_group": selected_age})
if not athletes.empty:
    athletes = athletes[athletes['events'].str.contains(selected_event, case=False, na=False)].copy()

# ==========================================
# OPSIE A: BAANITEMS (HEATS TOT 10 & TYD-POPUP)
# ==========================================
if is_track:
    st.markdown("### 🏃 Baanitem Invoer (Dinamiese Heats & Tye)")
    
    col_h_select, col_h_status = st.columns([2, 3])
    with col_h_select:
        heat_no = st.number_input("Kies Huidige Heat (1 tot 10)", min_value=1, max_value=10, value=1, step=1)
    
    if "heat_results" not in st.session_state:
        st.session_state.heat_results = {}

    with col_h_status:
        saved_heats = list(st.session_state.heat_results.keys())
        if saved_heats:
            st.info(f"💾 **Reeds Gestorde Heats vir hierdie item:** Heat {', Heat '.join(map(str, sorted(saved_heats)))}")
        else:
            st.caption("Nog geen heats vir hierdie item gestoor nie.")

    st.caption("Tik die 6 tye in en kies die atleet vir elke plek:")

    heat_data = []
    for pos in range(1, 7):
        c_pos, c_time, c_ath = st.columns([1, 2, 3])
        c_pos.markdown(f"**Plek {pos}**")
        t_val = c_time.text_input(f"Tyd P{pos}", key=f"h_{heat_no}_t_{pos}", placeholder="bv. 12,45", label_visibility="collapsed")
        
        ath_options = ["Geen Atleet / Oop"] + [f"{r['first_name']} {r['last_name']} ({r['school']})" for _, r in athletes.iterrows()] if not athletes.empty else ["Geen Atlete"]
        selected_ath_str = c_ath.selectbox(f"Atleet P{pos}", ath_options, key=f"h_{heat_no}_a_{pos}", label_visibility="collapsed")
        
        if t_val and selected_ath_str != "Geen Atleet / Oop":
            heat_data.append({"place_in_heat": pos, "time": t_val, "athlete_str": selected_ath_str})

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(f"💾 Stoor Heat {heat_no}"):
            if heat_data:
                st.session_state.heat_results[heat_no] = heat_data
                st.success(f"Heat {heat_no} se uitslae gestoor! Jy kan nou na die volgende heat beweeg of die item finaliseer.")
                st.rerun()
            else:
                st.warning("Voer ten minste een tyd en atleet in voor stoor.")
            
    with col_btn2:
        if st.button("🏆 Finaliseer & Publiseer Totale Item Uitslae", type="primary"):
            if st.session_state.heat_results:
                all_entries = []
                for h_num, h_list in st.session_state.heat_results.items():
                    for item in h_list:
                        ath_name = item['athlete_str'].split(" (")[0]
                        match_ath = athletes[athletes.apply(lambda r: f"{r['first_name']} {r['last_name']}" == ath_name, axis=1)]
                        if not match_ath.empty:
                            row_a = match_ath.iloc[0]
                            clean_t = item['time'].replace(",", ".")
                            try:
                                num_val = float(clean_t)
                            except:
                                num_val = 999.0
                            all_entries.append({
                                "athlete_id": row_a['id'],
                                "name": ath_name,
                                "school": row_a['school'],
                                "result_value": item['time'],
                                "parsed_val": num_val,
                                "asa_points": max(10, int(1000 - ((num_val - 10.0) * 35)))
                            })
                # Rangskik alle heats se tye saam (van vinnigste na stadigste)
                all_entries.sort(key=lambda x: x['parsed_val'])
                for rk, res in enumerate(all_entries, 1):
                    res['place'] = rk
                
                save_event_results(selected_event, selected_gender, selected_age, all_entries)
                st.success("Item gefinaliseer en amptelike uitslae gepubliseer vir Medaljes!")
                st.session_state.heat_results = {}
                st.rerun()
            else:
                st.warning("Stoor asseblief ten minste een heat voor finalisering.")

# ==========================================
# OPSIE B: HOOGSPRING (AANPASBARE HOOGTE-STYG)
# ==========================================
elif is_high_jump:
    st.markdown("### 🦘 Hoogspring Beoordeling")
    if "hj_height" not in st.session_state:
        st.session_state.hj_height = 1.10

    st.markdown(f"### Huidige Lat Hoogte: **{st.session_state.hj_height:.2f} m**")
    
    # Aanpasbare styg-knoppies
    c_inc1, c_inc2, c_inc3, c_custom = st.columns([1, 1, 1, 2])
    with c_inc1:
        if st.button("⬆️ +2 cm"):
            st.session_state.hj_height += 0.02
            st.rerun()
    with c_inc2:
        if st.button("⬆️ +3 cm"):
            st.session_state.hj_height += 0.03
            st.rerun()
    with c_inc3:
        if st.button("⬆️ +5 cm"):
            st.session_state.hj_height += 0.05
            st.rerun()
    with c_custom:
        custom_cm = st.number_input("Skuiwer met spesifieke cm (+/-)", value=0, step=1)
        if st.button("Skuiwer Lat"):
            st.session_state.hj_height += (custom_cm / 100.0)
            st.rerun()

    st.divider()
    st.caption(f"Aantekening vir Hoogte: **{st.session_state.hj_height:.2f}m**")
    
    with st.form("hj_form"):
        hj_results = []
        for idx, row in athletes.iterrows():
            c_name, c_poging = st.columns([2, 2])
            c_name.markdown(f"**{row['first_name']} {row['last_name']}** (`{row['school']}`)")
            status = c_poging.radio(f"Status vir {row['first_name']}", ["O (Slaag)", "X (Misluk)", "P (Pass)"], key=f"hj_{row['id']}", horizontal=True)
            
            hj_results.append({
                "athlete_id": row['id'],
                "name": f"{row['first_name']} {row['last_name']}",
                "school": row['school'],
                "result_value": f"{st.session_state.hj_height:.2f}m" if "O" in status else "Geen",
                "status": status
            })
            st.divider()
        
        if st.form_submit_button("🔒 Stoor Hierdie Hoogte se Pogings"):
            st.success("Pogings aangeteken!")

# ==========================================
# OPSIE C: ALGEMENE VELDITEMS (AFSTANDE)
# ==========================================
else:
    st.markdown("### 🏋️ Velditem Invoer (Afstande)")
    with st.form("field_form"):
        field_entries = []
        for idx, row in athletes.iterrows():
            c_n, c_in = st.columns([2, 2])
            c_n.markdown(f"**{row['first_name']} {row['last_name']}** (`{row['school']}`)")
            val_in = c_in.text_input("Beste Afstand (m)", key=f"f_{row['id']}", placeholder="bv. 8,45")
            
            try:
                num_v = float(val_in.replace(",", ".")) if val_in else 0.0
            except:
                num_v = 0.0
                
            field_entries.append({
                "athlete_id": row['id'],
                "name": f"{row['first_name']} {row['last_name']}",
                "school": row['school'],
                "result_value": val_in,
                "parsed_val": num_v,
                "asa_points": int(num_v * 180)
            })
        
        if st.form_submit_button("🔒 Stoor & Rangskik Velditem", type="primary"):
            valid_f = [f for f in field_entries if f['parsed_val'] > 0]
            valid_f.sort(key=lambda x: x['parsed_val'], reverse=True)
            for rk, res in enumerate(valid_f, 1):
                res['place'] = rk
            save_event_results(selected_event, selected_gender, selected_age, valid_f)
            st.success("Velditem uitslae suksesvol gesinkroniseer en gerangskik!")
            st.rerun()

# Vertoon Amptelike Uitslae
st.divider()
st.subheader("🥇 Gepubliseerde Uitslae vir Hierdie Item")
captured_df = fetch_event_results(selected_event, selected_gender, selected_age)
if not captured_df.empty:
    st.dataframe(captured_df, use_container_width=True)
else:
    st.info("Nog geen uitslae vir hierdie item gefinaliseer nie.")
