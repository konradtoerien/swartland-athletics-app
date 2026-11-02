import io
import os
import streamlit as st
import pandas as pd
from db import fetch_athletes, fetch_event_results, insert_athletes
from constants import AGE_GROUPS, get_events_for_age_and_gender, apply_swartland_theme, LOGO_PATH
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Lotingslyste", page_icon="📄", layout="wide")
apply_swartland_theme()

st.title("📄 Lotingslyste & Uitslae")

col1, col2, col3 = st.columns(3)
with col1:
    selected_age = st.selectbox("Ouderdomsgroep", AGE_GROUPS, index=7)
with col2:
    selected_gender = st.selectbox("Geslag", ["Seuns", "Dogters"])
with col3:
    available_events = get_events_for_age_and_gender(selected_age, selected_gender)
    selected_event = st.selectbox("Item / Dissipline", available_events if available_events else ["Geen items"])

st.divider()

all_athletes = fetch_athletes({"gender": selected_gender, "age_group": selected_age})

if not all_athletes.empty and selected_event and selected_event != "Geen items":
    matching_athletes = all_athletes[all_athletes['events'].str.contains(selected_event, case=False, na=False)].copy()
else:
    matching_athletes = pd.DataFrame()

st.subheader(f"Lotingslys: O/{selected_age} {selected_gender} - {selected_event}")

@st.dialog("👁️ Lotingslys Snelbesigtiging", width="large")
def preview_draw_sheet_dialog(event, gender, age, df):
    st.markdown(f"### 🏃 Laerskool Swartland - Amptelike Lotingslys")
    st.markdown(f"**Item:** O/{age} {gender} - {event}")
    st.divider()
    
    if not df.empty:
        view_df = df[['first_name', 'last_name', 'school']].copy()
        view_df.columns = ["Voornaam", "Van", "Skool"]
        view_df.index = range(1, len(view_df) + 1)
        view_df.index.name = "Baan / Pos"
        st.table(view_df)
    else:
        st.info("Geen atlete geregistreer vir hierdie item nie.")

if not matching_athletes.empty:
    matching_athletes.reset_index(drop=True, inplace=True)
    matching_athletes.index += 1
    matching_athletes.index.name = "Baan / Pos"
    
    # Netjiese Afrikaanse Opskrifte op skerm
    display_table = matching_athletes[['first_name', 'last_name', 'school']].copy()
    display_table.columns = ["Voornaam", "Van", "Skool"]
    st.table(display_table)

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("👁️ Bekyk Lotingslys (Pop-up)", type="secondary"):
            preview_draw_sheet_dialog(selected_event, selected_gender, selected_age, matching_athletes)
            
    with col_btn2:
        def generate_draw_pdf(event, gender, age, df):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            styles = getSampleStyleSheet()

            if os.path.exists(LOGO_PATH):
                logo_img = RLImage(LOGO_PATH, width=50, height=65)
                elements.append(logo_img)
                elements.append(Spacer(1, 10))

            title_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=colors.HexColor("#0A192F"),
                spaceAfter=10
            )
            elements.append(Paragraph(f"LAERSKOOL SWARTLAND - AMPTELIKE LOTINGSLYS", title_style))
            elements.append(Paragraph(f"<b>Item:</b> O/{age} {gender} - {event}", styles['Normal']))
            elements.append(Spacer(1, 12))

            table_data = [["Baan/Pos", "Atleet Naam", "Skool", "Amptelike Uitslag / Pogings"]]
            for idx, row in df.iterrows():
                name = f"{row['first_name']} {row['last_name']}"
                table_data.append([str(idx), name, row['school'], ""])

            t = Table(table_data, colWidths=[55, 175, 140, 150])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0A192F")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#F4C430")),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

            summary_title = ParagraphStyle(
                'SummaryHeader',
                parent=styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=11,
                textColor=colors.HexColor("#0A192F"),
                spaceAfter=5
            )
            elements.append(Paragraph("AMPTELIKE PRYSWENNERS & UITSLAE", summary_title))
            
            results_box_data = [
                ["Plek", "Atleet Naam", "Skool", "Tyd / Afstand", "Punte"],
                ["1ste Plek", "", "", "", ""],
                ["2de Plek", "", "", "", ""],
                ["3de Plek", "", "", "", ""],
                ["Nuwe Rekord?", "JA / NEE", "Nuwe Rekord Tyd/Afstand:", "", ""]
            ]
            res_table = Table(results_box_data, colWidths=[70, 175, 135, 80, 60])
            res_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#112240")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elements.append(res_table)

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_bytes = generate_draw_pdf(selected_event, selected_gender, selected_age, matching_athletes)
        st.download_button(
            label="🖨️ Drukbare PDF Lotingslys met Uitslaeblok",
            data=pdf_bytes,
            file_name=f"Lotingslys_O_{selected_age}_{selected_gender}_{selected_event}.pdf",
            mime="application/pdf"
        )
else:
    st.warning("Geen atlete gevind vir hierdie spesifieke item nie.")

st.divider()
st.subheader("📊 Uitslae vir Hierdie Item")

existing_results = fetch_event_results(selected_event, selected_gender, selected_age)
if not existing_results.empty:
    st.dataframe(existing_results, use_container_width=True)
else:
    st.info("Nog geen uitslae vir hierdie item ingedien nie.")