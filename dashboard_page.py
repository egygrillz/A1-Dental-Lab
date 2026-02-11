# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def show_dashboard_page(db):
    """Display dashboard with key metrics and statistics"""
    
    st.header("📊 لوحة المعلومات - Dashboard")
    
    # =============================================================================
    #                           KEY METRICS
    # =============================================================================
    st.subheader("📈 المؤشرات الرئيسية")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # 1. Cases in lab
    in_lab_query = """
        SELECT COUNT(*) as count 
        FROM cases 
        WHERE status IN ('في المعمل', 'في المعمل - بعد Try-in')
    """
    in_lab = db.run_query(in_lab_query)
    in_lab_count = in_lab['count'].values[0] if not in_lab.empty else 0
    col1.metric("🔵 الحالات في المعمل", in_lab_count)
    
    # 2. Delivered this month
    delivered_query = """
        SELECT COUNT(*) as count 
        FROM cases 
        WHERE status = 'تم التسليم' 
        AND strftime('%Y-%m', delivery_date) = strftime('%Y-%m', 'now')
    """
    delivered = db.run_query(delivered_query)
    delivered_count = delivered['count'].values[0] if not delivered.empty else 0
    col2.metric("🟢 التسليمات هذا الشهر", delivered_count)
    
    # 3. Total revenue this month
    revenue_query = """
        SELECT COALESCE(SUM(price), 0) as total 
        FROM cases 
        WHERE status = 'تم التسليم' 
        AND strftime('%Y-%m', delivery_date) = strftime('%Y-%m', 'now')
    """
    revenue = db.run_query(revenue_query)
    total_rev = revenue['total'].values[0] if not revenue.empty else 0
    col3.metric("💰 الإيرادات الشهرية", f"{total_rev:,.0f} ج.م")
    
    # 4. Unpaid cases
    unpaid_query = """
        SELECT COUNT(*) as count 
        FROM cases 
        WHERE is_paid = 0 AND status = 'تم التسليم'
    """
    unpaid = db.run_query(unpaid_query)
    unpaid_count = unpaid['count'].values[0] if not unpaid.empty else 0
    col4.metric("⚠️ حالات غير مدفوعة", unpaid_count)
    
    st.divider()
    
    # =============================================================================
    #                           UPCOMING DELIVERIES
    # =============================================================================
    st.subheader("📅 الحالات المقرر تسليمها قريباً")
    
    # Get cases due in next 7 days
    upcoming_query = """
        SELECT 
            case_code, patient, doctor, expected_delivery,
            is_try_in, try_in_date, status
        FROM cases
        WHERE status IN ('في المعمل', 'في المعمل - بعد Try-in')
        AND date(expected_delivery) BETWEEN date('now') AND date('now', '+7 days')
        ORDER BY expected_delivery ASC
    """
    upcoming_cases = db.run_query(upcoming_query)
    
    if not upcoming_cases.empty:
        for _, row in upcoming_cases.iterrows():
            days_left = (pd.to_datetime(row['expected_delivery']) - pd.Timestamp.now()).days
            
            # Color code based on urgency
            if days_left <= 0:
                urgency_color = "🔴"
                urgency_text = "متأخر!"
            elif days_left == 1:
                urgency_color = "🟠"
                urgency_text = "غداً"
            elif days_left == 2:
                urgency_color = "🟡"
                urgency_text = "بعد يومين"
            else:
                urgency_color = "🟢"
                urgency_text = f"بعد {days_left} أيام"
            
            col_a, col_b, col_c = st.columns([1, 3, 1])
            col_a.write(urgency_color)
            col_b.write(f"**{row['patient']}** - د/ {row['doctor']} | كود: `{row['case_code']}`")
            col_c.write(urgency_text)
    else:
        st.info("لا توجد حالات مقرر تسليمها في الأيام السبعة القادمة")
    
    st.divider()
    
    # =============================================================================
    #                           CHARTS AND STATISTICS
    # =============================================================================
    
    tab1, tab2, tab3 = st.tabs(["📊 الإحصائيات", "👨‍⚕️ الأطباء", "📅 التقويم"])
    
    with tab1:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("📈 الحالات الجديدة (آخر 30 يوم)")
            
            daily_cases_query = """
                SELECT 
                    entry_date,
                    COUNT(*) as count
                FROM cases
                WHERE date(entry_date) >= date('now', '-30 days')
                GROUP BY entry_date
                ORDER BY entry_date
            """
            daily_cases = db.run_query(daily_cases_query)
            
            if not daily_cases.empty:
                st.line_chart(daily_cases.set_index('entry_date')['count'])
            else:
                st.info("لا توجد بيانات كافية")
        
        with col_chart2:
            st.subheader("💵 الإيرادات (آخر 8 أسابيع)")
            
            weekly_revenue_query = """
                SELECT 
                    strftime('%Y-W%W', delivery_date) as week,
                    SUM(price) as revenue
                FROM cases
                WHERE status = 'تم التسليم'
                AND date(delivery_date) >= date('now', '-56 days')
                GROUP BY week
                ORDER BY week
            """
            weekly_rev = db.run_query(weekly_revenue_query)
            
            if not weekly_rev.empty:
                st.bar_chart(weekly_rev.set_index('week')['revenue'])
            else:
                st.info("لا توجد بيانات كافية")
    
    with tab2:
        st.subheader("👨‍⚕️ إحصائيات الأطباء")
        
        # Doctor statistics
        doc_stats_query = """
            SELECT 
                doctor,
                COUNT(*) as total_cases,
                SUM(CASE WHEN status = 'تم التسليم' THEN 1 ELSE 0 END) as delivered,
                SUM(CASE WHEN status IN ('في المعمل', 'في المعمل - بعد Try-in') THEN 1 ELSE 0 END) as in_lab,
                COALESCE(SUM(CASE WHEN status = 'تم التسليم' THEN price ELSE 0 END), 0) as total_revenue,
                COALESCE(SUM(CASE WHEN is_paid = 0 AND status = 'تم التسليم' THEN price ELSE 0 END), 0) as unpaid
            FROM cases
            GROUP BY doctor
            ORDER BY total_cases DESC
        """
        doc_stats = db.run_query(doc_stats_query)
        
        if not doc_stats.empty:
            # Format the data for display
            doc_stats['total_revenue'] = doc_stats['total_revenue'].apply(lambda x: f"{x:,.0f} ج.م")
            doc_stats['unpaid'] = doc_stats['unpaid'].apply(lambda x: f"{x:,.0f} ج.م")
            
            # Rename columns for Arabic display
            doc_stats_display = doc_stats.rename(columns={
                'doctor': 'الطبيب',
                'total_cases': 'إجمالي الحالات',
                'delivered': 'تم التسليم',
                'in_lab': 'في المعمل',
                'total_revenue': 'إجمالي الإيرادات',
                'unpaid': 'مديونيات'
            })
            
            st.dataframe(doc_stats_display, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد بيانات")
    
    with tab3:
        st.subheader("📅 التقويم - الحالات حسب الموعد")
        
        # Get all in-lab cases with expected delivery
        calendar_query = """
            SELECT 
                expected_delivery,
                COUNT(*) as count
            FROM cases
            WHERE status IN ('في المعمل', 'في المعمل - بعد Try-in')
            AND expected_delivery IS NOT NULL
            GROUP BY expected_delivery
            ORDER BY expected_delivery
        """
        calendar_data = db.run_query(calendar_query)
        
        if not calendar_data.empty:
            # Show as a simple table
            calendar_data['expected_delivery'] = pd.to_datetime(calendar_data['expected_delivery'])
            calendar_data['day_name'] = calendar_data['expected_delivery'].dt.day_name()
            
            # Rename for display
            calendar_display = calendar_data.rename(columns={
                'expected_delivery': 'التاريخ',
                'count': 'عدد الحالات',
                'day_name': 'اليوم'
            })
            
            st.dataframe(calendar_display, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد حالات في المعمل حالياً")
    
    st.divider()
    
   


if __name__ == "__main__":
    # For testing
    from database import DatabaseManager
    db = DatabaseManager()
    show_dashboard_page(db)
