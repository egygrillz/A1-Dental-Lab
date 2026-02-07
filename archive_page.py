# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
from fpdf import FPDF
from datetime import datetime


def show_archive_page(db):
    st.header("📂 أرشيف الحالات")

    # جلب البيانات
    df = db.run_query("SELECT * FROM cases ORDER BY id DESC")
    
    if df.empty:
        st.info("لا توجد حالات مسجلة حالياً.")
        return

    # --- Search bar ---
    col1, col2 = st.columns(2)
    search_patient = col1.text_input("🔍 بحث باسم المريض")
    search_doctor = col2.text_input("👨‍⚕️ بحث باسم الدكتور")

    if search_patient:
        df = df[df['patient'].str.contains(search_patient, case=False, na=False)]
    if search_doctor:
        df = df[df['doctor'].str.contains(search_doctor, case=False, na=False)]

    st.divider()

    for index, row in df.iterrows():
        with st.expander(f"📦 كود: {row['case_code']} | المريض: {row['patient']} | دكتور: {row['doctor']}"):
            col_info, col_files = st.columns([2, 1])

            with col_info:
                st.write("**🦷 تفاصيل الأسنان والأسعار:**")
                teeth_data = json.loads(row['teeth_map'])
                total_teeth_price = 0
                for tooth, info in teeth_data.items():
                    price = info.get('price', 0)
                    total_teeth_price += price
                    st.write(f"- سنة {tooth}: {info['material']} ({price} ج.م)")

                # PMMA price for Try-in cases
                pmma_price = 0
                if "try-in" in row['notes'].lower() or "تجربة" in row['notes']:
                    pmma_price = 150
                    st.warning(f"➕ إضافة سعر PMMA (Try-in): {pmma_price} ج.م")

                final_total = row['price'] + pmma_price
                st.success(f"💰 الإجمالي النهائي: {final_total} ج.م")

            with col_files:
                st.write("**📤 تحديث الملفات:**")
                new_file = st.file_uploader(
                    f"رفع ملف جديد {row['case_code']}",
                    key=f"file_{row['case_code']}"
                )
                if new_file and st.button("حفظ الملف", key=f"btn_{row['case_code']}"):
                    path = os.path.abspath(os.path.join("uploads", f"{row['case_code']}_{new_file.name}"))
                    with open(path, "wb") as f:
                        f.write(new_file.getbuffer())
                    db.run_action(
                        "UPDATE cases SET attachment = ? WHERE case_code = ?",
                        (path, row['case_code'])
                    )
                    st.rerun()

            st.divider()

            # Buttons: Report + Delete
            b1, b2 = st.columns(2)

            if b1.button(
                f"📑 تقرير مفصل (عربي)",
                key=f"pdf_{row['case_code']}",
                use_container_width=True,
                type="primary"
            ):
                generate_arabic_pdf(row, pmma_price)

            if b2.button(
                f"🗑️ حذف",
                key=f"del_{row['case_code']}",
                use_container_width=True
            ):
                db.run_action("DELETE FROM cases WHERE case_code = ?", (row['case_code'],))
                st.rerun()


def generate_arabic_pdf(row, pmma_price):
    pdf = FPDF()
    pdf.add_page()

    # Title and Code
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "CASE REPORT - TAQRIR HALA", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Code: {row['case_code']}", ln=True, align='C')
    pdf.ln(5)

    # Doctor and Patient
    pdf.cell(95, 10, f"Doctor: {row['doctor']}", 0, 0, 'L')
    pdf.cell(95, 10, f"Patient: {row['patient']}", 0, 1, 'R')
    pdf.ln(5)

    # ──────────────── FIXED DATES ────────────────
    entry_val    = row.get('entry_date') or row.get('created_at') or datetime.now().strftime("%Y-%m-%d")
    try_in_val   = row.get('try_in_date')   or 'N/A'
    delivery_val = row.get('delivery_date') or 'N/A'           # ← FIXED: using correct column

    # Make sure they are strings
    entry_val    = str(entry_val)
    try_in_val   = str(try_in_val)
    delivery_val = str(delivery_val)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(63, 10, f"Entry: {entry_val}",    1, 0, 'C')
    pdf.cell(63, 10, f"Try-in: {try_in_val}",  1, 0, 'C')
    pdf.cell(63, 10, f"Delivery: {delivery_val}", 1, 1, 'C')
    pdf.ln(8)
    # ─────────────────────────────────────────────

    # Teeth details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Teeth & Prices Details:", ln=True)

    teeth_data = json.loads(row['teeth_map'])
    for t, info in teeth_data.items():
        pdf.cell(0, 8, f"- Tooth {t}: {info['material']} | Price: {info['price']} EGP", ln=True)

    if pmma_price > 0:
        pdf.cell(0, 8, f"- PMMA (Try-in) Price: {pmma_price} EGP", ln=True)

    pdf.ln(2)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Total Final Price: {row['price'] + pmma_price} EGP", border=1, ln=True, align='C')
    pdf.ln(5)

    # Shade and Notes
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Shade/Color: {row['color']}", ln=True)

    if row['notes']:
        pdf.multi_cell(0, 10, f"Notes: {row['notes']}", border=1)

    # Image handling
    if row['attachment'] and os.path.exists(row['attachment']):
        pdf.ln(5)
        pdf.cell(0, 10, "Attached Image:", ln=True)
        pdf.set_draw_color(0, 0, 0)
        pdf.rect(10, pdf.get_y(), 82, 62)
        pdf.image(row['attachment'], x=11, y=pdf.get_y()+1, w=80, h=60)

    # Output and Download
    report_name = f"Report_{row['case_code']}.pdf"
    pdf.output(report_name)

    with open(report_name, "rb") as f:
        st.download_button(
            "تحميل التقرير PDF",
            f,
            file_name=report_name,
            key=f"dl_{row['case_code']}"
        )

    # Clean up
    os.remove(report_name)