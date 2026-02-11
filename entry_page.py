# -*- coding: utf-8 -*-
"""
Entry Page - New Case Registration
Features:
- Interactive tooth selection
- Nightguard mode
- Material pricing
- Try-in scheduling
- File attachments
- Validation
"""

import streamlit as st
import json
from datetime import datetime, timedelta
import os
from collections import defaultdict

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def show_entry_page(db):
    """Main entry page for registering new cases"""
    st.header("📥 تسجيل حالة جديدة - New Case Registration")
    
    # Initialize session state
    if 'confirmed_items' not in st.session_state:
        st.session_state.confirmed_items = []
    if 'pending_teeth' not in st.session_state:
        st.session_state.pending_teeth = {}
    if 'nightguard_mode' not in st.session_state:
        st.session_state.nightguard_mode = False
    if 'show_tooth_numbers' not in st.session_state:
        st.session_state.show_tooth_numbers = True
    
    # Get doctors and centers
    docs_df = db.run_query("""
        SELECT name, is_center, center_parent, phone, email
        FROM doctors_list 
        WHERE center_parent IS NULL AND is_active = 1
        ORDER BY is_center DESC, name
    """)
    
    if docs_df.empty:
        st.warning("⚠️ يرجى إضافة دكاترة أو مراكز أولاً من صفحة الإعدادات.")
        if st.button("➡️ الذهاب إلى الإعدادات"):
            st.switch_page("pages/settings.py")
        return
    
    # =========================================================================
    #                    ENTITY SELECTION (Doctor/Center)
    # =========================================================================
    
    with st.container(border=True):
        st.subheader("👨‍⚕️ معلومات الجهة - Entity Information")
        
        centers_df = docs_df[docs_df['is_center'] == 1]
        doctors_df = docs_df[docs_df['is_center'] == 0]
        
        col_type, col_entity, col_patient = st.columns([1, 2, 2])
        
        entity_type = col_type.radio(
            "نوع الجهة:", 
            ["دكتور", "مركز أسنان"], 
            horizontal=True,
            help="اختر دكتور فردي أو مركز أسنان"
        )
        
        selected_doctor = None
        selected_center = None
        selected_branch = None
        
        if entity_type == "دكتور":
            if not doctors_df.empty:
                # Create display list with contact info
                doctor_options = []
                for _, doc in doctors_df.iterrows():
                    display = doc['name']
                    if doc.get('phone'):
                        display += f" ({doc['phone']})"
                    doctor_options.append(display)
                
                selected_display = col_entity.selectbox(
                    "👨‍⚕️ اسم الدكتور", 
                    doctor_options,
                    help="اختر الدكتور من القائمة"
                )
                selected_doctor = selected_display.split(" (")[0]  # Extract name only
            else:
                col_entity.warning("⚠️ لا يوجد أطباء مسجلين")
                return
        else:  # Dental Center
            if not centers_df.empty:
                # Create display list with contact info
                center_options = []
                for _, center in centers_df.iterrows():
                    display = center['name']
                    if center.get('phone'):
                        display += f" ({center['phone']})"
                    center_options.append(display)
                
                selected_display = col_entity.selectbox(
                    "🏥 اسم المركز", 
                    center_options,
                    help="اختر المركز من القائمة"
                )
                selected_center = selected_display.split(" (")[0]  # Extract name only
                
                # Get branches
                branches_df = db.run_query(
                    "SELECT name FROM doctors_list WHERE center_parent = ? AND is_active = 1",
                    (selected_center,)
                )
                
                if not branches_df.empty:
                    branch_options = ["-- المركز الرئيسي --"] + branches_df['name'].tolist()
                    selected_branch = col_entity.selectbox(
                        "📍 الفرع", 
                        branch_options,
                        help="اختر الفرع أو اترك المركز الرئيسي"
                    )
                    if selected_branch == "-- المركز الرئيسي --":
                        selected_branch = None
            else:
                col_entity.warning("⚠️ لا يوجد مراكز مسجلة")
                return
        
        # Patient name
        patient_name = col_patient.text_input(
            "👤 اسم المريض *", 
            placeholder="أدخل اسم المريض الكامل",
            help="مطلوب - اسم المريض ضروري لحفظ الحالة"
        )
    
    # =========================================================================
    #                    LOAD PRICES FOR SELECTED ENTITY
    # =========================================================================
    
    price_entity = selected_center if selected_center else selected_doctor
    prices_df = db.run_query(
        "SELECT material, price, cost_price FROM doctors_prices WHERE doc_name = ? AND is_active = 1",
        (price_entity,)
    )
    
    materials_list = prices_df['material'].tolist() if not prices_df.empty else []
    
    if not materials_list:
        st.warning(f"⚠️ لا توجد أسعار مسجلة لـ {price_entity}. يرجى إضافة الأسعار من صفحة الإعدادات.")
        return
    
    # Check for nightguard availability
    has_nightguard = any("nightguard" in mat.lower() for mat in materials_list)
    
    # =========================================================================
    #                    NIGHTGUARD MODE TOGGLE
    # =========================================================================
    
    if has_nightguard:
        st.divider()
        with st.container(border=True):
            nightguard_checkbox = st.checkbox(
                "🌙 **تسجيل Nightguard** (سيتم اختيار الفك كامل)",
                value=st.session_state.nightguard_mode,
                key="ng_toggle",
                help="تفعيل هذا الخيار لإضافة واقي ليلي (Nightguard) كامل"
            )
            
            if nightguard_checkbox != st.session_state.nightguard_mode:
                st.session_state.nightguard_mode = nightguard_checkbox
                st.session_state.pending_teeth = {}
                st.rerun()
    
    # =========================================================================
    #                    NIGHTGUARD MODE - ARCH SELECTION
    # =========================================================================
    
    if st.session_state.nightguard_mode:
        st.divider()
        with st.container(border=True):
            st.subheader("🦷 اختيار الفك للـ Nightguard")
            
            nightguard_material = next((mat for mat in materials_list if "nightguard" in mat.lower()), None)
            
            if nightguard_material:
                nightguard_price = prices_df[prices_df['material'] == nightguard_material]['price'].values[0]
                
                st.info(f"💰 **سعر الـ Nightguard:** {nightguard_price:,.0f} ج.م للفك الواحد")
                
                col_upper, col_lower = st.columns(2)
                
                # Upper arch button
                if col_upper.button(
                    "🦷 الفك العلوي", 
                    use_container_width=True, 
                    type="primary",
                    help="إضافة واقي ليلي للفك العلوي"
                ):
                    upper_teeth = [18,17,16,15,14,13,12,11,21,22,23,24,25,26,27,28]
                    
                    teeth_map = {
                        str(tooth): {
                            "material": nightguard_material,
                            "price": nightguard_price,
                        }
                        for tooth in upper_teeth
                    }
                    
                    st.session_state.confirmed_items.append({
                        "teeth": upper_teeth,
                        "teeth_map": teeth_map,
                        "material": nightguard_material,
                        "price": nightguard_price,
                        "type": "nightguard",
                        "arch": "الفك العلوي"
                    })
                    
                    st.success(f"✅ تم إضافة Nightguard - الفك العلوي ({nightguard_material})")
                    st.rerun()
                
                # Lower arch button
                if col_lower.button(
                    "🦷 الفك السفلي", 
                    use_container_width=True, 
                    type="primary",
                    help="إضافة واقي ليلي للفك السفلي"
                ):
                    lower_teeth = [48,47,46,45,44,43,42,41,31,32,33,34,35,36,37,38]
                    
                    teeth_map = {
                        str(tooth): {
                            "material": nightguard_material,
                            "price": nightguard_price,
                        }
                        for tooth in lower_teeth
                    }
                    
                    st.session_state.confirmed_items.append({
                        "teeth": lower_teeth,
                        "teeth_map": teeth_map,
                        "material": nightguard_material,
                        "price": nightguard_price,
                        "type": "nightguard",
                        "arch": "الفك السفلي"
                    })
                    
                    st.success(f"✅ تم إضافة Nightguard - الفك السفلي ({nightguard_material})")
                    st.rerun()
                
                # Show added nightguards
                if st.session_state.confirmed_items:
                    st.write("**✅ الـ Nightguards المضافة:**")
                    for idx, item in enumerate(st.session_state.confirmed_items):
                        if item.get('type') == 'nightguard':
                            col_info, col_delete = st.columns([4, 1])
                            col_info.markdown(f"• **{item['arch']}** ({item['material']}) - {item['price']:,.0f} ج.م")
                            if col_delete.button("🗑️", key=f"del_ng_{idx}"):
                                st.session_state.confirmed_items.pop(idx)
                                st.rerun()
            else:
                st.error("❌ لم يتم العثور على مادة Nightguard في قائمة الأسعار!")
    
    # =========================================================================
    #                    REGULAR MODE - TOOTH MAP
    # =========================================================================
    
    else:
        st.divider()
        with st.container(border=True):
            st.subheader("🦷 خريطة الأسنان - Dental Chart")
            
            # Tooth number visibility toggle
            col_toggle, _ = st.columns([2, 3])
            show_numbers = col_toggle.checkbox(
                "إظهار أرقام الأسنان",
                value=st.session_state.show_tooth_numbers,
                key="show_tooth_nums"
            )
            st.session_state.show_tooth_numbers = show_numbers
            
            # CSS for tooth map styling
            st.markdown("""
                <style>
                .v-line { 
                    border-left: 2px solid #ddd; 
                    height: 50px; 
                    margin: auto; 
                    width: 1px; 
                }
                .h-line { 
                    border-top: 2px solid #ddd; 
                    margin: 5px 0px; 
                }
                </style>
            """, unsafe_allow_html=True)
            
            def draw_tooth(num, col):
                """Draw individual tooth button with states"""
                tooth_str = str(num)
                
                # Count how many times this tooth is used
                tooth_used_count = sum(
                    1 for item in st.session_state.confirmed_items 
                    if str(num) in [str(t) for t in item.get('teeth', [])]
                )
                
                # Determine button state and label
                if tooth_str in st.session_state.pending_teeth:
                    label = f"🦷 {num} ●" if show_numbers else "●"
                    btn_type = "primary"
                    help_text = "محدد - اضغط لإلغاء التحديد"
                elif tooth_used_count > 0:
                    label = f"🦷 {num} ({tooth_used_count})" if show_numbers else f"({tooth_used_count})"
                    btn_type = "secondary"
                    help_text = f"مستخدم في {tooth_used_count} عمل"
                else:
                    label = str(num) if show_numbers else "○"
                    btn_type = "secondary"
                    help_text = "اضغط للتحديد"
                
                if col.button(
                    label, 
                    key=f"t_{num}", 
                    use_container_width=True, 
                    type=btn_type,
                    help=help_text
                ):
                    if tooth_str in st.session_state.pending_teeth:
                        del st.session_state.pending_teeth[tooth_str]
                    else:
                        st.session_state.pending_teeth[tooth_str] = {"selected": True}
                    st.rerun()
            
            # Upper jaw
            st.caption("الفك العلوي - Upper Jaw")
            up_cols = st.columns([1,1,1,1,1,1,1,1, 0.2, 1,1,1,1,1,1,1,1])
            for i, t in enumerate([18,17,16,15,14,13,12,11]):
                draw_tooth(t, up_cols[i])
            up_cols[8].markdown('<div class="v-line"></div>', unsafe_allow_html=True)
            for i, t in enumerate([21,22,23,24,25,26,27,28]):
                draw_tooth(t, up_cols[i+9])
            
            st.markdown('<div class="h-line"></div>', unsafe_allow_html=True)
            
            # Lower jaw
            st.caption("الفك السفلي - Lower Jaw")
            lo_cols = st.columns([1,1,1,1,1,1,1,1, 0.2, 1,1,1,1,1,1,1,1])
            for i, t in enumerate([48,47,46,45,44,43,42,41]):
                draw_tooth(t, lo_cols[i])
            lo_cols[8].markdown('<div class="v-line"></div>', unsafe_allow_html=True)
            for i, t in enumerate([31,32,33,34,35,36,37,38]):
                draw_tooth(t, lo_cols[i+9])
            
            # Quick selection helpers
            if st.session_state.pending_teeth:
                st.caption(f"✓ محدد: {len(st.session_state.pending_teeth)} سن")
                col_clear, _ = st.columns([1, 3])
                if col_clear.button("🔄 إلغاء التحديد", type="secondary"):
                    st.session_state.pending_teeth = {}
                    st.rerun()
        
        # =========================================================================
        #                    MATERIAL SELECTION FOR PENDING TEETH
        # =========================================================================
        
        if st.session_state.pending_teeth:
            st.divider()
            with st.container(border=True):
                st.subheader("⚡ اختيار الخامة للأسنان المحددة")
                
                pending_numbers = sorted([int(k) for k in st.session_state.pending_teeth.keys()])
                
                # Group consecutive teeth
                groups = []
                current_group = []
                
                for num in pending_numbers:
                    if not current_group or num == current_group[-1] + 1:
                        current_group.append(num)
                    else:
                        groups.append(current_group)
                        current_group = [num]
                if current_group:
                    groups.append(current_group)
                
                # Process each group
                for group_idx, group in enumerate(groups):
                    teeth_str = "-".join(map(str, group))
                    
                    # Determine work type
                    if len(group) >= 2:
                        work_label = f"🌉 جسر {teeth_str}"
                        work_type = "bridge"
                    else:
                        work_label = f"👑 تاج {teeth_str}"
                        work_type = "crown"
                    
                    with st.expander(work_label, expanded=True):
                        col_mat, col_price = st.columns([2, 1])
                        
                        material = col_mat.selectbox(
                            "المادة / Material",
                            materials_list,
                            key=f"mat_group_{group_idx}",
                            help="اختر نوع الخامة المطلوبة"
                        )
                        
                        # Get and display price
                        price_row = prices_df[prices_df['material'] == material]
                        if not price_row.empty:
                            unit_price = price_row['price'].values[0]
                            total_price = unit_price * len(group)
                            
                            col_price.metric(
                                "السعر الإجمالي",
                                f"{total_price:,.0f} ج.م",
                                delta=f"{unit_price} × {len(group)}"
                            )
                            
                            # Confirm button
                            if st.button(
                                f"✅ تأكيد {work_type.title()} ({material})",
                                key=f"conf_group_{group_idx}",
                                type="primary",
                                use_container_width=True
                            ):
                                teeth_map = {
                                    str(t): {
                                        "material": material,
                                        "price": unit_price,
                                    }
                                    for t in group
                                }
                                
                                st.session_state.confirmed_items.append({
                                    "teeth": group,
                                    "teeth_map": teeth_map,
                                    "material": material,
                                    "price": total_price,
                                    "type": work_type,
                                    "label": work_label
                                })
                                
                                # Clear pending teeth
                                for t in group:
                                    if str(t) in st.session_state.pending_teeth:
                                        del st.session_state.pending_teeth[str(t)]
                                
                                st.success(f"✅ تم تأكيد {work_label} بنجاح!")
                                st.rerun()
                        else:
                            st.error("لم يتم العثور على السعر!")
    
    # =========================================================================
    #                    CASE SUMMARY
    # =========================================================================
    
    if st.session_state.confirmed_items:
        st.divider()
        with st.container(border=True):
            st.subheader("📋 ملخص الحالة - Case Summary")
            
            total_price = 0
            total_teeth = 0
            
            for idx, item in enumerate(st.session_state.confirmed_items):
                col_info, col_price, col_delete = st.columns([3, 1.5, 0.5])
                
                if item.get('type') == 'nightguard':
                    col_info.markdown(f"**{item['arch']}** - {item['material']}")
                else:
                    teeth_display = "-".join(map(str, item['teeth']))
                    col_info.markdown(f"**{item.get('label', teeth_display)}** - {item['material']}")
                
                col_price.markdown(f"💰 {item['price']:,.0f} ج.م")
                
                if col_delete.button("🗑️", key=f"del_summary_{idx}", help="حذف هذا العنصر"):
                    st.session_state.confirmed_items.pop(idx)
                    st.rerun()
                
                total_price += item['price']
                total_teeth += len(item['teeth'])
            
            # Display totals
            st.markdown("---")
            col_total1, col_total2 = st.columns(2)
            col_total1.metric("إجمالي الأسنان", total_teeth)
            col_total2.metric("الإجمالي", f"{total_price:,.0f} ج.م")
    
    # =========================================================================
    #                    CASE DETAILS
    # =========================================================================
    
    st.divider()
    with st.container(border=True):
        st.subheader("📝 تفاصيل الحالة - Case Details")
        
        col_shade, col_tech = st.columns(2)
        
        shade = col_shade.text_input(
            "🎨 اللون (Shade)",
            placeholder="A2, B3, etc.",
            help="اللون المطلوب للتركيبات"
        )
        
        lab_technician = col_tech.text_input(
            "👨‍🔧 الفني المسؤول",
            placeholder="اسم الفني",
            help="اختياري - اسم الفني المسؤول عن الحالة"
        )
        
        st.markdown("---")
        
        # Try-in option
        is_try_in = st.checkbox(
            "🦷 **إضافة مرحلة Try-in؟**",
            help="تفعيل في حالة الحاجة لتجربة مبدئية قبل التسليم النهائي"
        )
        
        t_date = None
        if is_try_in:
            t_date = st.date_input(
                "📅 موعد الـ Try-in",
                value=datetime.now() + timedelta(days=3),
                min_value=datetime.now().date(),
                help="تاريخ التجربة المبدئية"
            )
        
        # Dates
        col_entry, col_delivery = st.columns(2)
        
        e_date = col_entry.date_input(
            "📅 تاريخ الدخول *",
            value=datetime.now().date(),
            help="تاريخ استلام الحالة في المعمل"
        )
        
        d_date = col_delivery.date_input(
            "🚚 موعد التسليم النهائي *",
            value=datetime.now().date() + timedelta(days=7),
            min_value=e_date,
            help="الموعد المتوقع لتسليم الحالة"
        )
        
        # Validation warnings
        if d_date < e_date:
            st.warning("⚠️ تاريخ التسليم يجب أن يكون بعد تاريخ الدخول")
        
        if is_try_in and t_date:
            if t_date < e_date:
                st.warning("⚠️ موعد Try-in يجب أن يكون بعد تاريخ الدخول")
            if t_date > d_date:
                st.warning("⚠️ موعد Try-in يجب أن يكون قبل التسليم النهائي")
        
        # Priority
        priority = st.select_slider(
            "⚡ الأولوية",
            options=["عادي", "مهم", "عاجل"],
            value="عادي",
            help="حدد مستوى أولوية الحالة"
        )
        
        priority_map = {"عادي": "normal", "مهم": "important", "عاجل": "urgent"}
        
        # Notes
        notes = st.text_area(
            "🗒️ ملاحظات",
            placeholder="أي ملاحظات أو تعليمات خاصة بالحالة...",
            help="ملاحظات اختيارية"
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "📎 إرفاق ملف (صورة، PDF، تصميم، STL، إلخ)",
            type=["jpg", "jpeg", "png", "pdf", "stl", "obj", "zip", "rar"],
            help="ارفع أي ملف متعلق بالحالة (اختياري)"
        )
        
        attachment_path = None
        if uploaded_file is not None:
            file_extension = os.path.splitext(uploaded_file.name)[1]
            safe_filename = f"case_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
            file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            attachment_path = file_path
            st.success(f"✅ تم رفع الملف: {uploaded_file.name}")
    
    # =========================================================================
    #                    SAVE BUTTON
    # =========================================================================
    
    st.divider()
    
    if st.button(
        "💾 حفظ وتسجيل الحالة",
        type="primary",
        use_container_width=True,
        help="حفظ الحالة في قاعدة البيانات"
    ):
        # Validation
        errors = []
        
        if not patient_name:
            errors.append("❌ اسم المريض مطلوب")
        if not st.session_state.confirmed_items:
            errors.append("❌ يجب تأكيد الأسنان المطلوبة")
        if d_date < e_date:
            errors.append("❌ تاريخ التسليم يجب أن يكون بعد تاريخ الدخول")
        
        if errors:
            for error in errors:
                st.error(error)
            return
        
        # Prepare data
        combined_teeth_map = {}
        total_price = 0
        total_count = 0
        
        for item in st.session_state.confirmed_items:
            combined_teeth_map.update(item['teeth_map'])
            total_price += item['price']
            total_count += len(item['teeth'])
        
        doctor_value = selected_doctor if selected_doctor else selected_center
        center_value = selected_center if selected_center else None
        branch_value = selected_branch if selected_center else None
        
        # Create case data dictionary
        case_data = {
            'patient': patient_name,
            'doctor': doctor_value,
            'dental_center': center_value,
            'branch_name': branch_value,
            'entry_date': str(e_date),
            'expected_delivery': str(d_date),
            'color': shade,
            'teeth_map': json.dumps(combined_teeth_map),
            'notes': notes,
            'price': total_price,
            'count': total_count,
            'is_try_in': 1 if is_try_in else 0,
            'try_in_date': str(t_date) if t_date else None,
            'priority': priority_map.get(priority, 'normal'),
            'lab_technician': lab_technician if lab_technician else None,
            'attachment': attachment_path,
            'status': 'في المعمل'
        }
        
        # Save to database
        case_code = db.add_case(case_data)
        
        if case_code:
            st.success(f"""
                ✅ **تم الحفظ بنجاح!**
                
                - **الكود:** {case_code}
                - **المريض:** {patient_name}
                - **السعر الإجمالي:** {total_price:,.0f} ج.م
                - **عدد الأسنان:** {total_count}
                - **موعد التسليم:** {d_date}
            """)
            
            # Clear session state
            st.session_state.confirmed_items = []
            st.session_state.pending_teeth = {}
            st.session_state.nightguard_mode = False
            
            # Ask if user wants to add another case
            col_new, col_view = st.columns(2)
            if col_new.button("➕ تسجيل حالة جديدة", type="primary", use_container_width=True):
                st.rerun()
            if col_view.button("👀 عرض الأرشيف", use_container_width=True):
                st.switch_page("pages/archive.py")
        else:
            st.error("❌ حدث خطأ أثناء حفظ الحالة. يرجى المحاولة مرة أخرى.")
