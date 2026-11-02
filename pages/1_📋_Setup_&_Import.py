import io
import os
import streamlit as st
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenPyxlImage
from db import insert_athletes, fetch_athletes, fetch_all_results, fetch_all_records, reset_database
from constants import (
    AGE_GROUPS, 
    get_events_for_age_and_gender, 
    ALL_DISCIPLINES, 
    normalize_age_group, 
    apply_swartland_theme,
    NAVY_HEADER,
    GOLD_ACCENT,
    LOGO_PATH
)

st.set_page_config(page_title="Inskrywings", page_icon="📋", layout="wide")
apply_swartland_theme()

st.title("📋 Laerskool Swartland - Inskrywings & Bestuur")

tab1, tab2, tab3, tab4 = st.tabs([
    "📤 Bulk Import (Excel/CSV)", 
    "✍️ Manual Entry", 
    "🗃️ Huidige Geregistreerde Atlete", 
    "⚙️ Stoor / Reset Byeenkoms Data"
])

TRACK_EVENTS = ["50m", "60m", "80m", "100m", "150m", "200m", "800m", "1200m", "1500m", "4x100m Relay"]
FIELD_EVENTS = ["Long Jump", "High Jump", "Shot Put", "Discus", "Javelin"]
HURDLE_EVENTS = ["70m Hurdles", "75m Hurdles", "80m Hurdles", "150m Hurdles", "200m Hurdles"]
WALK_EVENTS = ["1500m Walk"]

