import io
import os
import streamlit as st
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenPyxlImage
from db import fetch_all_records, insert_records, delete_record
from constants import (
    AGE_GROUPS, 
    ALL_DISCIPLINES, 
    apply_swartland_theme,
    NAVY_HEADER,
    LOGO_PATH
)

st.set_page_config(page_title="Rekords", page_icon="🏆", layout="wide")
apply_swartland_theme()

st.title("🏆 Rekordbestuur")

tab1, tab2, tab3 = st.tabs(["📊 Huidige Rekords", "📤 Bulk Invoer & Uitvoer (Excel)", "✍️ Handmatige Invoer"])

with tab1:
    st.subheader("Bestaande Byeenkomsrekords")
    records_df = fetch_all_records()
    
    if not records_df.empty:
        clean_df = records_df.copy()
        drop_cols = [c for c in ['id'] if c in clean_df.columns]
        clean_df.drop(columns=drop_cols, inplace=True)
        
        clean_df.rename(columns={
            "event_name": "Item",
            "gender": "Geslag",
            "age_group": "Ouderdom",
            "record_value": "Tyd of Afstand",
            "holder": "Skool of Atleet",
            "year": "Jaar"
        }, inplace=True)
        
        st.dataframe(clean_df, use_container_width=True)
        st.caption(f"Totaal Aangetekende Rekords: {len(records_df)}")
        
        with st.expander("🗑️ Skrap 'n Rekord"):
            col_sel, col_act = st.columns([3, 1])
            with col_sel:
                rec_to_del = st.selectbox(
                    "Kies rekord om te verwyder:",
                    options=records_df.apply(lambda r: f"{r['event_name']} - O/{r['age_group']} {r['gender']} ({r['holder']})", axis=1)
                )
            with col_act:
                if st.button("Skrap Hierdie Rekord"):
                    idx = records_df.apply(lambda r: f"{r['event_name']} - O/{r['age_group']} {r['gender']} ({r['holder']})", axis=1).tolist().index(rec_to_del)
                    rec_id = records_df.iloc[idx]['id']
                    delete_record(rec_id)
                    st.success("Rekord suksesvol verwyder!")
                    st.rerun()
    else:
        st.info("Nog geen rekords in die stelsel geregistreer nie.")

