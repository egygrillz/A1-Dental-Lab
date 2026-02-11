# -*- coding: utf-8 -*-
"""
Authentication and User Management System
Features:
- User login/logout
- Role-based access control
- Password hashing
- Session management
- Admin user management
"""

import streamlit as st
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import json


class AuthManager:
    """Manage user authentication and authorization"""
    
    def __init__(self, db_name="lab_database.db"):
        self.db_name = db_name
        self._init_auth_tables()
        self._create_default_admin()
    
    def _init_auth_tables(self):
        """Initialize authentication tables"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    role TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT (datetime('now')),
                    created_by TEXT,
                    last_login TEXT,
                    login_count INTEGER DEFAULT 0,
                    notes TEXT
                )
            """)
            
            # Permissions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    module TEXT NOT NULL,
                    can_view INTEGER DEFAULT 0,
                    can_create INTEGER DEFAULT 0,
                    can_edit INTEGER DEFAULT 0,
                    can_delete INTEGER DEFAULT 0,
                    can_export INTEGER DEFAULT 0,
                    UNIQUE(role, module)
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    login_time TEXT DEFAULT (datetime('now')),
                    logout_time TEXT,
                    ip_address TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Activity log table (detailed)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    module TEXT NOT NULL,
                    description TEXT,
                    record_id INTEGER,
                    old_data TEXT,
                    new_data TEXT,
                    ip_address TEXT,
                    timestamp TEXT DEFAULT (datetime('now'))
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(username)")
            
            conn.commit()
    
    def _create_default_admin(self):
        """Create default admin user if not exists"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Check if admin exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                # Create admin with default password 'admin123'
                password_hash = self._hash_password('admin123')
                cursor.execute("""
                    INSERT INTO users (username, password_hash, full_name, role, is_active)
                    VALUES ('admin', ?, 'مدير النظام', 'admin', 1)
                """, (password_hash,))
                
                # Create default permissions for admin (full access)
                modules = ['cases', 'doctors', 'invoices', 'reports', 'settings', 'users']
                for module in modules:
                    cursor.execute("""
                        INSERT OR IGNORE INTO permissions 
                        (role, module, can_view, can_create, can_edit, can_delete, can_export)
                        VALUES ('admin', ?, 1, 1, 1, 1, 1)
                    """, (module,))
                
                # Create default permissions for other roles
                self._create_default_roles(cursor)
                
                conn.commit()
    
    def _create_default_roles(self, cursor):
        """Create default role permissions"""
        # Technician role (can view and create cases)
        tech_perms = {
            'cases': (1, 1, 1, 0, 0),  # view, create, edit, delete, export
            'doctors': (1, 0, 0, 0, 0),
            'invoices': (1, 0, 0, 0, 0),
            'reports': (1, 0, 0, 0, 0),
            'settings': (0, 0, 0, 0, 0),
            'users': (0, 0, 0, 0, 0)
        }
        
        for module, (v, c, e, d, ex) in tech_perms.items():
            cursor.execute("""
                INSERT OR IGNORE INTO permissions 
                (role, module, can_view, can_create, can_edit, can_delete, can_export)
                VALUES ('technician', ?, ?, ?, ?, ?, ?)
            """, (module, v, c, e, d, ex))
        
        # Accountant role (can manage invoices and view cases)
        acc_perms = {
            'cases': (1, 0, 0, 0, 1),
            'doctors': (1, 0, 0, 0, 0),
            'invoices': (1, 1, 1, 0, 1),
            'reports': (1, 0, 0, 0, 1),
            'settings': (0, 0, 0, 0, 0),
            'users': (0, 0, 0, 0, 0)
        }
        
        for module, (v, c, e, d, ex) in acc_perms.items():
            cursor.execute("""
                INSERT OR IGNORE INTO permissions 
                (role, module, can_view, can_create, can_edit, can_delete, can_export)
                VALUES ('accountant', ?, ?, ?, ?, ?, ?)
            """, (module, v, c, e, d, ex))
        
        # Manager role (full access except user management)
        mgr_perms = {
            'cases': (1, 1, 1, 1, 1),
            'doctors': (1, 1, 1, 1, 1),
            'invoices': (1, 1, 1, 1, 1),
            'reports': (1, 1, 1, 1, 1),
            'settings': (1, 1, 1, 0, 1),
            'users': (1, 0, 0, 0, 0)
        }
        
        for module, (v, c, e, d, ex) in mgr_perms.items():
            cursor.execute("""
                INSERT OR IGNORE INTO permissions 
                (role, module, can_view, can_create, can_edit, can_delete, can_export)
                VALUES ('manager', ?, ?, ?, ?, ?, ?)
            """, (module, v, c, e, d, ex))
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """Authenticate user and create session"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            
            cursor.execute("""
                SELECT id, full_name, role, is_active 
                FROM users 
                WHERE username = ? AND password_hash = ?
            """, (username, password_hash))
            
            result = cursor.fetchone()
            
            if result:
                user_id, full_name, role, is_active = result
                
                if not is_active:
                    return False, "الحساب غير مفعل"
                
                # Create session token
                session_token = secrets.token_hex(32)
                
                # Save session
                cursor.execute("""
                    INSERT INTO user_sessions (username, session_token, is_active)
                    VALUES (?, ?, 1)
                """, (username, session_token))
                
                # Update last login
                cursor.execute("""
                    UPDATE users 
                    SET last_login = datetime('now'),
                        login_count = login_count + 1
                    WHERE username = ?
                """, (username,))
                
                # Log activity
                self.log_activity(username, 'login', 'system', 'تسجيل دخول ناجح')
                
                conn.commit()
                
                # Store in session state
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.full_name = full_name
                st.session_state.role = role
                st.session_state.session_token = session_token
                
                return True, None
            else:
                return False, "اسم المستخدم أو كلمة المرور غير صحيحة"
    
    def logout(self, username: str):
        """Logout user and end session"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # End session
            cursor.execute("""
                UPDATE user_sessions 
                SET logout_time = datetime('now'),
                    is_active = 0
                WHERE username = ? AND is_active = 1
            """, (username,))
            
            # Log activity
            self.log_activity(username, 'logout', 'system', 'تسجيل خروج')
            
            conn.commit()
        
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    def check_permission(self, username: str, module: str, action: str) -> bool:
        """Check if user has permission for action on module"""
        if not username:
            return False
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Get user role
            cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            role = result[0]
            
            # Admin has all permissions
            if role == 'admin':
                return True
            
            # Check specific permission
            action_map = {
                'view': 'can_view',
                'create': 'can_create',
                'edit': 'can_edit',
                'delete': 'can_delete',
                'export': 'can_export'
            }
            
            column = action_map.get(action, 'can_view')
            
            cursor.execute(f"""
                SELECT {column} 
                FROM permissions 
                WHERE role = ? AND module = ?
            """, (role, module))
            
            result = cursor.fetchone()
            return bool(result and result[0]) if result else False
    
    def get_user_permissions(self, username: str) -> Dict[str, Dict[str, bool]]:
        """Get all permissions for user"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if not result:
                return {}
            
            role = result[0]
            
            if role == 'admin':
                # Admin has all permissions
                modules = ['cases', 'doctors', 'invoices', 'reports', 'settings', 'users']
                return {
                    module: {
                        'view': True, 'create': True, 'edit': True, 
                        'delete': True, 'export': True
                    }
                    for module in modules
                }
            
            cursor.execute("""
                SELECT module, can_view, can_create, can_edit, can_delete, can_export
                FROM permissions
                WHERE role = ?
            """, (role,))
            
            permissions = {}
            for row in cursor.fetchall():
                module, view, create, edit, delete, export = row
                permissions[module] = {
                    'view': bool(view),
                    'create': bool(create),
                    'edit': bool(edit),
                    'delete': bool(delete),
                    'export': bool(export)
                }
            
            return permissions
    
    def create_user(self, username: str, password: str, full_name: str, 
                    role: str, email: str = None, phone: str = None,
                    created_by: str = None, notes: str = None) -> Tuple[bool, str]:
        """Create new user"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Check if username exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
                if cursor.fetchone()[0] > 0:
                    return False, "اسم المستخدم موجود بالفعل"
                
                password_hash = self._hash_password(password)
                
                cursor.execute("""
                    INSERT INTO users 
                    (username, password_hash, full_name, email, phone, role, created_by, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (username, password_hash, full_name, email, phone, role, created_by, notes))
                
                # Log activity
                self.log_activity(created_by or 'admin', 'create', 'users', 
                                f'إضافة مستخدم جديد: {full_name} ({username})')
                
                conn.commit()
                return True, "تم إضافة المستخدم بنجاح"
        except Exception as e:
            return False, f"خطأ في إضافة المستخدم: {str(e)}"
    
    def update_user(self, username: str, **kwargs) -> Tuple[bool, str]:
        """Update user information"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Build update query
                updates = []
                values = []
                
                if 'full_name' in kwargs:
                    updates.append("full_name = ?")
                    values.append(kwargs['full_name'])
                
                if 'email' in kwargs:
                    updates.append("email = ?")
                    values.append(kwargs['email'])
                
                if 'phone' in kwargs:
                    updates.append("phone = ?")
                    values.append(kwargs['phone'])
                
                if 'role' in kwargs:
                    updates.append("role = ?")
                    values.append(kwargs['role'])
                
                if 'is_active' in kwargs:
                    updates.append("is_active = ?")
                    values.append(kwargs['is_active'])
                
                if 'password' in kwargs:
                    updates.append("password_hash = ?")
                    values.append(self._hash_password(kwargs['password']))
                
                if not updates:
                    return False, "لا توجد تحديثات"
                
                values.append(username)
                query = f"UPDATE users SET {', '.join(updates)} WHERE username = ?"
                
                cursor.execute(query, values)
                
                # Log activity
                self.log_activity(kwargs.get('updated_by', 'admin'), 'update', 'users',
                                f'تحديث بيانات المستخدم: {username}')
                
                conn.commit()
                return True, "تم تحديث البيانات بنجاح"
        except Exception as e:
            return False, f"خطأ في التحديث: {str(e)}"
    
    def delete_user(self, username: str, deleted_by: str) -> Tuple[bool, str]:
        """Delete user (soft delete by deactivating)"""
        if username == 'admin':
            return False, "لا يمكن حذف المدير الرئيسي"
        
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                cursor.execute("UPDATE users SET is_active = 0 WHERE username = ?", (username,))
                
                # Log activity
                self.log_activity(deleted_by, 'delete', 'users',
                                f'تعطيل المستخدم: {username}')
                
                conn.commit()
                return True, "تم تعطيل المستخدم"
        except Exception as e:
            return False, f"خطأ: {str(e)}"
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT username, full_name, email, phone, role, is_active, 
                       created_at, last_login, login_count
                FROM users
                ORDER BY created_at DESC
            """)
            
            columns = ['username', 'full_name', 'email', 'phone', 'role', 'is_active',
                      'created_at', 'last_login', 'login_count']
            
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def log_activity(self, username: str, action_type: str, module: str, 
                     description: str, record_id: int = None, 
                     old_data: str = None, new_data: str = None):
        """Log user activity"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO activity_log 
                    (username, action_type, module, description, record_id, old_data, new_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (username, action_type, module, description, record_id, old_data, new_data))
                
                conn.commit()
        except:
            pass  # Don't fail if logging fails
    
    def get_activity_log(self, username: str = None, module: str = None, 
                         start_date: str = None, end_date: str = None,
                         limit: int = 100) -> List[Dict]:
        """Get activity log with filters"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM activity_log WHERE 1=1"
            params = []
            
            if username:
                query += " AND username = ?"
                params.append(username)
            
            if module:
                query += " AND module = ?"
                params.append(module)
            
            if start_date:
                query += " AND date(timestamp) >= date(?)"
                params.append(start_date)
            
            if end_date:
                query += " AND date(timestamp) <= date(?)"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            columns = ['id', 'username', 'action_type', 'module', 'description',
                      'record_id', 'old_data', 'new_data', 'ip_address', 'timestamp']
            
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def update_permissions(self, role: str, module: str, permissions: Dict[str, bool]) -> bool:
        """Update role permissions for a module"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO permissions 
                    (role, module, can_view, can_create, can_edit, can_delete, can_export)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(role, module) DO UPDATE SET
                        can_view = excluded.can_view,
                        can_create = excluded.can_create,
                        can_edit = excluded.can_edit,
                        can_delete = excluded.can_delete,
                        can_export = excluded.can_export
                """, (
                    role, module,
                    permissions.get('view', 0),
                    permissions.get('create', 0),
                    permissions.get('edit', 0),
                    permissions.get('delete', 0),
                    permissions.get('export', 0)
                ))
                
                conn.commit()
                return True
        except:
            return False


def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('logged_in', False):
            st.warning("⚠️ يجب تسجيل الدخول أولاً")
            return None
        return func(*args, **kwargs)
    return wrapper


def require_permission(module: str, action: str):
    """Decorator to check permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.get('logged_in', False):
                st.error("❌ يجب تسجيل الدخول")
                return None
            
            auth = AuthManager()
            username = st.session_state.get('username')
            
            if not auth.check_permission(username, module, action):
                st.error(f"❌ ليس لديك صلاحية {action} في {module}")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
