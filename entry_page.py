# -*- coding: utf-8 -*-
import streamlit as st
import json
from datetime import datetime
import os
from collections import defaultdict

# Folder for uploaded files
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def show_entry_page(db):
    st.header("📥 تسجيل حالة جديدة")

    # ────────────────────────────────────────────────
    # Session state
    # ────────────────────────────────────────────────
    if 'confirmed_teeth' not in st.session_state:
        st.session_state.confirmed_teeth = {}     # teeth that are already confirmed
    if 'pending_teeth' not in st.session_state:
        st.session_state.pending_teeth = {}       # teeth currently selected (waiting for confirmation)
    if 'nightguard_mode' not in st.session_state:
        st.session_state.nightguard_mode = False

    # 1. Doctor & Patient
    docs_df = db.run_query("SELECT name FROM doctors_list")
    if docs_df.empty:
        st.warning("⚠️ يرجى إضافة دكاترة أولاً من صفحة الإدارة.")
        return

    col_doc, col_pat = st.columns(2)
    selected_doctor = col_doc.selectbox("👨‍⚕️ اسم الدكتور", docs_df['name'].tolist())
    patient_name = col_pat.text_input("👤 اسم المريض")

    # Load doctor's prices
    prices_df = db.run_query("SELECT material, price FROM doctors_prices WHERE doc_name = ?", (selected_doctor,))
    materials_list = prices_df['material'].tolist() if not prices_df.empty else []

    # Check if nightguard is available
    has_nightguard = any("nightguard" in mat.lower() for mat in materials_list)

    # ────────────────────────────────────────────────
    # Nightguard toggle
    # ────────────────────────────────────────────────
    if has_nightguard:
        st.divider()
        nightguard_checkbox = st.checkbox(
            "🌙 هل تريد تسجيل Nightguard؟ (سيتم اختيار الفك كامل)",
            value=st.session_state.nightguard_mode,
            key="ng_toggle"
        )
        
        if nightguard_checkbox != st.session_state.nightguard_mode:
            st.session_state.nightguard_mode = nightguard_checkbox
            # Clear pending teeth when switching modes
            st.session_state.pending_teeth = {}
            st.rerun()

    # ────────────────────────────────────────────────
    # If Nightguard mode: Show arch selection only
    # ────────────────────────────────────────────────
    if st.session_state.nightguard_mode:
        st.subheader("🦷 اختيار الفك للـ Nightguard")
        
        # Get nightguard material
        nightguard_material = next((mat for mat in materials_list if "nightguard" in mat.lower()), None)
        
        if nightguard_material:
            nightguard_price = prices_df[prices_df['material'] == nightguard_material]['price'].values[0]
            
            st.info(f"💰 سعر الـ Nightguard: {nightguard_price} ج.م للفك الواحد")
            
            col1, col2 = st.columns(2)
            
            # Upper arch button
            if col1.button("🦷 الفك العلوي", use_container_width=True, type="primary"):
                upper_teeth = [18,17,16,15,14,13,12,11,21,22,23,24,25,26,27,28]
                
                for tooth in upper_teeth:
                    st.session_state.confirmed_teeth[str(tooth)] = {
                        "material": nightguard_material,
                        "price": nightguard_price,
                        "type": "nightguard",
                        "arch": "الفك العلوي"
                    }
                
                st.success(f"✅ تم إضافة Nightguard - الفك العلوي ({nightguard_material})")
                st.rerun()
            
            # Lower arch button
            if col2.button("🦷 الفك السفلي", use_container_width=True, type="primary"):
                lower_teeth = [48,47,46,45,44,43,42,41,31,32,33,34,35,36,37,38]
                
                for tooth in lower_teeth:
                    st.session_state.confirmed_teeth[str(tooth)] = {
                        "material": nightguard_material,
                        "price": nightguard_price,
                        "type": "nightguard",
                        "arch": "الفك السفلي"
                    }
                
                st.success(f"✅ تم إضافة Nightguard - الفك السفلي ({nightguard_material})")
                st.rerun()
            
            # Show confirmed nightguards
            if st.session_state.confirmed_teeth:
                st.write("**الـ Nightguards المضافة:**")
                nightguard_arches = set()
                for tooth_str, data in st.session_state.confirmed_teeth.items():
                    if data.get('type') == 'nightguard':
                        nightguard_arches.add(data.get('arch', 'unknown'))
                
                for arch in nightguard_arches:
                    st.markdown(f"• {arch} ({nightguard_material})")
        else:
            st.error("لم يتم العثور على مادة Nightguard في قائمة الأسعار!")

    # ────────────────────────────────────────────────
    # Regular mode: Show tooth map
    # ────────────────────────────────────────────────
    else:
        st.subheader("🦷 خريطة الأسنان")
        st.markdown("""
            <style>
            .v-line { border-left: 2px solid white; height: 50px; margin: auto; width: 1px; }
            .h-line { border-top: 2px solid white; margin: 5px 0px; }
            </style>
        """, unsafe_allow_html=True)

        def draw_tooth(num, col):
            tooth_str = str(num)

            if tooth_str in st.session_state.confirmed_teeth:
                label = f"🦷 {num} ✓"
                btn_type = "primary"
            elif tooth_str in st.session_state.pending_teeth:
                label = f"🦷 {num} ●"
                btn_type = "primary"
            else:
                label = str(num)
                btn_type = "secondary"

            if col.button(label, key=f"t_{num}", use_container_width=True, type=btn_type):
                if tooth_str in st.session_state.confirmed_teeth:
                    st.info("هذا السن تم تأكيده بالفعل")
                else:
                    # Toggle pending selection
                    if tooth_str in st.session_state.pending_teeth:
                        del st.session_state.pending_teeth[tooth_str]
                    else:
                        st.session_state.pending_teeth[tooth_str] = {"selected": True}
                    st.rerun()

        # Upper jaw
        up_cols = st.columns([1,1,1,1,1,1,1,1, 0.2, 1,1,1,1,1,1,1,1])
        for i, t in enumerate([18,17,16,15,14,13,12,11]): draw_tooth(t, up_cols[i])
        up_cols[8].markdown('<div class="v-line"></div>', unsafe_allow_html=True)
        for i, t in enumerate([21,22,23,24,25,26,27,28]): draw_tooth(t, up_cols[i+9])

        st.markdown('<div class="h-line"></div>', unsafe_allow_html=True)

        # Lower jaw
        lo_cols = st.columns([1,1,1,1,1,1,1,1, 0.2, 1,1,1,1,1,1,1,1])
        for i, t in enumerate([48,47,46,45,44,43,42,41]): draw_tooth(t, lo_cols[i])
        lo_cols[8].markdown('<div class="v-line"></div>', unsafe_allow_html=True)
        for i, t in enumerate([31,32,33,34,35,36,37,38]): draw_tooth(t, lo_cols[i+9])

        # Quick selection buttons for regular materials
        if st.session_state.pending_teeth:
            st.divider()
            st.subheader("⚡ اختيار الخامة للأسنان المحددة")

            # Group pending teeth by consecutive numbers
            pending_numbers = sorted([int(k) for k in st.session_state.pending_teeth.keys()])
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

            # Show groups and material selection
            for group in groups:
                teeth_str = "-".join(map(str, group))
                label = f"جسر {teeth_str}" if len(group) >= 2 else f"سن {teeth_str}"
                st.markdown(f"**{label}**")

                material = st.selectbox(
                    f"اختر الخامة لـ {label}",
                    options=materials_list if materials_list else ["-- اختر --"],
                    key=f"mat_{teeth_str}"
                )

                if material and material != "-- اختر --":
                    price_row = prices_df[prices_df['material'] == material]
                    price = price_row['price'].values[0] if not price_row.empty else 0

                    if st.button(f"✅ تأكيد {label} ({material})", key=f"conf_{teeth_str}"):
                        for t in group:
                            st.session_state.confirmed_teeth[str(t)] = {
                                "material": material,
                                "price": price,
                                "type": "crown/bridge"
                            }
                        st.success(f"تم تأكيد {label} بنجاح!")
                        # Remove from pending
                        for t in group:
                            if str(t) in st.session_state.pending_teeth:
                                del st.session_state.pending_teeth[str(t)]
                        st.rerun()

    # ────────────────────────────────────────────────
    # Summary of all confirmed items (both modes)
    # ────────────────────────────────────────────────
    if st.session_state.confirmed_teeth:
        st.divider()
        st.subheader("📋 ملخص الحالة")
        
        # Group nightguards separately
        nightguard_arches = set()
        regular_groups = defaultdict(list)
        
        for tooth_str, data in st.session_state.confirmed_teeth.items():
            if data.get('type') == 'nightguard':
                arch = data.get('arch', 'unknown')
                nightguard_arches.add((arch, data['material']))
            else:
                key = (data["material"], data["type"])
                regular_groups[key].append(int(tooth_str))
        
        # Display nightguards
        if nightguard_arches:
            st.write("**Nightguards:**")
            for arch, material in nightguard_arches:
                st.markdown(f"• {arch} ({material})")
        
        # Display regular teeth
        if regular_groups:
            if nightguard_arches:
                st.write("**تيجان/جسور:**")
            
            for (material, typ), teeth_list in regular_groups.items():
                sorted_teeth = sorted(teeth_list)
                current_group = []
                groups = []

                for t in sorted_teeth:
                    if not current_group or t == current_group[-1] + 1:
                        current_group.append(t)
                    else:
                        groups.append(current_group)
                        current_group = [t]
                if current_group:
                    groups.append(current_group)

                for g in groups:
                    teeth_str = "-".join(map(str, g))
                    if len(g) >= 2:
                        st.markdown(f"• جسر {teeth_str} ({material})")
                    else:
                        st.markdown(f"• سن {teeth_str} ({material})")

    # ────────────────────────────────────────────────
    # Case details
    # ────────────────────────────────────────────────
    st.divider()
    st.subheader("📝 تفاصيل الحالة")
    
    col_m, col_s = st.columns(2)
    main_material = col_m.selectbox("💎 المادة الرئيسية", materials_list if materials_list else ["--"])
    shade = col_s.text_input("🎨 اللون (Shade)")

    st.write("---")
    is_try_in = st.checkbox("🦷 إضافة مرحلة Try-in؟ (سيتم حساب تكلفة PMMA إضافية)")
    t_date = None
    if is_try_in:
        t_date = st.date_input("📅 موعد الـ Try-in", datetime.now())

    col_i, col_o = st.columns(2)
    e_date = col_i.date_input("📅 تاريخ الدخول", datetime.now())
    d_date = col_o.date_input("🚚 موعد التسليم النهائي", datetime.now())
    
    # Validate dates
    if d_date < e_date:
        st.warning("⚠️ تاريخ التسليم يجب أن يكون بعد تاريخ الدخول")
    
    if is_try_in and t_date:
        if t_date < e_date:
            st.warning("⚠️ موعد Try-in يجب أن يكون بعد تاريخ الدخول")
        if t_date > d_date:
            st.warning("⚠️ موعد Try-in يجب أن يكون قبل التسليم النهائي")
    
    notes = st.text_area("🗒️ ملاحظات")

    # File upload
    uploaded_file = st.file_uploader(
        "إرفاق ملف (صورة، PDF، تصميم، إلخ)",
        type=["jpg", "jpeg", "png", "pdf", "stl", "zip", "rar"],
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
        st.success(f"تم رفع الملف: {uploaded_file.name}")

    # ────────────────────────────────────────────────
    # Save button
    # ────────────────────────────────────────────────
    if st.button("💾 حفظ وتسجيل الحالة", type="primary", use_container_width=True):
        # Validation
        errors = []
        if not patient_name:
            errors.append("اسم المريض مطلوب")
        if not st.session_state.confirmed_teeth:
            errors.append("يجب تأكيد الأسنان المطلوبة")
        if d_date < e_date:
            errors.append("تاريخ التسليم يجب أن يكون بعد تاريخ الدخول")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
            return

        teeth_data = st.session_state.confirmed_teeth

        # Calculate price - for nightguard, count as 1 unit per arch
        base_p = 0
        nightguard_arches = set()
        
        for tooth_str, item in teeth_data.items():
            if item.get('type') == 'nightguard':
                arch = item.get('arch', 'unknown')
                if arch not in nightguard_arches:
                    nightguard_arches.add(arch)
                    base_p += item['price']  # Add price once per arch
            else:
                base_p += item['price']
        
        try_p = 0
        if is_try_in:
            pmma_row = prices_df[prices_df['material'].str.upper() == "PMMA"]
            if not pmma_row.empty:
                # For nightguard, don't add PMMA cost
                non_nightguard_count = sum(1 for item in teeth_data.values() if item.get('type') != 'nightguard')
                try_p = non_nightguard_count * pmma_row['price'].values[0]
            else:
                st.warning("⚠️ لم يتم العثور على سعر PMMA، تم حساب تكلفة الـ Try-in بـ 0")
        
        total_p = base_p + try_p
        c_code = f"A1-{datetime.now().strftime('%y%m%d%H%M')}"

        # ─── IMPORTANT CHANGE ─────────────────────────────────────
        # We now explicitly set status = 'في المعمل'
        # This matches what checkout_page.py is looking for
        success = db.run_action("""
            INSERT INTO cases (
                case_code, doctor, patient, color, teeth_map, notes, 
                entry_date, expected_delivery, count, price, is_try_in, try_in_date, 
                is_paid, attachment, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
        """, (
            c_code, selected_doctor, patient_name, shade, json.dumps(teeth_data), 
            notes, str(e_date), str(d_date), len(teeth_data), total_p, 
            (1 if is_try_in else 0), (str(t_date) if t_date else None),
            attachment_path,
            'في المعمل'                      # ← This was missing → now fixed
        ))
        
        if success:
            st.success(f"✅ تم الحفظ! الكود: {c_code} | السعر الإجمالي: {total_p:,} ج.م")
            # Reset form
            st.session_state.confirmed_teeth = {}
            st.session_state.pending_teeth = {}
            st.session_state.nightguard_mode = False
            st.rerun()
        else:
            st.error("حدث خطأ أثناء حفظ الحالة. حاول مرة أخرى.")