import io
import os
import streamlit as st
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenPyxlImage
from db import get_local_connection
from constants import (
    AGE_GROUPS, 
    get_events_for_age_and_gender, 
    apply_swartland_theme, 
    NAVY_HEADER,
    LOGO_PATH
)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Program", page_icon="📅", layout="wide")
apply_swartland_theme()

st.title("📅 Byeenkoms Program & Tydrooster")

def init_program_db():
    conn = get_local_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_program (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_no INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            age_group TEXT NOT NULL,
            gender TEXT NOT NULL,
            event_name TEXT NOT NULL,
            venue TEXT NOT NULL,
            status TEXT DEFAULT 'Wagtend'
        )
    ''')
    conn.commit()
    conn.close()

init_program_db()

def fetch_program():
    conn = get_local_connection()
    df = pd.read_sql_query("SELECT * FROM event_program ORDER BY item_no ASC", conn)
    conn.close()
    return df

def save_program_item(item_no, start_time, age_group, gender, event_name, venue, status="Wagtend"):
    conn = get_local_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO event_program (item_no, start_time, age_group, gender, event_name, venue, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (item_no, start_time, age_group, gender, event_name, venue, status))
    conn.commit()
    conn.close()

def update_program_bulk(df):
    conn = get_local_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM event_program")
    for _, r in df.iterrows():
        cursor.execute('''
            INSERT INTO event_program (item_no, start_time, age_group, gender, event_name, venue, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (r.get('Item No', r.get('item_no', 1)), 
              r.get('Begin Tyd', r.get('start_time', '08:00')), 
              r.get('Ouderdom', r.get('age_group', '13')), 
              r.get('Geslag', r.get('gender', 'Seuns')), 
              r.get('Item', r.get('event_name', '')), 
              r.get('Plek', r.get('venue', 'Hoofbaan')), 
              r.get('Status', r.get('status', 'Wagtend'))))
    conn.commit()
    conn.close()

tab1, tab2, tab3 = st.tabs(["📋 Amptelike Program", "📤 Import / Export Program (Excel)", "✍️ Voeg Item By"])

with tab1:
    st.subheader("Dag se Tydrooster")
    prog_df = fetch_program()
    
    if not prog_df.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            venue_filter = st.selectbox("Filter volgens Baan/Plek", ["Alle Plekke"] + sorted(list(prog_df['venue'].unique())))
        with col_f2:
            status_filter = st.selectbox("Filter volgens Status", ["Alle Statusse", "Wagtend", "Besig", "Voltooi"])

        filtered_prog = prog_df.copy()
        if venue_filter != "Alle Plekke":
            filtered_prog = filtered_prog[filtered_prog['venue'] == venue_filter]
        if status_filter != "Alle Statusse":
            filtered_prog = filtered_prog[filtered_prog['status'] == status_filter]

        display_df = filtered_prog[['item_no', 'start_time', 'age_group', 'gender', 'event_name', 'venue', 'status']].copy()
        display_df.columns = ["Item No", "Tyd", "Ouderdom", "Geslag", "Item", "Plek", "Status"]
        
        st.dataframe(display_df, use_container_width=True)
        
        st.divider()
        st.subheader("🖨️ Drukbare Program PDF")
        
        def generate_program_pdf(df):
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
            elements.append(Paragraph("LAERSKOOL SWARTLAND - AMPTELIKE BYEENKOMS PROGRAM", title_style))
            elements.append(Spacer(1, 10))

            table_data = [["No", "Tyd", "Oud.", "Geslag", "Item", "Plek", "Status"]]
            for _, r in df.iterrows():
                table_data.append([
                    str(r['item_no']),
                    str(r['start_time']),
                    f"O/{r['age_group']}",
                    str(r['gender']),
                    str(r['event_name']),
                    str(r['venue']),
                    str(r['status'])
                ])

            t = Table(table_data, colWidths=[35, 55, 45, 55, 140, 110, 60])
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

        pdf_program = generate_program_pdf(prog_df)
        st.download_button(
            label="🖨️ Laai Amptelike Program PDF Af",
            data=pdf_program,
            file_name="Swartland_Atletiek_Program.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Nog geen items op die program ingesleutel nie.")

