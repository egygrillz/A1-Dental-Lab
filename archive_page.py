# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
from fpdf import FPDF
from datetime import datetime
from arabic_reshaper import reshape
from bidi.algorithm import get_display


def show_archive_page(db):
    st.header("📂 أرشيف الحالات")

    df = db.run_query("SELECT * FROM cases ORDER BY id DESC")
    
    if df.empty:
        st.info("لا توجد حالات مسجلة حالياً.")
        return

    col1, col2 = st.columns(2)
    search_patient = col1.text_input("🔍 بحث باسم المريض")
    search_doctor = col2.text_input("👨‍⚕️ بحث باسم الدكتور أو المركز")

    if search_patient:
        df = df[df['patient'].str.contains(search_patient, case=False, na=False)]
    if search_doctor:
        df = df[
            df['doctor'].str.contains(search_doctor, case=False, na=False) | 
            df['dental_center'].fillna('').str.contains(search_doctor, case=False, na=False)
        ]

    st.divider()

    for index, row in df.iterrows():
        entity_display = row['dental_center'] if row['dental_center'] else row['doctor']
        branch_info = f" - {row['branch_name']}" if row.get('branch_name') else ""
        
        with st.expander(f"📦 كود: {row['case_code']} | المريض: {row['patient']} | {entity_display}{branch_info}"):
            col_info, col_files = st.columns([2, 1])

            with col_info:
                st.write("**📋 معلومات الحالة:**")
                st.write(f"- **الكود:** {row['case_code']}")
                st.write(f"- **المريض:** {row['patient']}")
                
                if row['dental_center']:
                    st.write(f"- **المركز:** {row['dental_center']}")
                    if row.get('branch_name'):
                        st.write(f"- **الفرع:** {row['branch_name']}")
                else:
                    st.write(f"- **الدكتور:** {row['doctor']}")
                
                st.write(f"- **تاريخ الدخول:** {row['entry_date']}")
                st.write(f"- **الحالة:** {row['status']}")
                
                if row['is_try_in'] == 1:
                    st.write(f"- **Try-in:** نعم")
                    st.write(f"- **موعد Try-in:** {row['try_in_date'] or 'غير محدد'}")
                
                st.write(f"- **موعد التسليم المتوقع:** {row['expected_delivery']}")
                
                if row['delivery_date']:
                    st.write(f"- **تاريخ التسليم الفعلي:** {row['delivery_date']}")
                
                st.write(f"- **اللون:** {row['color'] or 'غير محدد'}")
                st.write(f"- **عدد الأسنان:** {row['count'] or 0}")
                st.write(f"- **حالة الدفع:** {'✅ مدفوع' if row['is_paid'] == 1 else '⏳ غير مدفوع'}")
                
                st.write("---")
                st.write("**🦷 تفاصيل الأسنان والأسعار:**")
                teeth_data = json.loads(row['teeth_map'])
                
                material_groups = {}
                for tooth, info in teeth_data.items():
                    material = info.get('material', 'غير محدد')
                    if material not in material_groups:
                        material_groups[material] = []
                    material_groups[material].append(tooth)
                
                total_teeth_price = 0
                for material, teeth_list in material_groups.items():
                    price = teeth_data[teeth_list[0]].get('price', 0)
                    total_price = price * len(teeth_list)
                    total_teeth_price += total_price
                    
                    teeth_display = ", ".join(sorted(teeth_list, key=int))
                    st.write(f"- {material}: أسنان {teeth_display} ({len(teeth_list)} × {price} = {total_price} ج.م)")

                st.success(f"💰 الإجمالي النهائي: {row['price']:,} ج.م")
                
                if row['notes']:
                    st.write("---")
                    st.write("**📝 ملاحظات:**")
                    st.info(row['notes'])

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
                
                if row['attachment'] and os.path.exists(row['attachment']):
                    st.write("**📎 ملف مرفق:**")
                    st.write(os.path.basename(row['attachment']))

            st.divider()

            b1, b2 = st.columns(2)

            if b1.button(
                f"📑 تقرير مفصل (PDF)",
                key=f"pdf_{row['case_code']}",
                use_container_width=True,
                type="primary"
            ):
                generate_detailed_pdf(row, db)

            if b2.button(
                f"🗑️ حذف",
                key=f"del_{row['case_code']}",
                use_container_width=True
            ):
                db.run_action("DELETE FROM cases WHERE case_code = ?", (row['case_code'],))
                st.rerun()


