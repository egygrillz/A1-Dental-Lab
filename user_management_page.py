# -*- coding: utf-8 -*-
"""
User Management Page - Admin Only
إدارة المستخدمين
"""

import streamlit as st
import pandas as pd
from auth_manager import AuthManager, require_permission
from datetime import datetime


@require_permission('users', 'view')
def show_user_management_page():
    """User management interface - Admin only"""
    
    st.header("👥 إدارة المستخدمين - User Management")
    
    auth = AuthManager()
    current_user = st.session_state.username
    current_role = st.session_state.role
    
    # Only admin can access this page
    if current_role != 'admin':
        st.error("❌ هذه الصفحة متاحة للمدير فقط")
        return
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 قائمة المستخدمين", 
        "➕ إضافة مستخدم", 
        "🔐 الصلاحيات",
        "📊 إحصائيات"
    ])
    
    # =========================================================================
    #                    TAB 1: USER LIST
    # =========================================================================
    
    with tab1:
        st.subheader("قائمة المستخدمين")
        
        users = auth.get_all_users()
        
        if not users:
            st.info("لا يوجد مستخدمين")
            return
        
        # Create DataFrame
        df = pd.DataFrame(users)
        
        # Add Arabic role names
        role_map = {
            'admin': 'مدير النظام',
            'manager': 'مدير',
            'accountant': 'محاسب',
            'technician': 'فني'
        }
        df['role_arabic'] = df['role'].map(role_map)
        
        # Add status display
        df['status_display'] = df['is_active'].apply(lambda x: '✅ نشط' if x else '❌ معطل')
        
        # Display users
        for idx, user in df.iterrows():
            with st.container(border=True):
                col_info, col_stats, col_actions = st.columns([2, 2, 1])
                
                with col_info:
                    st.markdown(f"### {user['full_name']}")
                    st.markdown(f"**اسم المستخدم:** `{user['username']}`")
                    st.markdown(f"**الصلاحية:** {user['role_arabic']}")
                    
                    if user['email']:
                        st.markdown(f"📧 {user['email']}")
                    if user['phone']:
                        st.markdown(f"📱 {user['phone']}")
                
                with col_stats:
                    st.metric("الحالة", user['status_display'])
                    st.metric("عدد مرات الدخول", user['login_count'])
                    
                    if user['last_login']:
                        last_login_date = datetime.fromisoformat(user['last_login'])
                        st.caption(f"آخر دخول: {last_login_date.strftime('%Y-%m-%d %H:%M')}")
                
                with col_actions:
                    if user['username'] != 'admin':  # Cannot edit admin
                        st.markdown("#### الإجراءات")
                        
                        if st.button("✏️ تعديل", key=f"edit_{user['username']}"):
                            st.session_state.edit_user = user['username']
                            st.rerun()
                        
                        if user['is_active']:
                            if st.button("🔒 تعطيل", key=f"disable_{user['username']}"):
                                success, msg = auth.update_user(
                                    user['username'], 
                                    is_active=0,
                                    updated_by=current_user
                                )
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        else:
                            if st.button("✅ تفعيل", key=f"enable_{user['username']}"):
                                success, msg = auth.update_user(
                                    user['username'],
                                    is_active=1,
                                    updated_by=current_user
                                )
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                    else:
                        st.info("المدير الرئيسي")
        
        # Edit user dialog
        if 'edit_user' in st.session_state:
            edit_username = st.session_state.edit_user
            user_data = next((u for u in users if u['username'] == edit_username), None)
            
            if user_data:
                st.divider()
                st.subheader(f"تعديل بيانات: {user_data['full_name']}")
                
                with st.form("edit_user_form"):
                    new_full_name = st.text_input("الاسم الكامل", value=user_data['full_name'])
                    new_email = st.text_input("البريد الإلكتروني", value=user_data.get('email') or '')
                    new_phone = st.text_input("رقم الهاتف", value=user_data.get('phone') or '')
                    
                    new_role = st.selectbox(
                        "الصلاحية",
                        options=['admin', 'manager', 'accountant', 'technician'],
                        index=['admin', 'manager', 'accountant', 'technician'].index(user_data['role']),
                        format_func=lambda x: role_map.get(x, x)
                    )
                    
                    change_password = st.checkbox("تغيير كلمة المرور")
                    new_password = None
                    if change_password:
                        new_password = st.text_input("كلمة المرور الجديدة", type="password")
                        confirm_password = st.text_input("تأكيد كلمة المرور", type="password")
                    
                    col_save, col_cancel = st.columns(2)
                    
                    if col_save.form_submit_button("💾 حفظ التعديلات", type="primary", use_container_width=True):
                        # Validate password if changing
                        if change_password:
                            if not new_password:
                                st.error("يرجى إدخال كلمة المرور الجديدة")
                            elif new_password != confirm_password:
                                st.error("كلمة المرور غير متطابقة")
                            else:
                                # Update with password
                                success, msg = auth.update_user(
                                    edit_username,
                                    full_name=new_full_name,
                                    email=new_email,
                                    phone=new_phone,
                                    role=new_role,
                                    password=new_password,
                                    updated_by=current_user
                                )
                                if success:
                                    st.success(msg)
                                    del st.session_state.edit_user
                                    st.rerun()
                                else:
                                    st.error(msg)
                        else:
                            # Update without password
                            success, msg = auth.update_user(
                                edit_username,
                                full_name=new_full_name,
                                email=new_email,
                                phone=new_phone,
                                role=new_role,
                                updated_by=current_user
                            )
                            if success:
                                st.success(msg)
                                del st.session_state.edit_user
                                st.rerun()
                            else:
                                st.error(msg)
                    
                    if col_cancel.form_submit_button("❌ إلغاء", use_container_width=True):
                        del st.session_state.edit_user
                        st.rerun()
    
    # =========================================================================
    #                    TAB 2: ADD USER
    # =========================================================================
    
    with tab2:
        st.subheader("➕ إضافة مستخدم جديد")
        
        with st.form("add_user_form"):
            col_basic1, col_basic2 = st.columns(2)
            
            with col_basic1:
                new_username = st.text_input(
                    "اسم المستخدم *",
                    placeholder="username",
                    help="سيستخدم لتسجيل الدخول"
                )
                
                new_full_name = st.text_input(
                    "الاسم الكامل *",
                    placeholder="محمد أحمد"
                )
                
                new_email = st.text_input(
                    "البريد الإلكتروني",
                    placeholder="user@example.com"
                )
            
            with col_basic2:
                new_password = st.text_input(
                    "كلمة المرور *",
                    type="password",
                    help="يجب أن تكون قوية"
                )
                
                confirm_password = st.text_input(
                    "تأكيد كلمة المرور *",
                    type="password"
                )
                
                new_phone = st.text_input(
                    "رقم الهاتف",
                    placeholder="01XXXXXXXXX"
                )
            
            new_role = st.selectbox(
                "الصلاحية *",
                options=['technician', 'accountant', 'manager', 'admin'],
                format_func=lambda x: {
                    'admin': 'مدير النظام',
                    'manager': 'مدير',
                    'accountant': 'محاسب',
                    'technician': 'فني'
                }.get(x, x),
                help="حدد صلاحيات المستخدم"
            )
            
            new_notes = st.text_area(
                "ملاحظات",
                placeholder="أي ملاحظات إضافية..."
            )
            
            # Permissions preview
            st.markdown("---")
            st.markdown("**📋 الصلاحيات:**")
            
            permissions_info = {
                'admin': "صلاحيات كاملة على جميع أجزاء النظام",
                'manager': "إدارة الحالات والفواتير والأطباء + عرض التقارير",
                'accountant': "إدارة الفواتير والمدفوعات + عرض الحالات",
                'technician': "تسجيل وتعديل الحالات فقط"
            }
            
            st.info(f"ℹ️ {permissions_info.get(new_role, '')}")
            
            st.markdown("---")
            
            if st.form_submit_button("➕ إضافة المستخدم", type="primary", use_container_width=True):
                # Validation
                errors = []
                
                if not new_username:
                    errors.append("اسم المستخدم مطلوب")
                elif len(new_username) < 3:
                    errors.append("اسم المستخدم يجب أن يكون 3 أحرف على الأقل")
                
                if not new_full_name:
                    errors.append("الاسم الكامل مطلوب")
                
                if not new_password:
                    errors.append("كلمة المرور مطلوبة")
                elif len(new_password) < 6:
                    errors.append("كلمة المرور يجب أن تكون 6 أحرف على الأقل")
                elif new_password != confirm_password:
                    errors.append("كلمة المرور غير متطابقة")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Create user
                    success, msg = auth.create_user(
                        username=new_username.lower().strip(),
                        password=new_password,
                        full_name=new_full_name,
                        role=new_role,
                        email=new_email if new_email else None,
                        phone=new_phone if new_phone else None,
                        created_by=current_user,
                        notes=new_notes if new_notes else None
                    )
                    
                    if success:
                        st.success(f"✅ {msg}")
                        st.balloons()
                    else:
                        st.error(f"❌ {msg}")
    
    # =========================================================================
    #                    TAB 3: PERMISSIONS
    # =========================================================================
    
    with tab3:
        st.subheader("🔐 إدارة الصلاحيات")
        
        st.info("""
        💡 **ملاحظة:** 
        - المدير (admin) لديه صلاحيات كاملة تلقائياً
        - يمكنك تخصيص صلاحيات الأدوار الأخرى
        """)
        
        # Select role to edit
        edit_role = st.selectbox(
            "اختر الدور لتعديل صلاحياته",
            options=['manager', 'accountant', 'technician'],
            format_func=lambda x: {
                'manager': 'مدير',
                'accountant': 'محاسب',
                'technician': 'فني'
            }.get(x, x)
        )
        
        st.divider()
        
        # Get current permissions
        with st.container(border=True):
            modules = {
                'cases': 'الحالات',
                'doctors': 'الأطباء والمراكز',
                'invoices': 'الفواتير',
                'reports': 'التقارير',
                'settings': 'الإعدادات',
                'users': 'المستخدمين'
            }
            
            actions = {
                'view': 'عرض',
                'create': 'إنشاء',
                'edit': 'تعديل',
                'delete': 'حذف',
                'export': 'تصدير'
            }
            
            # Get current permissions from database
            import sqlite3
            with sqlite3.connect(auth.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT module, can_view, can_create, can_edit, can_delete, can_export
                    FROM permissions
                    WHERE role = ?
                """, (edit_role,))
                
                current_perms = {}
                for row in cursor.fetchall():
                    module, view, create, edit, delete, export = row
                    current_perms[module] = {
                        'view': bool(view),
                        'create': bool(create),
                        'edit': bool(edit),
                        'delete': bool(delete),
                        'export': bool(export)
                    }
            
            # Display permission matrix
            st.markdown(f"### صلاحيات {edit_role}")
            
            updated_perms = {}
            
            for module, module_name in modules.items():
                st.markdown(f"**{module_name}**")
                
                cols = st.columns(5)
                perms = current_perms.get(module, {action: False for action in actions})
                module_perms = {}
                
                for idx, (action, action_name) in enumerate(actions.items()):
                    with cols[idx]:
                        checked = st.checkbox(
                            action_name,
                            value=perms.get(action, False),
                            key=f"{edit_role}_{module}_{action}"
                        )
                        module_perms[action] = checked
                
                updated_perms[module] = module_perms
                st.markdown("---")
            
            # Save button
            if st.button("💾 حفظ الصلاحيات", type="primary", use_container_width=True):
                success_count = 0
                for module, perms in updated_perms.items():
                    if auth.update_permissions(edit_role, module, perms):
                        success_count += 1
                
                if success_count == len(updated_perms):
                    st.success("✅ تم حفظ الصلاحيات بنجاح")
                    auth.log_activity(
                        current_user, 'update', 'permissions',
                        f'تحديث صلاحيات الدور: {edit_role}'
                    )
                    st.rerun()
                else:
                    st.error("❌ حدث خطأ في حفظ بعض الصلاحيات")
    
    # =========================================================================
    #                    TAB 4: STATISTICS
    # =========================================================================
    
    with tab4:
        st.subheader("📊 إحصائيات المستخدمين")
        
        users = auth.get_all_users()
        df = pd.DataFrame(users)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_users = len(df)
        active_users = len(df[df['is_active'] == 1])
        total_logins = df['login_count'].sum()
        
        col1.metric("إجمالي المستخدمين", total_users)
        col2.metric("المستخدمون النشطون", active_users)
        col3.metric("المستخدمون المعطلون", total_users - active_users)
        col4.metric("إجمالي مرات الدخول", total_logins)
        
        st.divider()
        
        # User roles distribution
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("**📊 توزيع الأدوار**")
            role_counts = df['role'].value_counts()
            role_map = {
                'admin': 'مدير النظام',
                'manager': 'مدير',
                'accountant': 'محاسب',
                'technician': 'فني'
            }
            role_counts.index = role_counts.index.map(role_map)
            st.bar_chart(role_counts)
        
        with col_chart2:
            st.markdown("**📈 نشاط المستخدمين**")
            active_df = df[df['login_count'] > 0].sort_values('login_count', ascending=False).head(5)
            if not active_df.empty:
                st.bar_chart(active_df.set_index('full_name')['login_count'])
            else:
                st.info("لا يوجد نشاط بعد")
        
        st.divider()
        
        # Recent users
        st.markdown("**👤 المستخدمون الجدد**")
        recent_users = df.sort_values('created_at', ascending=False).head(5)
        
        for _, user in recent_users.iterrows():
            created_date = datetime.fromisoformat(user['created_at'])
            st.markdown(
                f"• **{user['full_name']}** ({role_map.get(user['role'], user['role'])}) - "
                f"{created_date.strftime('%Y-%m-%d')}"
            )
