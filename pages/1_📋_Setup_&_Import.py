import io
import streamlit as st
import pandas as pd
from db import insert_athletes, fetch_athletes
from constants import AGE_GROUPS, get_events_for_age_and_gender, ALL_DISCIPLINES

st.set_page_config(page_title="Setup & Import", page_icon="📋", layout="wide")
st.title("📋 Primary School Meet Setup & Registration")

tab1, tab2, tab3 = st.tabs(["📤 Bulk Import (Excel/CSV)", "✍️ Manual Entry", "🗃️ Registered Athletes"])

with tab1:
    st.subheader("Upload Primary School Roster")
    st.info("Download the Excel template below. Simply fill in athlete details and check/mark the event columns with `x` or `TRUE`.")
    
    # Generate interactive Excel template with event checkboxes/columns
    def generate_excel_template():
        buffer = io.BytesIO()
        template_rows = [
            {
                "first_name": "Johan", "last_name": "Botha", "school": "Swartland", 
                "gender": "Seuns", "age_group": "u/13", "100m": "x", "High Jump": "x"
            },
            {
                "first_name": "Anika", "last_name": "Smit", "school": "Vredenburg", 
                "gender": "Dogters", "age_group": "u/12", "Shot Put": "x", "1200m": "x"
            }
        ]
        
        base_cols = ["first_name", "last_name", "school", "gender", "age_group"]
        full_cols = base_cols + ALL_DISCIPLINES
        
        df_template = pd.DataFrame(template_rows)
        for col in ALL_DISCIPLINES:
            if col not in df_template.columns:
                df_template[col] = ""
                
        df_template = df_template[full_cols]
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_template.to_excel(writer, index=False, sheet_name="Athlete Registration")
            
        buffer.seek(0)
        return buffer

    st.download_button(
        label="📥 Download Excel Registration Sheet Template",
        data=generate_excel_template(),
        file_name="Primary_School_Athlete_Registration_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded_file = st.file_uploader("Upload Completed Excel or CSV File", type=["xlsx", "xls", "csv"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                raw_df = pd.read_csv(uploaded_file)
            else:
                raw_df = pd.read_excel(uploaded_file)
                
            # Process wide-format event checkboxes into a unified events list
            processed_rows = []
            for _, row in raw_df.iterrows():
                athlete_events = []
                for col in raw_df.columns:
                    if col in ALL_DISCIPLINES:
                        val = str(row[col]).strip().lower()
                        if val in ['x', 'true', '1', 'yes', 'y', 'x']:
                            athlete_events.append(col)
                
                # Check if events were provided in a single comma-separated column instead
                if 'events' in raw_df.columns and pd.notna(row['events']):
                    athlete_events.extend([e.strip() for e in str(row['events']).split(',')])
                    
                processed_rows.append({
                    "first_name": row.get("first_name", ""),
                    "last_name": row.get("last_name", ""),
                    "school": row.get("school", ""),
                    "gender": row.get("gender", ""),
                    "age_group": row.get("age_group", ""),
                    "events": ", ".join(sorted(list(set(athlete_events))))
                })
                
            clean_df = pd.DataFrame(processed_rows)
            st.write("Preview of Parsed Athletes:")
            st.dataframe(clean_df, use_container_width=True)
            
            if st.button("🚀 Register All Athletes", type="primary"):
                insert_athletes(clean_df)
                st.success(f"Successfully registered {len(clean_df)} athletes!")
                st.rerun()
        except Exception as e:
            st.error(f"Error reading file: {e}")

with tab2:
    st.subheader("Add Single Athlete / Late Entry")
    with st.form("manual_athlete_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            school = st.text_input("School / Team Name")
            gender = st.selectbox("Gender", ["Seuns", "Dogters"])
        with col2:
            age_group = st.selectbox("Age Group", AGE_GROUPS)
            valid_events = get_events_for_age_and_gender(age_group, gender)
            selected_events = st.multiselect(f"Select Events for {age_group} {gender}", valid_events)
            
        if st.form_submit_button("Register Athlete"):
            if first_name and last_name and school and selected_events:
                events_str = ", ".join(selected_events)
                new_athlete = pd.DataFrame([{
                    "first_name": first_name,
                    "last_name": last_name,
                    "school": school,
                    "gender": gender,
                    "age_group": age_group,
                    "events": events_str
                }])
                insert_athletes(new_athlete)
                st.success(f"Added {first_name} {last_name} ({school}) for {events_str}!")
                st.rerun()
            else:
                st.warning("Please fill in all required fields and select at least one event.")

with tab3:
    st.subheader("Current Registered Athletes")
    athletes_df = fetch_athletes()
    if not athletes_df.empty:
        st.dataframe(athletes_df, use_container_width=True)
        st.caption(f"Total Athletes: {len(athletes_df)}")
    else:
        st.info("No athletes registered yet.")