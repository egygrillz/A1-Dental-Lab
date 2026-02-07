import streamlit as st
import pandas as pd

def show_doctors_page(db):
    st.header("⚙️ إعدادات المعمل والأسعار")

    tab1, tab2 = st.tabs(["👨‍⚕️ إدارة الأطباء", "💰 قائمة الأسعار لكل دكتور"])

    with tab1:
        st.subheader("إضافة طبيب جديد")
        with st.form("add_doc", clear_on_submit=True):
            name = st.text_input("اسم الدكتور:")
            if st.form_submit_button("إضافة"):
                if name:
                    db.run_action("INSERT OR IGNORE INTO doctors_list (name, doc_code) VALUES (?,?)", 
                                 (name, f"D-{name[:3].upper()}"))
                    st.success(f"تمت إضافة د/ {name}")
                    st.rerun()

        st.divider()
        docs = db.run_query("SELECT name, doc_code FROM doctors_list")
        if not docs.empty:
            for idx, row in docs.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{row['name']}** ({row['doc_code']})")
                if c2.button("🗑️", key=f"del_{idx}"):
                    db.run_action("DELETE FROM doctors_list WHERE name=?", (row['name'],))
                    st.rerun()

    with tab2:
        docs_list = db.run_query("SELECT name FROM doctors_list")['name'].tolist()
        if docs_list:
            sel_doc = st.selectbox("اختر الدكتور لتعديل أسعاره:", docs_list)
            
            with st.container(border=True):
                st.write(f"إضافة خامة جديدة لـ د/ {sel_doc}")
                c1, c2, c3 = st.columns([2,1,1])
                m_name = c1.text_input("اسم الخامة (Material):", placeholder="Zircon...")
                m_price = c2.number_input("السعر:", min_value=0, step=50)
                if c3.button("➕ حفظ السعر"):
                    if m_name:
                        db.run_action("""
                            INSERT INTO doctors_prices (doc_name, material, price) VALUES (?,?,?)
                            ON CONFLICT(doc_name, material) DO UPDATE SET price=excluded.price
                        """, (sel_doc, m_name, m_price))
                        st.success("تم الحفظ")
                        st.rerun()

            st.divider()
            st.write(f"📊 قائمة أسعار د/ {sel_doc}")
            prices = db.run_query("SELECT id, material, price FROM doctors_prices WHERE doc_name=?", (sel_doc,))
            if not prices.empty:
                edited = st.data_editor(prices, column_config={"id": None}, hide_index=True, use_container_width=True)
                if st.button("💾 حفظ التعديلات"):
                    for _, r in edited.iterrows():
                        db.run_action("UPDATE doctors_prices SET price=? WHERE id=?", (r['price'], r['id']))
                    st.success("تم التحديث")
            else:
                st.info("لا توجد خامات مضافة لهذا الدكتور.")