with tab2:
    st.subheader("Laai Rekords In / Voer Uit via Excel")
    st.info("Laai die rekord-dokument af, vul of wysig die rekords, en laai dit weer op.")
    
    def generate_records_excel():
        buffer = io.BytesIO()
        records_df = fetch_all_records()
        
        if records_df.empty:
            data = [
                {"Item": "100m", "Ouderdom": "13", "Geslag": "Seuns", "Tyd of Afstand": "11.85", "Skool of Atleet": "Laerskool Swartland", "Jaar": 2024},
                {"Item": "Shot Put", "Ouderdom": "12", "Geslag": "Dogters", "Tyd of Afstand": "10.42", "Skool of Atleet": "Laerskool Vredenburg", "Jaar": 2023}
            ]
            df = pd.DataFrame(data)
        else:
            df = records_df.copy()
            df.rename(columns={
                "event_name": "Item",
                "gender": "Geslag",
                "age_group": "Ouderdom",
                "record_value": "Tyd of Afstand",
                "holder": "Skool of Atleet",
                "year": "Jaar"
            }, inplace=True)
            if 'id' in df.columns:
                df.drop(columns=['id'], inplace=True)
                
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Rekords", startrow=4)
            worksheet = writer.sheets["Rekords"]
            
            if os.path.exists(LOGO_PATH):
                img = OpenPyxlImage(LOGO_PATH)
                img.width = 50
                img.height = 65
                worksheet.add_image(img, "A1")
                
            worksheet.cell(row=2, column=3, value="LAERSKOOL SWARTLAND - AMPTELIKE REKORDDOKUMENT").font = Font(name="Arial", size=13, bold=True, color=NAVY_HEADER)

            header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
            thin_border = Side(border_style="thin", color="CCCCCC")
            box_border = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)
            align_center = Alignment(horizontal="center", vertical="center")
            align_left = Alignment(horizontal="left", vertical="center")

            # Styl vir Kolomopskrifte (Rij 5)
            for col_num in range(1, len(df.columns) + 1):
                cell = worksheet.cell(row=5, column=col_num)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = align_center
                cell.border = box_border

            # Data-rye
            for row_idx in range(6, len(df) + 20):
                for col_idx in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    cell.border = box_border
                    cell.alignment = align_left if col_idx in [1, 5] else align_center

            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = max(max_len + 5, 15)

        buffer.seek(0)
        return buffer

    st.download_button(
        label="📥 Laai Rekord Excel-Dokument Af",
        data=generate_records_excel(),
        file_name="Swartland_Atletiek_Rekords.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded_rec_file = st.file_uploader("Laai Gewysigde Rekord-Lêer In", type=["xlsx", "csv"])
    if uploaded_rec_file:
        try:
            if uploaded_rec_file.name.endswith(".csv"):
                rec_import_df = pd.read_csv(uploaded_rec_file)
            else:
                rec_import_df = pd.read_excel(uploaded_rec_file, header=4 if "LAERSKOOL" in str(pd.read_excel(uploaded_rec_file).iloc[0:3]) else 0)
                
            st.write("Voorbeeld van Ingeleesde Rekords:")
            st.dataframe(rec_import_df, use_container_width=True)
            
            if st.button("🚀 Stoor Alle Rekords", type="primary"):
                processed_recs = []
                for _, r in rec_import_df.iterrows():
                    item_val = r.get("Item", r.get("item", ""))
                    if not item_val or str(item_val).strip() == "nan":
                        continue
                    processed_recs.append({
                        "event_name": str(item_val).strip(),
                        "gender": "Seuns" if str(r.get("Geslag", r.get("geslag", "M"))).strip().lower().startswith(("s", "m", "b")) else "Dogters",
                        "age_group": str(r.get("Ouderdom", r.get("ouderdom", "13"))).strip(),
                        "record_value": str(r.get("Tyd of Afstand", r.get("tyd_of_afstand", "0"))).strip(),
                        "holder": str(r.get("Skool of Atleet", r.get("skool_of_atleet", ""))).strip(),
                        "year": int(r.get("Jaar", r.get("jaar", 2026)))
                    })
                insert_records(pd.DataFrame(processed_recs))
                st.success("Rekords suksesvol bygevoeg!")
                st.rerun()
        except Exception as e:
            st.error(f"Fout met inlees van lêer: {e}")

with tab3:
    st.subheader("Voeg Enkele Rekord Handmatig By")
    with st.form("single_record_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            rec_event = st.selectbox("Item / Dissipline", ALL_DISCIPLINES)
            rec_gender = st.selectbox("Geslag", ["Seuns", "Dogters"])
            rec_age = st.selectbox("Ouderdomsgroep", AGE_GROUPS)
        with c2:
            rec_val = st.text_input("Tyd of Afstand (bv. 11,85 of 12,45m)")
            rec_holder = st.text_input("Skool of Atleet Naam", placeholder="bv. Laerskool Swartland")
            rec_year = st.number_input("Jaar Aangeteken", min_value=1950, max_value=2030, value=2026)
            
        if st.form_submit_button("Stoor Rekord"):
            if rec_event and rec_val and rec_holder:
                new_rec = pd.DataFrame([{
                    "event_name": rec_event,
                    "gender": rec_gender,
                    "age_group": rec_age,
                    "record_value": rec_val,
                    "holder": rec_holder,
                    "year": rec_year
                }])
                insert_records(new_rec)
                st.success(f"Rekord vir {rec_event} O/{rec_age} {rec_gender} gestoor!")
                st.rerun()
            else:
                st.warning("Vul asseblief al die verpligte velde in.")