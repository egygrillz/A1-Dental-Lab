import streamlit as st
import pandas as pd

def show_doctors_page(db):
    st.header("⚙️ إعدادات المعمل والأسعار")

    tab1, tab2, tab3 = st.tabs(["👨‍⚕️ إدارة الأطباء", "🏥 إدارة مراكز الأسنان", "💰 قائمة الأسعار"])

    # ============================================================================
    # TAB 1: Doctors Management
    # ============================================================================
    with tab1:
        st.subheader("إضافة طبيب جديد")
        with st.form("add_doc", clear_on_submit=True):
            name = st.text_input("اسم الدكتور:")
            if st.form_submit_button("إضافة"):
                if name:
                    db.run_action(
                        "INSERT OR IGNORE INTO doctors_list (name, doc_code, is_center) VALUES (?,?,?)", 
                        (name, f"D-{name[:3].upper()}", 0)
                    )
                    st.success(f"تمت إضافة د/ {name}")
                    st.rerun()

        st.divider()
        st.subheader("قائمة الأطباء")
        docs = db.run_query("SELECT name, doc_code FROM doctors_list WHERE is_center = 0 AND center_parent IS NULL")
        if not docs.empty:
            for idx, row in docs.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{row['name']}** ({row['doc_code']})")
                if c2.button("🗑️", key=f"del_doc_{idx}"):
                    db.run_action("DELETE FROM doctors_list WHERE name=? AND is_center=0", (row['name'],))
                    st.rerun()
        else:
            st.info("لا يوجد أطباء مسجلين")

    # ============================================================================
    # TAB 2: Dental Centers Management
    # ============================================================================
    with tab2:
        st.subheader("إضافة مركز أسنان جديد")
        with st.form("add_center", clear_on_submit=True):
            center_name = st.text_input("اسم المركز:")
            if st.form_submit_button("إضافة المركز"):
                if center_name:
                    db.run_action(
                        "INSERT OR IGNORE INTO doctors_list (name, doc_code, is_center) VALUES (?,?,?)", 
                        (center_name, f"C-{center_name[:3].upper()}", 1)
                    )
                    st.success(f"تمت إضافة مركز {center_name}")
                    st.rerun()

        st.divider()
        st.subheader("قائمة المراكز والفروع")
        
        centers = db.run_query("SELECT name, doc_code FROM doctors_list WHERE is_center = 1")
        if not centers.empty:
            for idx, center_row in centers.iterrows():
                with st.expander(f"🏥 {center_row['name']}", expanded=False):
                    # Center info
                    col_info, col_del = st.columns([4, 1])
                    col_info.write(f"**كود المركز:** {center_row['doc_code']}")
                    if col_del.button("🗑️ حذف المركز", key=f"del_center_{idx}"):
                        # Delete center and all branches
                        db.run_action("DELETE FROM doctors_list WHERE name=? OR center_parent=?", 
                                     (center_row['name'], center_row['name']))
                        st.rerun()
                    
                    st.divider()
                    
                    # Add branch
                    st.write("**إضافة فرع جديد:**")
                    with st.form(f"add_branch_{idx}", clear_on_submit=True):
                        branch_name = st.text_input("اسم الفرع:", key=f"branch_input_{idx}")
                        if st.form_submit_button("إضافة الفرع"):
                            if branch_name:
                                db.run_action(
                                    "INSERT OR IGNORE INTO doctors_list (name, doc_code, is_center, center_parent) VALUES (?,?,?,?)", 
                                    (branch_name, f"B-{branch_name[:3].upper()}", 0, center_row['name'])
                                )
                                st.success(f"تمت إضافة فرع {branch_name}")
                                st.rerun()
                    
                    # List branches
                    branches = db.run_query(
                        "SELECT name FROM doctors_list WHERE center_parent = ?", 
                        (center_row['name'],)
                    )
                    
                    if not branches.empty:
                        st.write("**الفروع:**")
                        for bidx, branch_row in branches.iterrows():
                            bcol1, bcol2 = st.columns([4, 1])
                            bcol1.write(f"📍 {branch_row['name']}")
                            if bcol2.button("🗑️", key=f"del_branch_{idx}_{bidx}"):
                                db.run_action("DELETE FROM doctors_list WHERE name=? AND center_parent=?", 
                                            (branch_row['name'], center_row['name']))
                                st.rerun()
                    else:
                        st.info("لا توجد فروع لهذا المركز")
        else:
            st.info("لا توجد مراكز مسجلة")

    # ============================================================================
    # TAB 3: Price Lists
    # ============================================================================
    with tab3:
        # Get all entities (doctors and centers)
        all_entities = db.run_query("""
            SELECT name, is_center 
            FROM doctors_list 
            WHERE center_parent IS NULL
            ORDER BY is_center DESC, name
        """)
        
        if all_entities.empty:
            st.warning("يرجى إضافة أطباء أو مراكز أولاً")
            return
        
        # Create display names
        entity_names = []
        for _, row in all_entities.iterrows():
            prefix = "🏥 " if row['is_center'] == 1 else "👨‍⚕️ "
            entity_names.append(prefix + row['name'])
        
        selected_display = st.selectbox("اختر الطبيب أو المركز لتعديل أسعاره:", entity_names)
        selected_entity = selected_display.split(" ", 1)[1]  # Remove emoji prefix
        
        with st.container(border=True):
            st.write(f"إضافة خامة جديدة لـ {selected_entity}")
            c1, c2, c3 = st.columns([2,1,1])
            m_name = c1.text_input("اسم الخامة (Material):", placeholder="Zircon...")
            m_price = c2.number_input("السعر:", min_value=0, step=50)
            if c3.button("➕ حفظ السعر"):
                if m_name:
                    db.run_action("""
                        INSERT INTO doctors_prices (doc_name, material, price) VALUES (?,?,?)
                        ON CONFLICT(doc_name, material) DO UPDATE SET price=excluded.price
                    """, (selected_entity, m_name, m_price))
                    st.success("تم الحفظ")
                    st.rerun()

        st.divider()
        st.write(f"📊 قائمة أسعار {selected_entity}")
        prices = db.run_query("SELECT id, material, price FROM doctors_prices WHERE doc_name=?", (selected_entity,))
        if not prices.empty:
            # Display as editable table
            for idx, row in prices.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"**{row['material']}**")
                
                new_price = col2.number_input(
                    "السعر", 
                    value=float(row['price']), 
                    min_value=0.0, 
                    step=50.0,
                    key=f"price_{row['id']}"
                )
                
                if col3.button("💾 تحديث", key=f"update_{row['id']}"):
                    db.run_action("UPDATE doctors_prices SET price=? WHERE id=?", (new_price, row['id']))
                    st.success("تم التحديث")
                    st.rerun()
                
                if col3.button("🗑️ حذف", key=f"del_price_{row['id']}"):
                    db.run_action("DELETE FROM doctors_prices WHERE id=?", (row['id'],))
                    st.rerun()
        else:
            st.info("لا توجد خامات مضافة.")
