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
#                 INVOICE PDF CLASS
# =============================================================================
class InvoicePDF(FPDF):
    def __init__(self):
        super().__init__()
        possible_paths = [
            "fonts",
            "dejavu-fonts-ttf-2.37/ttf",
            "A1-Dental-Lab/fonts"
        ]
        
        found = False
        for folder in possible_paths:
            sans_path = os.path.join(folder, "DejaVuSans.ttf")
            bold_path = os.path.join(folder, "DejaVuSans-Bold.ttf")
            
            if os.path.exists(sans_path) and os.path.exists(bold_path):
                self.add_font("DejaVu", "", sans_path, uni=True)
                self.add_font("DejaVu", "B", bold_path, uni=True)
                found = True
                break
        
        if not found:
            print("CRITICAL: Font files not found in any expected directory")
            
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

    def draw_info_grid(self, entity_name, branch_name=None):
        self.set_fill_color(245, 245, 245)
        self.set_font("DejaVu", "B", 11)
        self.set_text_color(0, 0, 0)
        
        if branch_name:
            self.cell(0, 10, get_display(reshape(f"  بيانات: {entity_name} - {branch_name}")), fill=True, ln=1, align='R')
        else:
            self.cell(0, 10, get_display(reshape(f"  بيانات: {entity_name}")), fill=True, ln=1, align='R')
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

    def draw_total(self, total_amount, raseed_sabek=0, sabek_date="", raseed_mostahak=0):
        self.ln(5)
        self.set_font("DejaVu", "", 11)
        
        # Row 1: Previous Balance
        text_sabek = f"الرصيد السابق بتاريخ {sabek_date}"
        self.cell(140, 10, get_display(reshape(text_sabek)), align='R')
        self.cell(50, 10, f"{raseed_sabek:,.2f}", border=1, align='C')
        self.ln()

        # Row 2: Due Balance
        self.cell(140, 10, get_display(reshape("الرصيد المستحق")), align='R')
        self.cell(50, 10, f"{raseed_mostahak:,.2f}", border=1, align='C')
        self.ln()

        # Row 3: Current Invoice Subtotal
        self.cell(140, 10, get_display(reshape("إجمالي الفاتورة الحالية")), align='R')
        self.cell(50, 10, f"{total_amount:,.2f}", border=1, align='C')
        self.ln(12)

        # Row 4: Grand Total (Egmaly el Mosta7akat)
        grand_total = total_amount + raseed_sabek + raseed_mostahak
        self.set_font("DejaVu", "B", 14)
        self.set_fill_color(240, 240, 240)
        self.cell(140, 12, get_display(reshape("إجمالي المستحقات النهائي (ج.م)")), align='R', fill=True)
        self.cell(50, 12, f"{grand_total:,.2f}", border=1, align='C', fill=True)


