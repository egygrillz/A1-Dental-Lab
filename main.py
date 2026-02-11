# -*- coding: utf-8 -*-
"""
A1 Dental Lab Management System - Main Application
نظام إدارة معامل الأسنان A1
"""

import streamlit as st
from datetime import datetime

# Import page functions
from login_page import show_login_page, check_authentication, logout_button, get_current_user
from dashboard_page import show_dashboard_page
from entry_page import show_entry_page
from checkout_page import show_checkout_page
from archive_page import show_archive_page
from invoice_page import show_invoice_page
from doctors_page import show_doctors_page
from user_management_page import show_user_management_page
from activity_log_page import show_activity_log_page

# Import core utilities
from database import DatabaseManager
from auth_manager import AuthManager, require_permission
from constants import PAGE_TITLE, PAGE_ICON, LAYOUT

# ────────────────────────────────────────────────
#               Page Configuration
# ────────────────────────────────────────────────

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com',
        'Report a bug': "mailto:support@example.com",
        'About': "A1 Dental Lab Management System v2.0\n© 2024-2026"
    }
)


# ────────────────────────────────────────────────
#               Initialize Session & DB
# ────────────────────────────────────────────────

# Initialize database connection
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# Initialize auth manager
if 'auth' not in st.session_state:
    st.session_state.auth = AuthManager()

db = st.session_state.db
auth = st.session_state.auth


# ────────────────────────────────────────────────
#               Main Application Flow
# ────────────────────────────────────────────────

def main():
    # Show login page if not authenticated
    if not check_authentication():
        show_login_page()
        return

    # User is logged in → show sidebar & content
    user = get_current_user()
    if not user:
        st.error("حدث خطأ في جلب بيانات المستخدم. يرجى تسجيل الدخول مرة أخرى.")
        return

    # Sidebar - User info & navigation
    with st.sidebar:
        st.markdown(f"**مرحباً بك** {user['full_name']}")
        st.caption(f"الصلاحية: {get_role_display(user['role'])}")
        st.markdown("---")

        # Navigation menu
        st.markdown("### القائمة الرئيسية")

        # Common pages (most roles can access)
        if st.button("🏠 لوحة التحكم", use_container_width=True, type="secondary"):
            st.session_state.current_page = "dashboard"

        if st.button("📥 تسجيل حالة جديدة", use_container_width=True, type="secondary"):
            st.session_state.current_page = "entry"

        if st.button("📤 تسليم الحالات", use_container_width=True, type="secondary"):
            st.session_state.current_page = "checkout"

        if st.button("📂 الأرشيف", use_container_width=True, type="secondary"):
            st.session_state.current_page = "archive"

        if st.button("💳 الفواتير والمدفوعات", use_container_width=True, type="secondary"):
            st.session_state.current_page = "invoices"

        # Settings - doctors & prices (manager & admin)
        if user['role'] in ['admin', 'manager']:
            if st.button("⚙️ إعدادات الأطباء والأسعار", use_container_width=True, type="secondary"):
                st.session_state.current_page = "doctors"

        # Admin-only pages
        if user['role'] == 'admin':
            st.markdown("---")
            st.markdown("### إدارة النظام")

            if st.button("👥 إدارة المستخدمين", use_container_width=True, type="secondary"):
                st.session_state.current_page = "users"

            if st.button("📋 سجل النشاط", use_container_width=True, type="secondary"):
                st.session_state.current_page = "activity"

        # Logout
        st.markdown("---")
        logout_button()

    # ────────────────────────────────────────────────
    #               Main Content Area
    # ────────────────────────────────────────────────

    # Default page if none selected
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"

    # Show header with current page title
    page_titles = {
        "dashboard": "لوحة التحكم",
        "entry": "تسجيل حالة جديدة",
        "checkout": "تسليم الحالات",
        "archive": "أرشيف الحالات",
        "invoices": "الفواتير والمدفوعات",
        "doctors": "إعدادات الأطباء والأسعار",
        "users": "إدارة المستخدمين",
        "activity": "سجل النشاط"
    }

    current_title = page_titles.get(st.session_state.current_page, "الصفحة الرئيسية")
    st.header(f"{current_title} • {datetime.now().strftime('%Y-%m-%d')}")

    # Show selected page
    try:
        if st.session_state.current_page == "dashboard":
            show_dashboard_page(db)

        elif st.session_state.current_page == "entry":
            show_entry_page(db)

        elif st.session_state.current_page == "checkout":
            show_checkout_page(db)

        elif st.session_state.current_page == "archive":
            show_archive_page(db)

        elif st.session_state.current_page == "invoices":
            show_invoice_page(db)

        elif st.session_state.current_page == "doctors":
            # Only manager & admin can access
            if user['role'] in ['admin', 'manager']:
                show_doctors_page(db)
            else:
                st.error("ليس لديك صلاحية الوصول إلى هذه الصفحة")

        elif st.session_state.current_page == "users":
            # Admin only
            if user['role'] == 'admin':
                show_user_management_page()
            else:
                st.error("هذه الصفحة متاحة للمدير فقط")

        elif st.session_state.current_page == "activity":
            # Admin only (or you can change to manager too)
            if user['role'] == 'admin':
                show_activity_log_page()
            else:
                st.error("هذه الصفحة متاحة للمدير فقط")

    except Exception as e:
        st.error(f"حدث خطأ أثناء عرض الصفحة: {str(e)}")
        st.exception(e)


# ────────────────────────────────────────────────
#               Helpers
# ────────────────────────────────────────────────

def get_role_display(role: str) -> str:
    """Arabic display name for roles"""
    role_names = {
        'admin': 'مدير النظام',
        'manager': 'مدير',
        'accountant': 'محاسب',
        'technician': 'فني'
    }
    return role_names.get(role, role)


# ────────────────────────────────────────────────
#               Entry Point
# ────────────────────────────────────────────────

if __name__ == "__main__":
    main()