with tab2:
    st.subheader("Laai Program in via Excel / Laai Dokumment Af")
    st.info("Voer die hele dag se tydrooster vinnig in via Excel.")
    
    def generate_program_excel_template():
        buffer = io.BytesIO()
        template_data = [
            {"Item No": 1, "Begin Tyd": "08:00", "Ouderdom": "13", "Geslag": "Seuns", "Item": "100m", "Plek": "Hoofbaan", "Status": "Wagtend"},
            {"Item No": 2, "Begin Tyd": "08:05", "Ouderdom": "12", "Geslag": "Dogters", "Item": "High Jump", "Plek": "Hoogspring Mat A", "Status": "Wagtend"},
            {"Item No": 3, "Begin Tyd": "08:15", "Ouderdom": "11", "Geslag": "Seuns", "Item": "Shot Put", "Plek": "Gewigstoot C", "Status": "Wagtend"}
        ]
        df_temp = pd.DataFrame(template_data)
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_temp.to_excel(writer, index=False, sheet_name="Program", startrow=4)
            worksheet = writer.sheets["Program"]
            
            if os.path.exists(LOGO_PATH):
                img = OpenPyxlImage(LOGO_PATH)
                img.width = 50
                img.height = 65
                worksheet.add_image(img, "A1")
                
            worksheet.cell(row=2, column=3, value="LAERSKOOL SWARTLAND - AMPTELIKE PROGRAMDOKUMENT").font = Font(name="Arial", size=13, bold=True, color=NAVY_HEADER)

            header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
            thin_border = Side(border_style="thin", color="CCCCCC")
            box_border = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)
            align_center = Alignment(horizontal="center", vertical="center")

            for col_num in range(1, len(df_temp.columns) + 1):
                cell = worksheet.cell(row=5, column=col_num)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = align_center
                cell.border = box_border

            for row_idx in range(6, 40):
                for col_idx in range(1, len(df_temp.columns) + 1):
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    cell.border = box_border
                    cell.alignment = align_center

            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = max(max_len + 5, 14)

        buffer.seek(0)
        return buffer

    st.download_button(
        label="📥 Laai Program Excel-Dokument Af",
        data=generate_program_excel_template(),
        file_name="Swartland_Atletiek_Program_Dokument.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded_prog_file = st.file_uploader("Laai Voltooide Program Excel In", type=["xlsx", "csv"])
    if uploaded_prog_file:
        try:
            if uploaded_prog_file.name.endswith(".csv"):
                p_df = pd.read_csv(uploaded_prog_file)
            else:
                p_df = pd.read_excel(uploaded_prog_file, header=4 if "LAERSKOOL" in str(pd.read_excel(uploaded_prog_file).iloc[0:3]) else 0)
                
            st.write("Voorbeeld van Program Ingeloof:")
            st.dataframe(p_df, use_container_width=True)
            
            if st.button("🚀 Stoor en Vervang Program", type="primary"):
                update_program_bulk(p_df)
                st.success("Program suksesvol gelaai en opgedateer!")
                st.rerun()
        except Exception as e:
            st.error(f"Fout met inlees van lêer: {e}")

with tab3:
    st.subheader("Voeg Enkele Item by Program By")
    with st.form("single_program_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            p_no = st.number_input("Item Nommer", min_value=1, value=len(prog_df)+1 if not prog_df.empty else 1)
            p_time = st.text_input("Begin Tyd", value="08:00")
        with c2:
            p_age = st.selectbox("Ouderdomsgroep", AGE_GROUPS, index=7)
            p_gender = st.selectbox("Geslag", ["Seuns", "Dogters"])
        with c3:
            p_events = get_events_for_age_and_gender(p_age, p_gender)
            p_event = st.selectbox("Item / Dissipline", p_events)
            p_venue = st.text_input("Plek / Baan", value="Hoofbaan")

        if st.form_submit_button("Voeg by Program"):
            save_program_item(p_no, p_time, p_age, p_gender, p_event, p_venue)
            st.success(f"Item {p_no} ({p_event} O/{p_age} {p_gender}) bygevoeg!")
            st.rerun()