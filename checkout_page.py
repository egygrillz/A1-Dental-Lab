# -*- coding: utf-8 -*-
import streamlit as st

def show_checkout_page(db):
    st.header("📤 تسليم الحالات")

    # البحث
    search = st.text_input("🔍 ابحث باسم المريض أو الكود")

    # الاستعلام الرئيسي للحالات في المعمل (including after Try-in)
    query = """
        SELECT 
            id,
            case_code,
            patient,
            doctor,
            entry_date,
            expected_delivery,
            is_try_in,
            try_in_date,
            status,
            count,
            color,
            notes
        FROM cases 
        WHERE status IN ('في المعمل', 'في المعمل - بعد Try-in')
    """
    params = []

    if search:
        query += " AND (patient LIKE ? OR case_code LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY entry_date DESC"

    results = db.run_query(query, tuple(params))

    if results.empty:
        st.info("لا توجد حالات في المعمل حالياً.")
        return

    # عرض كل حالة في كونتينر
    for _, row in results.iterrows():
        with st.container(border=True):
            # صف أول: معلومات أساسية
            c1, c2, c3 = st.columns([3, 2, 2])

            c1.markdown(f"**الكود:** {row['case_code']}")
            c1.markdown(f"**المريض:** {row['patient']}")
            c1.markdown(f"**الطبيب:** {row['doctor']}")

            c2.markdown(f"**تاريخ الدخول:** {row['entry_date']}")
            c2.markdown(f"**موعد التسليم المتوقع:** {row['expected_delivery']}")

            # Show Try-in status
            if row['is_try_in'] == 1:
                if row['status'] == 'في المعمل - بعد Try-in':
                    c3.markdown("✅ **تم تسليم Try-in**")
                    c3.markdown("**في انتظار التسليم النهائي**")
                else:
                    c3.markdown("⏳ **Try-in مطلوب**")
                    c3.markdown(f"موعد الـ Try-in: {row['try_in_date'] or 'غير محدد'}")
            else:
                c3.markdown("**نهائي فقط**")

            # صف تاني: تفاصيل إضافية
            c4, c5, c6 = st.columns([1.5, 1.5, 3])

            c4.markdown(f"**عدد الأسنان:** {row['count'] or 0}")
            c5.markdown(f"**اللون:** {row['color'] or 'غير محدد'}")

            # ملاحظات مختصرة
            notes_short = (row['notes'][:80] + "...") if row['notes'] and len(row['notes']) > 80 else row['notes'] or "لا توجد ملاحظات"
            c6.markdown(f"**ملاحظات:** {notes_short}")

            # أزرار التسليم
            btn_col1, btn_col2, _ = st.columns([1, 1, 3])

            # زرار Try-in (يظهر فقط إذا كان Try-in مطلوب ولم يتم تسليمه بعد)
            if row['is_try_in'] == 1 and row['status'] == 'في المعمل':
                if btn_col1.button("تم تسليم الـ Try-in", key=f"tryin_{row['id']}", use_container_width=True, type="secondary"):
                    confirm_key = f"confirm_tryin_{row['id']}"
                    if not st.session_state.get(confirm_key, False):
                        st.session_state[confirm_key] = True
                        st.warning("هل أنت متأكد من تسليم الـ Try-in؟ اضغط الزر مرة أخرى للتأكيد.")
                        st.rerun()
                    else:
                        # Update status to show Try-in was delivered, but keep in lab
                        db.run_action("""
                            UPDATE cases 
                            SET status = 'في المعمل - بعد Try-in'
                            WHERE id = ?
                        """, (row['id'],))
                        st.session_state[confirm_key] = False
                        st.success("✅ تم تسجيل تسليم الـ Try-in - الحالة لا تزال في المعمل")
                        st.rerun()

            # زرار التسليم النهائي (دائماً موجود)
            if btn_col2.button("تم التسليم النهائي", key=f"final_{row['id']}", use_container_width=True, type="primary"):
                confirm_key = f"confirm_final_{row['id']}"
                if not st.session_state.get(confirm_key, False):
                    st.session_state[confirm_key] = True
                    st.warning("⚠️ هل أنت متأكد من تسليم الحالة نهائياً؟\nسيتم إزالة الحالة من قائمة المعمل.\nاضغط الزر مرة أخرى للتأكيد.")
                    st.rerun()
                else:
                    # Mark as delivered - this removes it from the list
                    db.run_action("""
                        UPDATE cases 
                        SET status = 'تم التسليم',
                            delivery_date = DATE('now')
                        WHERE id = ?
                    """, (row['id'],))
                    st.session_state[confirm_key] = False
                    st.success("✅ تم تسجيل التسليم النهائي - تم إزالة الحالة من المعمل")
                    st.rerun()

            st.markdown("---")