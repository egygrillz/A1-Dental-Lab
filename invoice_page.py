# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# =============================================================================
#                           INVOICE PDF CLASS
# =============================================================================
class InvoicePDF(FPDF):
    def __init__(self):
        super().__init__()
        # FIXED: Use correct font directory path
        font_dir = "dejavu-fonts-ttf-2.37/ttf"  # Updated path
        sans_path = os.path.join(font_dir, "DejaVuSans.ttf")
        bold_path = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
        
        if os.path.exists(sans_path):
            self.add_font("DejaVu", "", sans_path, uni=True)
            self.add_font("DejaVu", "B", bold_path, uni=True)
        else:
            # Fallback: try fonts directory
            font_dir = "fonts"
            sans_path = os.path.join(font_dir, "DejaVuSans.ttf")
            bold_path = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
            if os.path.exists(sans_path):
                self.add_font("DejaVu", "", sans_path, uni=True)
                self.add_font("DejaVu", "B", bold_path, uni=True)
        
        self.set_right_margin(10)
        self.set_left_margin(10)

    def header(self):
        self.set_font("DejaVu", "B", 22)
        self.set_text_color(0, 0, 0)
        self.cell(0, 15, 'INVOICE', ln=True, align='R')
        
        self.set_font("DejaVu", "B", 18)
        self.cell(0, 8, "A1 DENTAL LAB", ln=True, align='L')
        
        self.set_font("DejaVu", "", 10)
        self.set_text_color(80, 80, 80)
        date_str = datetime.now().strftime('%d/%m/%Y')
        self.cell(0, 5, get_display(reshape(f"تاريخ الإصدار: {date_str}")), ln=True, align='L')
        self.ln(8)

    def draw_info_grid(self, doctor_name):
        self.set_fill_color(245, 245, 245)
        self.set_font("DejaVu", "B", 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, get_display(reshape(f"  بيانات الطبيب: د/ {doctor_name}")), fill=True, ln=1, align='R')
        self.ln(5)

    def draw_table(self, df):
        self.set_font("DejaVu", "B", 9)
        self.set_fill_color(40, 40, 40)
        self.set_text_color(255, 255, 255)
        
        cols = [25, 25, 20, 15, 45, 40, 20]
        headers = ["السعر", "التاريخ", "اللون", "العدد", "الخامة/Material", "المريض", "كود"]
        
        for i, h in enumerate(headers):
            self.cell(cols[i], 12, get_display(reshape(h)), border=1, align='C', fill=True)
        self.ln()

        self.set_text_color(0, 0, 0)
        fill = False
        
        for _, row in df.iterrows():
            self.set_fill_color(252, 252, 252)
            try:
                t_map = json.loads(row['teeth_map'])
                mat_counts = {}
                for t_info in t_map.values():
                    m = t_info['material']
                    mat_counts[m] = mat_counts.get(m, 0) + 1
                
                mat_list = list(mat_counts.keys())
                num_materials = len(mat_list)

                for i, mat_name in enumerate(mat_list):
                    is_first = (i == 0)
                    is_last = (i == num_materials - 1)
                    
                    if num_materials == 1:
                        border_style = 1
                    else:
                        border_style = 'LR'
                        if is_first: border_style += 'T'
                        if is_last: border_style += 'B'

                    price_val   = f"{row['price']:,.2f}" if is_first else ""
                    date_val    = str(row['entry_date']) if is_first else ""
                    shade_val   = str(row['color']) if is_first else ""
                    patient_val = get_display(reshape(str(row['patient']))) if is_first else ""
                    code_val    = str(row['case_code']) if is_first else ""

                    self.set_font("DejaVu", "", 9)
                    self.cell(cols[0], 10, price_val,   border=border_style, align='C', fill=fill)
                    self.cell(cols[1], 10, date_val,    border=border_style, align='C', fill=fill)
                    self.cell(cols[2], 10, shade_val,   border=border_style, align='C', fill=fill)
                    
                    self.cell(cols[3], 10, str(mat_counts[mat_name]), border=1, align='C', fill=fill)
                    self.cell(cols[4], 10, get_display(reshape(mat_name)), border=1, align='C', fill=fill)
                    
                    self.set_font("DejaVu", "", 9)
                    self.cell(cols[5], 10, patient_val, border=border_style, align='C', fill=fill)
                    
                    self.set_font("DejaVu", "", 6)
                    self.cell(cols[6], 10, code_val,    border=border_style, align='C', fill=fill)
                    self.ln()
            except Exception as e:
                # Fallback for cases without proper teeth_map
                self.set_font("DejaVu", "", 9)
                self.cell(cols[0], 10, f"{row['price']:,.2f}", border=1, align='C', fill=fill)
                self.cell(cols[1], 10, str(row['entry_date']), border=1, align='C', fill=fill)
                self.cell(cols[2], 10, str(row['color']), border=1, align='C', fill=fill)
                self.cell(cols[3], 10, "1", border=1, align='C', fill=fill)
                self.cell(cols[4], 10, "N/A", border=1, align='C', fill=fill)
                self.cell(cols[5], 10, get_display(reshape(str(row['patient']))), border=1, align='C', fill=fill)
                self.set_font("DejaVu", "", 6)
                self.cell(cols[6], 10, str(row['case_code']), border=1, align='C', fill=fill)
                self.ln()
            
            fill = not fill

    def draw_total(self, total_amount):
        self.ln(5)
        self.set_font("DejaVu", "B", 14)
        self.set_text_color(0, 0, 0)
        self.cell(140, 12, get_display(reshape("الإجمالي النهائي (ج.م)  ")), align='R')
        self.cell(50, 12, f"{total_amount:,.2f}", border=1, align='C')


