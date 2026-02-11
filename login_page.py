# -*- coding: utf-8 -*-
"""
Login Page - User Authentication
تسجيل الدخول
"""

import streamlit as st
from auth_manager import AuthManager
from datetime import datetime


def show_login_page():
    """Display login page"""
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🦷</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>A1 Dental Lab</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #666;'>نظام إدارة المعامل</h4>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Login form
        with st.container(border=True):
            st.subheader("🔐 تسجيل الدخول")
            
            username = st.text_input(
                "اسم المستخدم",
                placeholder="أدخل اسم المستخدم",
                key="login_username"
            )
            
            password = st.text_input(
                "كلمة المرور",
                type="password",
                placeholder="أدخل كلمة المرور",
                key="login_password"
            )
            
            st.markdown("")  # Spacing
            
            col_login, col_forgot = st.columns([2, 1])
            
            if col_login.button("دخول", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("❌ يرجى إدخال اسم المستخدم وكلمة المرور")
                else:
                    auth = AuthManager()
                    success, error_msg = auth.login(username, password)
                    
                    if success:
                        st.success(f"✅ مرحباً {st.session_state.full_name}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {error_msg}")
            
            if col_forgot.button("نسيت كلمة المرور؟"):
                st.info("يرجى التواصل مع المدير لإعادة تعيين كلمة المرور")
        
        
        
        # Footer
        st.markdown("---")
        st.markdown(
            f"<p style='text-align: center; color: #999; font-size: 12px;'>"
            f"© 2024-2026 A1 Dental Lab - جميع الحقوق محفوظة<br>"
            f"الإصدار 6.1 | {datetime.now().strftime('%Y-%m-%d')}"
            f"</p>",
            unsafe_allow_html=True
        )


def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('logged_in', False)


def get_current_user():
    """Get current logged in user info"""
    if check_authentication():
        return {
            'username': st.session_state.get('username'),
            'full_name': st.session_state.get('full_name'),
            'role': st.session_state.get('role')
        }
    return None


def logout_button():
    """Display logout button in sidebar"""
    if check_authentication():
        st.sidebar.markdown("---")
        
        user_info = get_current_user()
        st.sidebar.markdown(f"**المستخدم:** {user_info['full_name']}")
        st.sidebar.markdown(f"**الصلاحية:** {get_role_display(user_info['role'])}")
        
        if st.sidebar.button("🚪 تسجيل الخروج", use_container_width=True):
            auth = AuthManager()
            auth.logout(st.session_state.username)
            st.rerun()


def get_role_display(role: str) -> str:
    """Get Arabic display name for role"""
    role_names = {
        'admin': 'مدير النظام',
        'manager': 'مدير',
        'accountant': 'محاسب',
        'technician': 'فني'
    }
    return role_names.get(role, role)
