import streamlit as st
import pandas as pd
from db import insert_athletes, fetch_athletes

st.set_page_config(page_title="Setup & Import", page_icon="📋", layout="wide")
st.title("📋 Meet Setup & Athlete Registration")

tab1, tab2, tab3 = st.tabs(["📤 Bulk Import (CSV/Excel)", "✍️ Manual Entry", "🗃️ Registered Athletes"])

with tab1:
    st.subheader("Upload Athlete Roster")
    st.info("Required columns: `first_name`, `last_name`, `school`, `gender`, `age_group`, `events` (comma-separated).")
    
    sample_df = pd.DataFrame([
        {"first_name": "Johan", "last_name": "Botha", "school": "Swartland", "gender": "Seuns", "age_group": "u/13", "events": "100m, High Jump"},
        {"first_name": "Anika", "last_name": "Smit", "school": "Vredenburg", "gender": "Dogters", "age_group": "u/12", "events": "Shot Put, 800m"}
    ])
    st.download_button(
        label="📥 Download CSV Template",
        data=sample_df.to_csv(index=False),
        file_name="athlete_import_template.csv",
        mime="text/csv"
    )

    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
            st.write("Preview:")
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("🚀 Register All Athletes", type="primary"):
                insert_athletes(df)
                st.success(f"Registered {len(df)} athletes!")
                st.rerun()
        except Exception as e:
            st.error(f"Error reading file: {e}")

with tab2:
    st.subheader("Add Athlete / Late Entry")
    with st.form("manual_athlete_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            school = st.text_input("School / Team")
        with col2:
            gender = st.selectbox("Gender", ["Seuns", "Dogters"])
            age_group = st.selectbox("Age Group", ["u/7", "u/8", "u/9", "u/10", "u/11", "u/12", "u/13", "u/14", "u/15", "u/17", "u/19"])
            events = st.text_input("Events (comma-separated)", placeholder="e.g., High Jump, 100m")
            
        if st.form_submit_button("Register Athlete"):
            if first_name and last_name and school:
                new_athlete = pd.DataFrame([{
                    "first_name": first_name,
                    "last_name": last_name,
                    "school": school,
                    "gender": gender,
                    "age_group": age_group,
                    "events": events
                }])
                insert_athletes(new_athlete)
                st.success(f"Added {first_name} {last_name} ({school})!")
                st.rerun()
            else:
                st.warning("Please complete all required fields.")

with tab3:
    st.subheader("Current Registered Athletes")
    athletes_df = fetch_athletes()
    if not athletes_df.empty:
        st.dataframe(athletes_df, use_container_width=True)
        st.caption(f"Total Athletes: {len(athletes_df)}")
    else:
        st.info("No athletes registered yet.")