def generate_detailed_pdf(row, db):
    """Generate comprehensive PDF report with all case details"""
    
    pdf = FPDF()
    pdf.add_page()

    # Try to add Arabic font - FIXED
    possible_paths = [
        "fonts",
        "dejavu-fonts-ttf-2.37/ttf",
        "A1-Dental-Lab/fonts"
    ]
    
    font_loaded = False
    for folder in possible_paths:
        sans_path = os.path.join(folder, "DejaVuSans.ttf")
        bold_path = os.path.join(folder, "DejaVuSans-Bold.ttf")
        
        if os.path.exists(sans_path) and os.path.exists(bold_path):
            pdf.add_font("DejaVu", "", sans_path, uni=True)
            pdf.add_font("DejaVu", "B", bold_path, uni=True)
            font_loaded = True
            break
    
    # HEADER
    if font_loaded:
        pdf.set_font("DejaVu", 'B', 16)
    else:
        pdf.set_font("Arial", 'B', 16)
        
    pdf.cell(0, 10, "DETAILED CASE REPORT", ln=True, align='C')
    
    if font_loaded:
        pdf.set_font("DejaVu", 'B', 14)
    else:
        pdf.set_font("Arial", 'B', 14)
        
    pdf.cell(0, 10, "A1 DENTAL LAB", ln=True, align='C')
    pdf.ln(5)

    # CASE CODE
    if font_loaded:
        pdf.set_font("DejaVu", 'B', 12)
    else:
        pdf.set_font("Arial", 'B', 12)
        
    pdf.cell(0, 10, f"Case Code: {row['case_code']}", ln=True, align='C', border=1)
    pdf.ln(8)

    # BASIC INFORMATION
    if font_loaded:
        pdf.set_font("DejaVu", 'B', 11)
        pdf.cell(0, 8, get_display(reshape("المعلومات الأساسية - Basic Information")), ln=True)
    else:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "Basic Information", ln=True)
    pdf.ln(2)

    if font_loaded:
        pdf.set_font("DejaVu", '', 10)
    else:
        pdf.set_font("Arial", '', 10)
    
    # Patient
    pdf.cell(60, 7, "Patient Name:", 0, 0, 'L')
    if font_loaded:
        pdf.cell(0, 7, get_display(reshape(str(row['patient']))), 0, 1, 'L')
    else:
        pdf.cell(0, 7, str(row['patient']), 0, 1, 'L')
    
    # Doctor or Center
    if row['dental_center']:
        pdf.cell(60, 7, "Dental Center:", 0, 0, 'L')
        if font_loaded:
            pdf.cell(0, 7, get_display(reshape(str(row['dental_center']))), 0, 1, 'L')
        else:
            pdf.cell(0, 7, str(row['dental_center']), 0, 1, 'L')
        
        if row.get('branch_name'):
            pdf.cell(60, 7, "Branch:", 0, 0, 'L')
            if font_loaded:
                pdf.cell(0, 7, get_display(reshape(str(row['branch_name']))), 0, 1, 'L')
            else:
                pdf.cell(0, 7, str(row['branch_name']), 0, 1, 'L')
    else:
        pdf.cell(60, 7, "Doctor:", 0, 0, 'L')
        if font_loaded:
            pdf.cell(0, 7, get_display(reshape(str(row['doctor']))), 0, 1, 'L')
        else:
            pdf.cell(0, 7, str(row['doctor']), 0, 1, 'L')
    
    # Status
    pdf.cell(60, 7, "Status:", 0, 0, 'L')
    if font_loaded:
        pdf.cell(0, 7, get_display(reshape(str(row['status']))), 0, 1, 'L')
    else:
        pdf.cell(0, 7, str(row['status']), 0, 1, 'L')
    
    # Payment status
    pdf.cell(60, 7, "Payment Status:", 0, 0, 'L')
    payment_text = "Paid" if row['is_paid'] == 1 else "Unpaid"
    pdf.cell(0, 7, payment_text, 0, 1, 'L')
    
    pdf.ln(5)

    # DATES
    if font_loaded:
        pdf.set_font("DejaVu", 'B', 11)
        pdf.cell(0, 8, get_display(reshape("التواريخ - Dates")), ln=True)
    else:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "Dates", ln=True)
    pdf.ln(2)

    if font_loaded:
        pdf.set_font("DejaVu", '', 10)
    else:
        pdf.set_font("Arial", '', 10)
    
    entry_date = row.get('entry_date') or 'N/A'
    expected_delivery = row.get('expected_delivery') or 'N/A'
    delivery_date = row.get('delivery_date') or 'N/A'
    
    pdf.cell(63, 8, f"Entry Date: {entry_date}", 1, 0, 'C')
    pdf.cell(63, 8, f"Expected: {expected_delivery}", 1, 0, 'C')
    pdf.cell(63, 8, f"Delivered: {delivery_date}", 1, 1, 'C')
    
    # Try-in info
    if row['is_try_in'] == 1:
        pdf.ln(2)
        try_in_date = row.get('try_in_date') or 'Not specified'
        pdf.cell(0, 7, f"Try-in Date: {try_in_date}", 0, 1, 'L')
    
    pdf.ln(5)

    # TEETH DETAILS
    if font_loaded:
        pdf.set_font("DejaVu", 'B', 11)
        pdf.cell(0, 8, get_display(reshape("تفاصيل الأسنان - Teeth Details")), ln=True)
    else:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "Teeth Details", ln=True)
    pdf.ln(2)

    teeth_data = json.loads(row['teeth_map'])
    
    # Group by material
    material_groups = {}
    for tooth, info in teeth_data.items():
        material = info.get('material', 'Unspecified')
        if material not in material_groups:
            material_groups[material] = {'teeth': [], 'price': info.get('price', 0)}
        material_groups[material]['teeth'].append(tooth)
    
    if font_loaded:
        pdf.set_font("DejaVu", '', 10)
    else:
        pdf.set_font("Arial", '', 10)
    
    total_price = 0
    for material, data in material_groups.items():
        teeth_list = ", ".join(sorted(data['teeth'], key=int))
        unit_price = data['price']
        count = len(data['teeth'])
        subtotal = unit_price * count
        total_price += subtotal
        
        if font_loaded:
            material_display = get_display(reshape(material))
        else:
            material_display = material
        
        pdf.cell(70, 7, f"Material: {material_display}", 0, 0, 'L')
        pdf.cell(60, 7, f"Teeth: {teeth_list}", 0, 0, 'L')
        pdf.cell(30, 7, f"Count: {count}", 0, 0, 'L')
        pdf.cell(30, 7, f"Total: {subtotal} EGP", 0, 1, 'R')
    
    # Shade
    pdf.ln(3)
    pdf.cell(60, 7, f"Shade/Color: {row['color'] or 'Not specified'}", 0, 1, 'L')
    pdf.cell(60, 7, f"Total Teeth Count: {row['count'] or 0}", 0, 1, 'L')
    
    pdf.ln(5)

    # PRICING
    if font_loaded:
        pdf.set_font("DejaVu", 'B', 12)
        pdf.cell(0, 10, get_display(reshape("الأسعار - Pricing")), ln=True)
    else:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Pricing", ln=True)
    
    if font_loaded:
        pdf.set_font("DejaVu", 'B', 11)
    else:
        pdf.set_font("Arial", 'B', 11)
        
    pdf.cell(130, 10, "Total Case Price:", 0, 0, 'R')
    pdf.cell(60, 10, f"{row['price']:,.2f} EGP", 1, 1, 'C')
    
    pdf.ln(5)

    # NOTES
    if row['notes']:
        if font_loaded:
            pdf.set_font("DejaVu", 'B', 11)
            pdf.cell(0, 8, get_display(reshape("ملاحظات - Notes")), ln=True)
        else:
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, "Notes", ln=True)
        pdf.ln(2)
        
        if font_loaded:
            pdf.set_font("DejaVu", '', 10)
            notes_text = get_display(reshape(row['notes']))
        else:
            pdf.set_font("Arial", '', 10)
            notes_text = row['notes']
        
        pdf.multi_cell(0, 7, notes_text, border=1)
        pdf.ln(5)

    # IMAGE
    if row['attachment'] and os.path.exists(row['attachment']):
        if font_loaded:
            pdf.set_font("DejaVu", 'B', 11)
        else:
            pdf.set_font("Arial", 'B', 11)
            
        pdf.cell(0, 8, "Attached Image:", ln=True)
        pdf.ln(2)
        
        try:
            if row['attachment'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                pdf.set_draw_color(0, 0, 0)
                pdf.rect(10, pdf.get_y(), 82, 62)
                pdf.image(row['attachment'], x=11, y=pdf.get_y()+1, w=80, h=60)
                pdf.ln(65)
            else:
                pdf.cell(0, 7, f"File attached: {os.path.basename(row['attachment'])}", 0, 1, 'L')
        except:
            pdf.cell(0, 7, f"File attached: {os.path.basename(row['attachment'])}", 0, 1, 'L')

    # FOOTER - FIXED: Don't use italic if font not loaded
    pdf.ln(10)
    if font_loaded:
        pdf.set_font("DejaVu", '', 8)  # Regular font, not italic
    else:
        pdf.set_font("Arial", '', 8)
        
    pdf.cell(0, 5, f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    pdf.cell(0, 5, "A1 Dental Lab Management System", 0, 1, 'C')

    # Output
    report_name = f"Detailed_Report_{row['case_code']}.pdf"
    
    try:
        # FIXED PDF OUTPUT
        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')
        elif isinstance(pdf_output, bytearray):
            pdf_output = bytes(pdf_output)
        
        st.download_button(
            "📥 تحميل التقرير المفصل",
            pdf_output,
            file_name=report_name,
            mime="application/pdf",
            key=f"dl_detailed_{row['case_code']}"
        )
        st.success("✅ تم إنشاء التقرير المفصل بنجاح!")
    except Exception as e:
        st.error(f"❌ خطأ في إنشاء التقرير: {str(e)}")
