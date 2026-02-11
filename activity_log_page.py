# -*- coding: utf-8 -*-
"""
Activity Log Viewer - Complete System Audit Trail
سجل النشاطات
"""

import streamlit as st
import pandas as pd
from auth_manager import AuthManager, require_permission
from datetime import datetime, timedelta
import json


@require_permission('reports', 'view')
def show_activity_log_page():
    """Activity log viewer with advanced filtering"""
    
    st.header("📋 سجل النشاطات - Activity Log")
    
    auth = AuthManager()
    current_user = st.session_state.username
    current_role = st.session_state.role
    
    st.markdown("""
    📊 **نظام المراقبة الشامل**
    - عرض جميع الأنشطة في النظام
    - تتبع إجراءات كل مستخدم
    - فلترة متقدمة حسب المستخدم، النشاط، أو التاريخ
    - تصدير التقارير
    """)
    
    # =========================================================================
    #                    FILTERS
    # =========================================================================
    
    with st.container(border=True):
        st.subheader("🔍 الفلاتر - Filters")
        
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        # User filter
        with col_filter1:
            all_users = auth.get_all_users()
            user_options = ['الكل'] + [u['username'] for u in all_users]
            user_names = ['الكل'] + [f"{u['full_name']} ({u['username']})" for u in all_users]
            
            selected_user_idx = st.selectbox(
                "المستخدم",
                range(len(user_options)),
                format_func=lambda x: user_names[x]
            )
            
            selected_user = None if selected_user_idx == 0 else user_options[selected_user_idx]
        
        # Module filter
        with col_filter2:
            modules = ['الكل', 'system', 'cases', 'doctors', 'invoices', 'users', 'reports', 'settings']
            module_names = {
                'الكل': 'الكل',
                'system': 'النظام',
                'cases': 'الحالات',
                'doctors': 'الأطباء',
                'invoices': 'الفواتير',
                'users': 'المستخدمين',
                'reports': 'التقارير',
                'settings': 'الإعدادات'
            }
            
            selected_module = st.selectbox(
                "القسم",
                modules,
                format_func=lambda x: module_names.get(x, x)
            )
            
            if selected_module == 'الكل':
                selected_module = None
        
        # Action type filter
        with col_filter3:
            actions = ['الكل', 'login', 'logout', 'create', 'update', 'delete', 'view', 'export']
            action_names = {
                'الكل': 'الكل',
                'login': 'تسجيل دخول',
                'logout': 'تسجيل خروج',
                'create': 'إنشاء',
                'update': 'تعديل',
                'delete': 'حذف',
                'view': 'عرض',
                'export': 'تصدير'
            }
            
            selected_action = st.selectbox(
                "نوع الإجراء",
                actions,
                format_func=lambda x: action_names.get(x, x)
            )
            
            if selected_action == 'الكل':
                selected_action = None
        
        # Date range filter
        col_date1, col_date2, col_limit = st.columns(3)
        
        with col_date1:
            start_date = st.date_input(
                "من تاريخ",
                value=datetime.now().date() - timedelta(days=7),
                max_value=datetime.now().date()
            )
        
        with col_date2:
            end_date = st.date_input(
                "إلى تاريخ",
                value=datetime.now().date(),
                max_value=datetime.now().date()
            )
        
        with col_limit:
            limit = st.number_input(
                "عدد السجلات",
                min_value=10,
                max_value=1000,
                value=100,
                step=10
            )
        
        # Apply filters button
        col_apply, col_export, col_clear = st.columns(3)
        
        if col_apply.button("🔍 تطبيق الفلاتر", type="primary", use_container_width=True):
            st.session_state.apply_filters = True
        
        if col_export.button("📥 تصدير Excel", use_container_width=True):
            st.session_state.export_log = True
        
        if col_clear.button("🔄 مسح الفلاتر", use_container_width=True):
            st.session_state.apply_filters = False
            st.rerun()
    
    # =========================================================================
    #                    DISPLAY LOG
    # =========================================================================
    
    st.divider()
    
    # Get activity log
    activities = auth.get_activity_log(
        username=selected_user,
        module=selected_module,
        start_date=str(start_date),
        end_date=str(end_date),
        limit=limit
    )
    
    # Filter by action type if selected
    if selected_action:
        activities = [a for a in activities if a['action_type'] == selected_action]
    
    if not activities:
        st.info("لا توجد سجلات تطابق الفلاتر المحددة")
        return
    
    # Statistics
    st.subheader(f"📊 الإحصائيات - وجد {len(activities)} سجل")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    df_activities = pd.DataFrame(activities)
    
    # Count by action type
    action_counts = df_activities['action_type'].value_counts()
    
    col_stat1.metric("إجمالي الإجراءات", len(activities))
    col_stat2.metric("المستخدمون", df_activities['username'].nunique())
    col_stat3.metric("الأقسام", df_activities['module'].nunique())
    col_stat4.metric("اليوم", len(df_activities[df_activities['timestamp'].str.contains(str(datetime.now().date()))]))
    
    # Export functionality
    if st.session_state.get('export_log', False):
        try:
            # Create Excel file
            excel_df = df_activities.copy()
            excel_df['timestamp_arabic'] = pd.to_datetime(excel_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            excel_df['action_arabic'] = excel_df['action_type'].map(action_names)
            excel_df['module_arabic'] = excel_df['module'].map(module_names)
            
            # Select and rename columns
            export_df = excel_df[[
                'timestamp_arabic', 'username', 'action_arabic', 
                'module_arabic', 'description'
            ]]
            export_df.columns = ['التاريخ والوقت', 'المستخدم', 'الإجراء', 'القسم', 'الوصف']
            
            # Convert to Excel
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='سجل النشاطات')
            
            st.download_button(
                label="📥 تحميل ملف Excel",
                data=output.getvalue(),
                file_name=f"activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.session_state.export_log = False
        except ImportError:
            st.error("❌ يرجى تثبيت openpyxl: pip install openpyxl")
            st.session_state.export_log = False
    
    st.divider()
    
    # Display activities
    st.subheader("📜 السجلات")
    
    # Group by date
    df_activities['date'] = pd.to_datetime(df_activities['timestamp']).dt.date
    
    for date in sorted(df_activities['date'].unique(), reverse=True):
        date_activities = df_activities[df_activities['date'] == date]
        
        with st.expander(f"📅 {date} - {len(date_activities)} إجراء", expanded=(date == datetime.now().date())):
            for _, activity in date_activities.iterrows():
                with st.container(border=True):
                    # Parse timestamp
                    timestamp = datetime.fromisoformat(activity['timestamp'])
                    
                    # Create columns
                    col_time, col_user, col_action, col_module = st.columns([2, 2, 2, 2])
                    
                    # Time
                    with col_time:
                        st.markdown(f"**⏰ {timestamp.strftime('%H:%M:%S')}**")
                    
                    # User
                    with col_user:
                        user_info = next((u for u in all_users if u['username'] == activity['username']), None)
                        user_display = user_info['full_name'] if user_info else activity['username']
                        st.markdown(f"👤 **{user_display}**")
                    
                    # Action
                    with col_action:
                        action_display = action_names.get(activity['action_type'], activity['action_type'])
                        
                        # Color code by action type
                        if activity['action_type'] == 'create':
                            st.markdown(f"🟢 {action_display}")
                        elif activity['action_type'] == 'update':
                            st.markdown(f"🟡 {action_display}")
                        elif activity['action_type'] == 'delete':
                            st.markdown(f"🔴 {action_display}")
                        elif activity['action_type'] == 'login':
                            st.markdown(f"🔵 {action_display}")
                        elif activity['action_type'] == 'logout':
                            st.markdown(f"⚪ {action_display}")
                        else:
                            st.markdown(f"⚫ {action_display}")
                    
                    # Module
                    with col_module:
                        module_display = module_names.get(activity['module'], activity['module'])
                        st.markdown(f"📁 {module_display}")
                    
                    # Description
                    st.markdown(f"**الوصف:** {activity['description']}")
                    
                    # Show details if available
                    if activity.get('old_data') or activity.get('new_data'):
                        with st.expander("📝 التفاصيل"):
                            col_old, col_new = st.columns(2)
                            
                            if activity.get('old_data'):
                                with col_old:
                                    st.markdown("**البيانات القديمة:**")
                                    try:
                                        old_data = json.loads(activity['old_data'])
                                        st.json(old_data)
                                    except:
                                        st.text(activity['old_data'])
                            
                            if activity.get('new_data'):
                                with col_new:
                                    st.markdown("**البيانات الجديدة:**")
                                    try:
                                        new_data = json.loads(activity['new_data'])
                                        st.json(new_data)
                                    except:
                                        st.text(activity['new_data'])
    
    # =========================================================================
    #                    SUMMARY CHARTS
    # =========================================================================
    
    st.divider()
    st.subheader("📊 التحليلات")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("**الإجراءات حسب النوع**")
        action_counts_arabic = action_counts.copy()
        action_counts_arabic.index = action_counts_arabic.index.map(action_names)
        st.bar_chart(action_counts_arabic)
    
    with col_chart2:
        st.markdown("**النشاط حسب المستخدم**")
        user_counts = df_activities['username'].value_counts().head(10)
        
        # Map to full names
        user_counts_named = user_counts.copy()
        for username in user_counts_named.index:
            user_info = next((u for u in all_users if u['username'] == username), None)
            if user_info:
                user_counts_named = user_counts_named.rename({username: user_info['full_name']})
        
        st.bar_chart(user_counts_named)
    
    # Timeline chart
    st.markdown("**📈 النشاط بمرور الوقت**")
    df_activities['hour'] = pd.to_datetime(df_activities['timestamp']).dt.hour
    hourly_counts = df_activities.groupby('hour').size()
    st.line_chart(hourly_counts)
