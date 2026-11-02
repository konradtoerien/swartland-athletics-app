import io
import streamlit as st
import pandas as pd
from db import fetch_athletes, insert_athletes
from constants import AGE_GROUPS, get_events_for_age_and_gender
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="Draw Sheets", page_icon="📄", layout="wide")
st.title("📄 Primary School Draw Sheets")

col1, col2, col3 = st.columns(3)
with col1:
    selected_age = st.selectbox("Age Group", AGE_GROUPS)
with col2:
    selected_gender = st.selectbox("Gender", ["Seuns", "Dogters"])
with col3:
    available_events = get_events_for_age_and_gender(selected_age, selected_gender)
    selected_event = st.selectbox("Discipline / Event", available_events if available_events else ["No events available"])

st.divider()

all_athletes = fetch_athletes({"gender": selected_gender, "age_group": selected_age})

if not all_athletes.empty and selected_event and selected_event != "No events available":
    matching_athletes = all_athletes[all_athletes['events'].str.contains(selected_event, case=False, na=False)].copy()
else:
    matching_athletes = pd.DataFrame()

st.subheader(f"Draw Sheet: {selected_age} {selected_gender} - {selected_event}")

if not matching_athletes.empty:
    matching_athletes.reset_index(drop=True, inplace=True)
    matching_athletes.index += 1
    matching_athletes.index.name = "Pos / Lane"
    
    st.table(matching_athletes[['first_name', 'last_name', 'school']])

    def generate_draw_pdf(event, gender, age, df):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()

        title_text = f"<b>OFFICIAL DRAW SHEET: {age} {gender} - {event}</b>"
        elements.append(Paragraph(title_text, styles['Title']))
        elements.append(Spacer(1, 15))

        table_data = [["Lane / Pos", "Athlete Name", "School", "Official Score / Notes"]]
        for idx, row in df.iterrows():
            name = f"{row['first_name']} {row['last_name']}"
            table_data.append([str(idx), name, row['school'], ""])

        t = Table(table_data, colWidths=[60, 180, 140, 140])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F2937")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer

    pdf_bytes = generate_draw_pdf(selected_event, selected_gender, selected_age, matching_athletes)
    st.download_button(
        label="🖨️ Download Printable PDF Draw Sheet",
        data=pdf_bytes,
        file_name=f"DrawSheet_{selected_age}_{selected_gender}_{selected_event}.pdf",
        mime="application/pdf"
    )
else:
    st.warning("No registered athletes found for this event combination.")

with st.expander("➕ Add Late Walk-On Athlete"):
    with st.form("late_entry_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        l_first = c1.text_input("First Name")
        l_last = c2.text_input("Last Name")
        l_school = c3.text_input("School")
        
        if st.form_submit_button("Add to Draw Sheet"):
            if l_first and l_last and l_school and selected_event != "No events available":
                late_df = pd.DataFrame([{
                    "first_name": l_first,
                    "last_name": l_last,
                    "school": l_school,
                    "gender": selected_gender,
                    "age_group": selected_age,
                    "events": selected_event
                }])
                insert_athletes(late_df)
                st.success(f"Added {l_first} {l_last}!")
                st.rerun()