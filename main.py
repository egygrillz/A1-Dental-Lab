# -*- coding: utf-8 -*-
"""
A1 Dental Lab Management System
Main Application Entry Point
"""

import streamlit as st
import os
from database import DatabaseManager
from entry_page import show_entry_page
from checkout_page import show_checkout_page
from doctors_page import show_doctors_page
from invoice_page import show_invoice_page
from archive_page import show_archive_page
from dashboard_page import show_dashboard_page

# Page configuration
st.set_page_config(
    page_title="A1 Dental Lab",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = DatabaseManager()

# Sidebar
st.sidebar.title("🦷 A1 Dental Lab")

# Display logo if exists
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=120)

st.sidebar.markdown("---")

# Navigation menu
menu = [
    "📊 لوحة المعلومات",
    "📥 تسجيل حالة",
    "📤 تسليم حالات",
    "🧾 الفواتير",
    "🗄️ الأرشيف",
    "👨‍⚕️ الإعدادات"
]

choice = st.sidebar.radio("القائمة الرئيسية:", menu)

st.sidebar.markdown("---")

# Database stats in sidebar
stats = db.get_database_stats()
st.sidebar.metric("📦 إجمالي الحالات", stats['total_cases'])
st.sidebar.metric("🔵 في المعمل", stats['in_lab'])
st.sidebar.metric("⚠️ غير مدفوعة", stats['unpaid'])

st.sidebar.markdown("---")

# Backup button
if st.sidebar.button("💾 نسخة احتياطية", use_container_width=True):
    backup_path = db.backup_database()
    if backup_path:
        st.sidebar.success(f"✅ تم إنشاء النسخة الاحتياطية")
    else:
        st.sidebar.error("❌ فشل إنشاء النسخة الاحتياطية")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("A1 Dental Lab © 2024-2026")
st.sidebar.caption("نظام إدارة المعامل")

# Main content area - route to appropriate page
if choice == "📊 لوحة المعلومات":
    show_dashboard_page(db)
elif choice == "📥 تسجيل حالة":
    show_entry_page(db)
elif choice == "📤 تسليم حالات":
    show_checkout_page(db)
elif choice == "🧾 الفواتير":
    show_invoice_page(db)
elif choice == "🗄️ الأرشيف":
    show_archive_page(db)
elif choice == "👨‍⚕️ الإعدادات":
    show_doctors_page(db)