with tab1:
    st.subheader("Laai Atletieklys In")
    st.info("Laai die Excel-inskrywingsdokument af. Kies die **Seuns (M)** of **Dogters (F)** tab onderaan in Excel, vul atleetbesonderhede in en merk gekose items met 'x'.")
    
    def generate_styled_excel_template():
        buffer = io.BytesIO()
        base_cols = ["Ouderdom", "Voornaam", "Van", "Skool"]
        ordered_disciplines = [d for d in ALL_DISCIPLINES if d in TRACK_EVENTS] + \
                              [d for d in ALL_DISCIPLINES if d in FIELD_EVENTS] + \
                              [d for d in ALL_DISCIPLINES if d in HURDLE_EVENTS] + \
                              [d for d in ALL_DISCIPLINES if d in WALK_EVENTS]
                              
        full_cols = base_cols + ordered_disciplines

        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            for sheet_name in ["Seuns (M)", "Dogters (F)"]:
                sample_rows = [
                    {"Ouderdom": "13", "Voornaam": "Johan", "Van": "Botha", "Skool": "Laerskool Swartland", "100m": "x", "High Jump": "x"},
                    {"Ouderdom": "12", "Voornaam": "Karel", "Van": "Venter", "Skool": "Laerskool Swartland", "Shot Put": "x", "1200m": "x"}
                ]
                df_temp = pd.DataFrame(sample_rows)
                for c in ordered_disciplines:
                    if c not in df_temp.columns:
                        df_temp[c] = ""
                df_temp = df_temp[full_cols]
                
                df_temp.to_excel(writer, index=False, sheet_name=sheet_name, startrow=5)
                worksheet = writer.sheets[sheet_name]

                if os.path.exists(LOGO_PATH):
                    img = OpenPyxlImage(LOGO_PATH)
                    img.width = 50
                    img.height = 65
                    worksheet.add_image(img, "A1")

                worksheet.cell(row=2, column=3, value=f"LAERSKOOL SWARTLAND - INSKRYWINGSDOKUMENT ({sheet_name.upper()})").font = Font(name="Arial", size=12, bold=True, color=NAVY_HEADER)

                group_fill_track = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
                group_fill_field = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
                group_fill_hurdle = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
                group_fill_walk = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
                
                header_font_dark = Font(name="Arial", size=10, bold=True, color="000000")
                header_font_white = Font(name="Arial", size=10, bold=True, color="FFFFFF")
                header_fill_navy = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
                thin_border = Side(border_style="thin", color="CCCCCC")
                box_border = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)
                align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
                align_left = Alignment(horizontal="left", vertical="center")

                for c_idx, c_name in enumerate(full_cols, 1):
                    cell_grp = worksheet.cell(row=5, column=c_idx)
                    cell_grp.alignment = align_center
                    cell_grp.border = box_border
                    if c_name in TRACK_EVENTS:
                        cell_grp.value = "Track"
                        cell_grp.fill = group_fill_track
                        cell_grp.font = header_font_dark
                    elif c_name in FIELD_EVENTS:
                        cell_grp.value = "Field"
                        cell_grp.fill = group_fill_field
                        cell_grp.font = header_font_dark
                    elif c_name in HURDLE_EVENTS:
                        cell_grp.value = "Hurdles"
                        cell_grp.fill = group_fill_hurdle
                        cell_grp.font = header_font_dark
                    elif c_name in WALK_EVENTS:
                        cell_grp.value = "Walk"
                        cell_grp.fill = group_fill_walk
                        cell_grp.font = header_font_dark

                for c_idx, c_name in enumerate(full_cols, 1):
                    cell = worksheet.cell(row=6, column=c_idx)
                    cell.font = header_font_white
                    cell.fill = header_fill_navy
                    cell.alignment = align_center
                    cell.border = box_border

                for row_idx in range(7, 60):
                    for col_idx in range(1, len(full_cols) + 1):
                        cell = worksheet.cell(row=row_idx, column=col_idx)
                        cell.border = box_border
                        cell.alignment = align_center if col_idx in [1] or col_idx > 4 else align_left

                worksheet.column_dimensions['A'].width = 8
                worksheet.column_dimensions['B'].width = 14
                worksheet.column_dimensions['C'].width = 14
                worksheet.column_dimensions['D'].width = 16
                
                for col_idx in range(5, len(full_cols) + 1):
                    col_letter = worksheet.cell(row=6, column=col_idx).column_letter
                    worksheet.column_dimensions[col_letter].width = 7

        buffer.seek(0)
        return buffer

    st.download_button(
        label="📥 Laai Excel Inskrywingsdokument Af",
        data=generate_styled_excel_template(),
        file_name="Swartland_Atletiek_Inskrywingsdokument.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded_file = st.file_uploader("Laai Voltooide Inskrywingsdokument In", type=["xlsx", "xls", "csv"])
    if uploaded_file:
        try:
            processed_rows = []
            if uploaded_file.name.endswith(".csv"):
                sheets_dict = {"Inskrywings": pd.read_csv(uploaded_file)}
            else:
                xl = pd.ExcelFile(uploaded_file)
                sheets_dict = {sheet: xl.parse(sheet) for sheet in xl.sheet_names}
                
            for sheet_name, raw_df in sheets_dict.items():
                gender_from_sheet = "Seuns" if "seun" in sheet_name.lower() or "(m)" in sheet_name.lower() else "Dogters"
                
                header_row_idx = 0
                for r_i in range(min(6, len(raw_df))):
                    row_vals = [str(v).lower() for v in raw_df.iloc[r_i].values]
                    if "voornaam" in row_vals or "van" in row_vals or "ouderdom" in row_vals:
                        header_row_idx = r_i + 1
                        break
                        
                if header_row_idx > 0:
                    raw_df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=header_row_idx)
                    
                col_map = {c: str(c).strip().lower().replace(" ", "_") for c in raw_df.columns if pd.notna(c)}
                raw_df.rename(columns=col_map, inplace=True)
                
                for _, row in raw_df.iterrows():
                    athlete_events = []
                    for orig_col in raw_df.columns:
                        matched_disc = next((d for d in ALL_DISCIPLINES if str(d).lower() == str(orig_col).lower()), None)
                        if matched_disc:
                            val = str(row[orig_col]).strip().lower()
                            if val in ['x', 'true', '1', 'yes', 'y', 'ja']:
                                athlete_events.append(matched_disc)
                    
                    first_name = row.get("voornaam", row.get("first_name", ""))
                    last_name = row.get("van", row.get("last_name", ""))
                    if not first_name or str(first_name).strip() in ["nan", "Track", "Field", "Hurdles", "Walk"]:
                        continue
                        
                    school = row.get("skool", row.get("school", "Laerskool Swartland"))
                    age = normalize_age_group(row.get("ouderdom", row.get("age", row.get("age_group", "13"))))
                    
                    gender_val = str(row.get("geslag", row.get("gender", gender_from_sheet))).strip().lower()
                    gender = "Seuns" if gender_val.startswith(("m", "s", "b", "seun")) else "Dogters"
                    
                    processed_rows.append({
                        "first_name": str(first_name).strip().title(),
                        "last_name": str(last_name).strip().title(),
                        "school": str(school).strip(),
                        "gender": gender,
                        "age_group": age,
                        "events": ", ".join(sorted(list(set(athlete_events))))
                    })
                
            clean_df = pd.DataFrame(processed_rows)
            st.write("Voorbeeld van Ingeleesde Atlete:")
            
            display_preview = clean_df.copy()
            display_preview.columns = ["Voornaam", "Van", "Skool", "Geslag", "Ouderdom", "Items"]
            st.dataframe(display_preview, use_container_width=True)
            
            if st.button("🚀 Registreer Alle Atlete", type="primary"):
                insert_athletes(clean_df)
                st.success(f"{len(clean_df)} atlete suksesvol geregistreer!")
                st.rerun()
        except Exception as e:
            st.error(f"Fout met inlees van lêer: {e}")