def show_invoice_page(db):
    st.header("🧾 فواتير A1 DENTAL LAB")

    if 'selected_case_ids' not in st.session_state:
        st.session_state.selected_case_ids = set()

    all_entities_df = db.run_query("""
        SELECT name, is_center, center_parent 
        FROM doctors_list 
        WHERE center_parent IS NULL
        ORDER BY is_center DESC, name
    """)
    
    if all_entities_df.empty:
        st.warning("يرجى إضافة أطباء أو مراكز من الإعدادات أولاً.")
        return

    col_type, col_entity, col_branch = st.columns([1, 2, 2])
    
    entity_type = col_type.radio("اختر نوع الجهة:", ["دكتور", "مركز أسنان"], horizontal=True)
    
    selected_entity = None
    selected_branch = None
    is_center = False
    query_all_branches = False
    
    if entity_type == "دكتور":
        doctors = all_entities_df[all_entities_df['is_center'] == 0]['name'].tolist()
        if doctors:
            selected_entity = col_entity.selectbox("👨‍⚕️ اختر الدكتور", doctors)
        else:
            st.warning("لا يوجد أطباء مسجلين")
            return
    else:
        centers = all_entities_df[all_entities_df['is_center'] == 1]['name'].tolist()
        if centers:
            selected_entity = col_entity.selectbox("🏥 اختر المركز", centers)
            is_center = True
            
            branches_df = db.run_query(
                "SELECT name FROM doctors_list WHERE center_parent = ?", 
                (selected_entity,)
            )
            
            if not branches_df.empty:
                branch_options = ["-- جميع الفروع --", "-- المركز الرئيسي --"] + branches_df['name'].tolist()
                selected_branch_display = col_branch.selectbox("📍 اختر الفرع", branch_options)
                
                if selected_branch_display == "-- جميع الفروع --":
                    query_all_branches = True
                    selected_branch = None
                elif selected_branch_display == "-- المركز الرئيسي --":
                    selected_branch = None
                    query_all_branches = False
                else:
                    selected_branch = selected_branch_display
                    query_all_branches = False
            else:
                col_branch.info("لا توجد فروع لهذا المركز")
        else:
            st.warning("لا توجد مراكز مسجلة")
            return

    st.divider()
    st.subheader("💰 إدارة الأرصدة")
    
    balance_info = db.get_or_create_balance(
        selected_entity, 
        'center' if is_center else 'doctor',
        selected_branch if selected_branch else None
    )
    
    with st.expander("📊 عرض وتعديل الأرصدة", expanded=True):
        col_prev, col_out = st.columns(2)
        
        prev_balance = col_prev.number_input(
            "الرصيد السابق (ج.م)",
            value=float(balance_info.get('previous_balance', 0) if balance_info else 0),
            step=100.0,
            key="prev_balance_input"
        )
        
        prev_balance_date = col_prev.date_input(
            "تاريخ الرصيد السابق",
            value=datetime.strptime(balance_info['previous_balance_date'], '%Y-%m-%d').date() 
                  if balance_info and balance_info.get('previous_balance_date') else datetime.now().date(),
            key="prev_balance_date_input"
        )
        
        outstanding_balance = col_out.number_input(
            "الرصيد المستحق (ج.م)",
            value=float(balance_info.get('outstanding_balance', 0) if balance_info else 0),
            step=100.0,
            help="هذا الرصيد يتم تحديثه تلقائياً عند إصدار الفواتير، لكن يمكنك تعديله يدوياً",
            key="out_balance_input"
        )
        
        balance_notes = st.text_area(
            "ملاحظات على الأرصدة",
            value=balance_info.get('notes', '') if balance_info else '',
            key="balance_notes_input"
        )
        
        if st.button("💾 حفظ تعديلات الأرصدة", type="primary"):
            db.update_balance(
                selected_entity,
                selected_branch if selected_branch else None,
                prev_balance,
                str(prev_balance_date),
                outstanding_balance,
                balance_notes
            )
            st.success("✅ تم حفظ الأرصدة بنجاح")
            st.rerun()
        
        total_due = prev_balance + outstanding_balance
        st.metric("إجمالي المستحق", f"{total_due:,.2f} ج.م")

    st.divider()
    st.subheader("📋 الحالات الغير مدفوعة")
    
    if is_center:
        if query_all_branches:
            query = "SELECT * FROM cases WHERE dental_center = ? AND is_paid = 0 ORDER BY entry_date DESC"
            params = (selected_entity,)
        elif selected_branch:
            query = "SELECT * FROM cases WHERE dental_center = ? AND branch_name = ? AND is_paid = 0 ORDER BY entry_date DESC"
            params = (selected_entity, selected_branch)
        else:
            query = "SELECT * FROM cases WHERE dental_center = ? AND (branch_name IS NULL OR branch_name = '') AND is_paid = 0 ORDER BY entry_date DESC"
            params = (selected_entity,)
    else:
        query = "SELECT * FROM cases WHERE doctor = ? AND (dental_center IS NULL OR dental_center = '') AND is_paid = 0 ORDER BY entry_date DESC"
        params = (selected_entity,)
    
    unpaid_cases = db.run_query(query, params)

    if unpaid_cases.empty:
        st.success(f"لا توجد مديونيات على {selected_entity}")
        return

    select_all_key = f"select_all_{selected_entity}_{selected_branch}"
    if select_all_key not in st.session_state:
        st.session_state[select_all_key] = False
    
    def toggle_select_all():
        if st.session_state[select_all_key]:
            st.session_state.selected_case_ids = set(unpaid_cases['id'].tolist())
        else:
            st.session_state.selected_case_ids = set()
    
    st.checkbox("✅ تحديد الكل", key=select_all_key, on_change=toggle_select_all)
    
    for idx, row in unpaid_cases.iterrows():
        col_c, col_i = st.columns([1, 9])
        is_selected = row['id'] in st.session_state.selected_case_ids
        checkbox_key = f"inv_check_{row['id']}"
        if col_c.checkbox("", value=is_selected, key=checkbox_key):
            st.session_state.selected_case_ids.add(row['id'])
        else:
            st.session_state.selected_case_ids.discard(row['id'])
        
        branch_info = f" | فرع: {row['branch_name']}" if row.get('branch_name') else ""
        col_i.write(f"**{row['patient']}** | كود: `{row['case_code']}` | سعر: {row['price']:,} ج.م | تاريخ: {row['entry_date']}{branch_info}")

    selected_df = unpaid_cases[unpaid_cases['id'].isin(st.session_state.selected_case_ids)].copy()
    
    if not selected_df.empty:
        total_sum = selected_df["price"].sum()
        st.markdown("---")
        st.subheader(f"الإجمالي: {total_sum:,} ج.م")
        
        new_outstanding = balance_info.get('outstanding_balance', 0) + total_sum if balance_info else total_sum
        st.info(f"📊 الرصيد المستحق بعد هذه الفاتورة: {new_outstanding:,.2f} ج.م")

        col_pdf, col_confirm = st.columns(2)
        
        if col_pdf.button("📄 إصدار فاتورة PDF", use_container_width=True):
            try:
                pdf = InvoicePDF()
                pdf.add_page()
                pdf.draw_info_grid(selected_entity, selected_branch)
                pdf.draw_table(selected_df)
                
                # ADDED BALANCE PARAMETERS TO PDF CALL
                pdf.draw_total(
                    total_amount=total_sum,
                    raseed_sabek=prev_balance,
                    sabek_date=str(prev_balance_date),
                    raseed_mostahak=outstanding_balance
                )
                
                pdf_output = pdf.output(dest='S')
                if isinstance(pdf_output, str):
                    pdf_output = pdf_output.encode('latin-1')
                elif isinstance(pdf_output, bytearray):
                    pdf_output = bytes(pdf_output)

                entity_display = f"{selected_entity}_{selected_branch}" if selected_branch else selected_entity
                st.download_button(
                    label="📥 تحميل الملف",
                    data=pdf_output,
                    file_name=f"A1_Invoice_{entity_display.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key=f"download_inv_{datetime.now().strftime('%H%M%S')}"
                )
                st.success("✅ تم إنشاء الفاتورة بنجاح!")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء إنشاء الفاتورة: {str(e)}")

        if col_confirm.button("✅ تأكيد التحصيل (مدفوع)", type="primary", use_container_width=True):
            try:
                invoice_number = db.create_invoice(
                    doctor_name=selected_entity,
                    case_ids=selected_df["id"].tolist(),
                    total_amount=total_sum,
                    dental_center=selected_entity if is_center else None,
                    branch_name=selected_branch if is_center else None,
                    created_by=None,
                    notes=f"فاتورة - {datetime.now().strftime('%Y-%m-%d')}"
                )
                if invoice_number:
                    st.success(f"✅ تم تسجيل المبلغ المستلم بنجاح - رقم الفاتورة: {invoice_number}")
                    st.session_state.selected_case_ids = set()
                    st.rerun()
                else:
                    st.error("حدث خطأ أثناء إنشاء الفاتورة")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء تحديث الحالة: {str(e)}")