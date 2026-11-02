import io
import os
import streamlit as st
import pandas as pd
from db import fetch_all_results
from constants import apply_swartland_theme, LOGO_PATH
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Verslae", page_icon="🖨️", layout="wide")
apply_swartland_theme()

st.title("🖨️ Byeenkoms Verslae & Puntetabelle")

results_df = fetch_all_results()

tab1, tab2, tab3 = st.tabs(["🏆 Totale Spanpunte", "🌟 Victor & Victrix Ludorum", "📄 Amptelike PDF Uitslagboekie"])

with tab1:
    st.subheader("Totale Skoolpunte (ASA Punte Totaal)")
    if not results_df.empty:
        school_points = results_df.groupby('school')['asa_points'].sum().reset_index()
        school_points.columns = ["Skool", "Totale ASA Punte"]
        school_points.sort_values(by="Totale ASA Punte", ascending=False, inplace=True)
        school_points.reset_index(drop=True, inplace=True)
        school_points.index += 1
        
        st.table(school_points)
    else:
        st.info("Nog geen uitslae om spanpunte te bereken nie.")

with tab2:
    st.subheader("Top Atletiese Prestasies (Victor / Victrix Ludorum Kandidaten)")
    if not results_df.empty:
        top_athletes = results_df.groupby(['athlete_name', 'school', 'gender', 'age_group'])['asa_points'].sum().reset_index()
        top_athletes.columns = ["Atleet Naam", "Skool", "Geslag", "Ouderdom", "Totale ASA Punte"]
        top_athletes.sort_values(by="Totale ASA Punte", ascending=False, inplace=True)
        top_athletes.reset_index(drop=True, inplace=True)
        top_athletes.index += 1
        
        st.dataframe(top_athletes.head(10), use_container_width=True)
    else:
        st.info("Nog geen uitslae om topsprekers te toon nie.")

with tab3:
    st.subheader("Laai Amptelike Byeenkoms Uitslagboekie Af")
    st.write("Genereer 'n volledige PDF-opsomming van al die uitslae wat vandag vasgelê is.")
    
    def generate_full_results_pdf(df):
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
            fontSize=16,
            textColor=colors.HexColor("#0A192F"),
            spaceAfter=15
        )
        elements.append(Paragraph("LAERSKOOL SWARTLAND - AMPTELIKE BYEENKOMS UITSLAE", title_style))
        elements.append(Spacer(1, 10))

        table_data = [["Plek", "Atleet Naam", "Skool", "Item", "Oud.", "Uitslag", "Punte"]]
        for _, row in df.iterrows():
            table_data.append([
                str(row.get('place', '')),
                str(row.get('athlete_name', '')),
                str(row.get('school', '')),
                str(row.get('event_name', '')),
                str(row.get('age_group', '')),
                str(row.get('result_value', '')),
                str(row.get('asa_points', ''))
            ])

        t = Table(table_data, colWidths=[40, 130, 110, 90, 40, 60, 50])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0A192F")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#F4C430")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer

    if not results_df.empty:
        pdf_bytes = generate_full_results_pdf(results_df)
        st.download_button(
            label="🖨️ Laai Volledige Uitslagboekie PDF Af",
            data=pdf_bytes,
            file_name="Swartland_Atletiek_Byeenkoms_Uitslae.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Geen uitslae beskikbaar om 'n PDF te genereer nie.")