with tab2:
    st.subheader("Enkel Atleet / Laat Inskrywing")
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("Voornaam")
        last_name = st.text_input("Van")
        school = st.text_input("Skool", value="Laerskool Swartland")
        gender_code = st.selectbox("Geslag", ["M (Seuns)", "F (Dogters)"])
        gender = "Seuns" if gender_code.startswith("M") else "Dogters"
    with col2:
        age_group = st.selectbox("Ouderdomsgroep", AGE_GROUPS, index=7)
        valid_events = get_events_for_age_and_gender(age_group, gender)
        selected_events = st.multiselect(f"Kies Items vir O/{age_group} ({gender})", valid_events)
        
    if st.button("Voeg Atleet By"):
        if first_name and last_name and school and selected_events:
            events_str = ", ".join(selected_events)
            new_athlete = pd.DataFrame([{
                "first_name": first_name.strip().title(),
                "last_name": last_name.strip().title(),
                "school": school.strip(),
                "gender": gender,
                "age_group": age_group,
                "events": events_str
            }])
            insert_athletes(new_athlete)
            st.success(f"{first_name} {last_name} geregistreer vir {events_str}!")
            st.rerun()
        else:
            st.warning("Vul asseblief al die verpligte velde in en kies ten minste een item.")

with tab3:
    st.subheader("Huidige Geregistreerde Atlete")
    athletes_df = fetch_athletes()
    if not athletes_df.empty:
        clean_display = athletes_df.copy()
        drop_cols = [c for c in ['id'] if c in clean_display.columns]
        clean_display.drop(columns=drop_cols, inplace=True)
        
        rename_dict = {
            "first_name": "Voornaam",
            "last_name": "Van",
            "school": "Skool",
            "gender": "Geslag",
            "age_group": "Ouderdom",
            "events": "Items"
        }
        clean_display.rename(columns=rename_dict, inplace=True)
        st.dataframe(clean_display, use_container_width=True)
        st.caption(f"Totaal Geregistreer: {len(athletes_df)} atlete")
    else:
        st.info("Nog geen atlete geregistreer nie.")

with tab4:
    st.subheader("⚙️ Stoor / Reset Byeenkoms Data")
    
    st.markdown("### 💾 Rugsteun & Export")
    st.write("Laai 'n volledige Excel-lêer af met al die huidige geregistreerde atlete, uitslae en rekords.")
    
    def generate_full_backup_excel():
        buffer = io.BytesIO()
        df_ath = fetch_athletes()
        df_res = fetch_all_results()
        df_rec = fetch_all_records()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_ath.to_excel(writer, index=False, sheet_name="Atlete")
            df_res.to_excel(writer, index=False, sheet_name="Uitslae")
            df_rec.to_excel(writer, index=False, sheet_name="Rekords")
        buffer.seek(0)
        return buffer

    st.download_button(
        label="💾 Laai Volledige Byeenkoms Rugsteun (Excel)",
        data=generate_full_backup_excel(),
        file_name="Swartland_Atletiek_Byeenkoms_Rugsteun.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.divider()
    
    st.markdown("### ⚠️ Vee Alles Skoon (Reset)")
    st.warning("Hierdie aksie sal **alle** geregistreerde atlete, uitslae en rekords van die stelsel skrap! Maak seker jy het 'n rugsteun voor jy voortgaan.")
    
    confirm_reset = st.checkbox("Ek verstaan hierdie aksie kan nie ongedaan gemaak word nie.")
    
    if st.button("🗑️ Vee Alle Data Skoon", type="primary", disabled=not confirm_reset):
        reset_database()
        st.success("Die stelsel is suksesvol skoongemaak!")
        st.rerun()