# =============================================================================
#                           MAIN PAGE FUNCTION
# =============================================================================
def show_invoice_page(db):
    st.header("🧾 فواتير A1 DENTAL LAB")

    doctors_df = db.run_query("SELECT name FROM doctors_list ORDER BY name")
    if doctors_df.empty:
        st.warning("يرجى إضافة أطباء من الإعدادات أولاً.")
        return

    selected_doctor = st.selectbox(
        "اختر الطبيب",
        options=doctors_df["name"].tolist(),
        key="inv_dr_select"
    )

    unpaid_cases = db.run_query(
        """
        SELECT * FROM cases 
        WHERE doctor = ? AND is_paid = 0 
        ORDER BY entry_date DESC
        """,
        (selected_doctor,)
    )

    if unpaid_cases.empty:
        st.success(f"لا توجد مديونيات على د/ {selected_doctor}")
        return

    selected_rows = []
    for idx, row in unpaid_cases.iterrows():
        col_c, col_i = st.columns([1, 9])
        if col_c.checkbox("", key=f"inv_check_{row['id']}"):
            selected_rows.append(idx)
        col_i.write(
            f"**{row['patient']}** | كود: `{row['case_code']}` | "
            f"سعر: {row['price']:,} ج.م | تاريخ: {row['entry_date']}"
        )

    if selected_rows:
        selected_df = unpaid_cases.loc[selected_rows].copy()
        total_sum = selected_df["price"].sum()
        
        st.markdown("---")
        st.subheader(f"الإجمالي: {total_sum:,} ج.م")

        if st.button("📄 إصدار فاتورة PDF"):
            try:
                pdf = InvoicePDF()
                pdf.add_page()
                pdf.draw_info_grid(selected_doctor)
                pdf.draw_table(selected_df)
                pdf.draw_total(total_sum)
                
                # ✅ FIXED: Removed double bytes() wrapping
                pdf_bytes = bytes(pdf.output(dest='S'))

                st.download_button(
                    label="📥 تحميل الملف",
                    data=pdf_bytes,
                    file_name=f"A1_Invoice_{selected_doctor.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ تم إنشاء الفاتورة بنجاح!")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء إنشاء الفاتورة: {str(e)}")
                st.info("تأكد من وجود ملفات الخطوط في المسار الصحيح")

        if st.button("✅ تأكيد التحصيل (مدفوع)", type="primary"):
            try:
                for case_id in selected_df["id"].tolist():
                    db.run_action("UPDATE cases SET is_paid = 1 WHERE id = ?", (case_id,))
                st.success("تم تسجيل المبلغ المستلم بنجاح.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء تحديث الحالة: {str(e)}")


if __name__ == "__main__":
    print("invoice_page.py loaded successfully")
    print("show_invoice_page function is defined →", "show_invoice_page" in globals())
