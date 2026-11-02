import streamlit as st
import pandas as pd
from db import fetch_athletes, fetch_event_record, save_event_results
from constants import AGE_GROUPS, get_events_for_age_and_gender

st.set_page_config(page_title="Officiating", page_icon="⏱️", layout="wide")
st.title("⏱️ Field & Track Officiating")

col1, col2, col3 = st.columns(3)
with col1:
    selected_age = st.selectbox("Age Group", AGE_GROUPS)
with col2:
    selected_gender = st.selectbox("Gender", ["Seuns", "Dogters"])
with col3:
    available_events = get_events_for_age_and_gender(selected_age, selected_gender)
    selected_event = st.selectbox("Discipline", available_events if available_events else ["No events available"])

st.divider()

if selected_event and selected_event != "No events available":
    record_info = fetch_event_record(selected_event, selected_gender, selected_age)
    if record_info:
        st.info(f"🏆 **Current Record:** {record_info['record_value']} by {record_info['holder']} ({record_info['year']})")
    else:
        st.caption("No benchmark record set for this event.")

    athletes = fetch_athletes({"gender": selected_gender, "age_group": selected_age})
    if not athletes.empty:
        athletes = athletes[athletes['events'].str.contains(selected_event, case=False, na=False)].copy()

    if not athletes.empty:
        st.subheader(f"Record Results: {selected_age} {selected_gender} - {selected_event}")
        
        def calculate_asa_points(event, value):
            try:
                val = float(value)
                if "m" in event and "Hurdles" not in event and "Walk" not in event:
                    return max(0, int(1000 - (val * 45)))
                else:
                    return max(0, int(val * 120))
            except:
                return 0

        results_data = []
        
        with st.form("results_entry_form"):
            for idx, row in athletes.iterrows():
                st.markdown(f"**{row['first_name']} {row['last_name']}** ({row['school']})")
                c1, c2 = st.columns([2, 1])
                with c1:
                    res_val = st.text_input("Result (e.g., 12.4s or 4.52m)", key=f"res_{row['id']}")
                with c2:
                    points = calculate_asa_points(selected_event, res_val) if res_val else 0
                    st.metric("Est. ASA Points", points)
                
                results_data.append({
                    "athlete_id": row['id'],
                    "name": f"{row['first_name']} {row['last_name']}",
                    "school": row['school'],
                    "result_value": res_val,
                    "asa_points": points
                })
                st.divider()

            submit = st.form_submit_button("🔒 Submit & Lock Event Results", type="primary")
            
            if submit:
                save_event_results(selected_event, selected_gender, selected_age, results_data)
                st.success("Results submitted and synced successfully!")
    else:
        st.warning("No registered athletes found for this event combination.")
else:
    st.info("Select a valid age group and discipline to start recording results.")