# -*- coding: utf-8 -*-
"""
A1 Dental Lab Management System - Database Manager
Comprehensive database management with full CRUD operations and analytics
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import shutil
import os
import glob
from typing import Optional, Dict, List, Tuple, Any


class DatabaseManager:
    """
    Comprehensive database manager for dental lab operations
    Features:
    - Case management
    - Doctor/Center management
    - Invoice generation
    - Balance tracking
    - Analytics and reporting
    - Automatic backups
    """
    
    def __init__(self, db_name="lab_database.db"):
        self.db_name = db_name
        self.backup_folder = "backups"
        self.init_db()
        
    # =========================================================================
    #                         DATABASE INITIALIZATION
    # =========================================================================
    
    def init_db(self):
        """Initialize all database tables with complete schema"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            self._create_doctors_table(cursor)
            self._create_cases_table(cursor)
            self._create_prices_table(cursor)
            self._create_invoices_table(cursor)
            self._create_invoice_cases_table(cursor)
            self._create_balances_table(cursor)
            self._create_payments_table(cursor)
            self._create_audit_log_table(cursor)
            self._create_material_catalog_table(cursor)
            
            self._create_indexes(cursor)
            self._migrate_existing_columns(cursor)
            
            conn.commit()
    
    def _create_doctors_table(self, cursor):
        """Create doctors_list table for doctors and dental centers"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                doc_code TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                is_center INTEGER DEFAULT 0,
                center_parent TEXT,
                is_active INTEGER DEFAULT 1,
                notes TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (center_parent) REFERENCES doctors_list(name) ON DELETE CASCADE
            )
        """)
    
    def _create_cases_table(self, cursor):
        """Create cases table for lab cases"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_code TEXT UNIQUE NOT NULL,
                patient TEXT NOT NULL,
                doctor TEXT NOT NULL,
                dental_center TEXT,
                branch_name TEXT,
                entry_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'في المعمل',
                color TEXT,
                teeth_map TEXT,
                notes TEXT,
                price REAL,
                count INTEGER,
                expected_delivery TEXT,
                delivery_date TEXT,
                try_in_date TEXT,
                is_try_in INTEGER DEFAULT 0,
                is_paid INTEGER DEFAULT 0,
                attachment TEXT,
                priority TEXT DEFAULT 'normal',
                lab_technician TEXT,
                discount REAL DEFAULT 0,
                tax REAL DEFAULT 0,
                final_price REAL,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
    
    def _create_prices_table(self, cursor):
        """Create doctors_prices table for material pricing per doctor/center"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_name TEXT NOT NULL,
                material TEXT NOT NULL,
                price REAL NOT NULL,
                cost_price REAL DEFAULT 0,
                notes TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                UNIQUE(doc_name, material)
            )
        """)
    
    def _create_invoices_table(self, cursor):
        """Create invoices table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                doctor_name TEXT NOT NULL,
                dental_center TEXT,
                branch_name TEXT,
                total_amount REAL NOT NULL,
                discount REAL DEFAULT 0,
                tax REAL DEFAULT 0,
                final_amount REAL,
                issue_date TEXT NOT NULL,
                issue_time TEXT NOT NULL,
                created_by TEXT,
                notes TEXT,
                is_cancelled INTEGER DEFAULT 0,
                cancelled_at TEXT,
                cancelled_by TEXT,
                cancellation_reason TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
    
    def _create_invoice_cases_table(self, cursor):
        """Create invoice_cases linking table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_cases (
                invoice_id INTEGER NOT NULL,
                case_id INTEGER NOT NULL,
                PRIMARY KEY (invoice_id, case_id),
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
                FOREIGN KEY (case_id) REFERENCES cases(id)
            )
        """)
    
    def _create_balances_table(self, cursor):
        """Create balances table for tracking account balances"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                branch_name TEXT,
                previous_balance REAL DEFAULT 0,
                previous_balance_date TEXT,
                outstanding_balance REAL DEFAULT 0,
                total_paid REAL DEFAULT 0,
                total_invoiced REAL DEFAULT 0,
                notes TEXT,
                last_updated TEXT DEFAULT (datetime('now')),
                UNIQUE(entity_name, branch_name)
            )
        """)
    
    def _create_payments_table(self, cursor):
        """Create payments table for tracking payments"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT NOT NULL,
                branch_name TEXT,
                amount REAL NOT NULL,
                payment_method TEXT,
                reference_number TEXT,
                payment_date TEXT NOT NULL,
                notes TEXT,
                created_by TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
    
    def _create_audit_log_table(self, cursor):
        """Create audit log table for tracking changes"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                action TEXT NOT NULL,
                old_values TEXT,
                new_values TEXT,
                user TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)
    
    def _create_material_catalog_table(self, cursor):
        """Create material catalog table for standard materials"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS material_catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_name TEXT UNIQUE NOT NULL,
                category TEXT,
                default_price REAL DEFAULT 0,
                default_cost REAL DEFAULT 0,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        
        # Insert default materials if empty
        cursor.execute("SELECT COUNT(*) FROM material_catalog")
        if cursor.fetchone()[0] == 0:
            default_materials = [
                ('Zircon', 'Crown', 1200, 600),
                ('E-max', 'Crown', 1000, 500),
                ('Porcelain', 'Crown', 800, 400),
                ('Metal-Ceramic', 'Crown', 700, 350),
                ('PMMA', 'Temporary', 150, 50),
                ('Nightguard', 'Appliance', 500, 200),
                ('Zircon Bridge', 'Bridge', 1200, 600),
                ('Maryland Bridge', 'Bridge', 900, 450),
            ]
            cursor.executemany("""
                INSERT INTO material_catalog (material_name, category, default_price, default_cost)
                VALUES (?, ?, ?, ?)
            """, default_materials)
    
    def _create_indexes(self, cursor):
        """Create indexes for better query performance"""
        indexes = [
            # Cases table indexes
            "CREATE INDEX IF NOT EXISTS idx_cases_doctor ON cases(doctor)",
            "CREATE INDEX IF NOT EXISTS idx_cases_dental_center ON cases(dental_center)",
            "CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status)",
            "CREATE INDEX IF NOT EXISTS idx_cases_entry_date ON cases(entry_date)",
            "CREATE INDEX IF NOT EXISTS idx_cases_expected_delivery ON cases(expected_delivery)",
            "CREATE INDEX IF NOT EXISTS idx_cases_is_paid ON cases(is_paid)",
            "CREATE INDEX IF NOT EXISTS idx_cases_patient ON cases(patient)",
            
            # Invoices table indexes
            "CREATE INDEX IF NOT EXISTS idx_invoices_doctor ON invoices(doctor_name)",
            "CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(issue_date)",
            "CREATE INDEX IF NOT EXISTS idx_invoices_cancelled ON invoices(is_cancelled)",
            
            # Composite indexes
            "CREATE INDEX IF NOT EXISTS idx_cases_doctor_paid ON cases(doctor, is_paid)",
            "CREATE INDEX IF NOT EXISTS idx_cases_center_branch ON cases(dental_center, branch_name)",
            "CREATE INDEX IF NOT EXISTS idx_cases_status_delivery ON cases(status, expected_delivery)",
        ]
        
        for idx_sql in indexes:
            cursor.execute(idx_sql)
    
    def _migrate_existing_columns(self, cursor):
        """Add missing columns to existing tables safely"""
        # Cases table columns
        case_columns = {
            "color": "TEXT",
            "teeth_map": "TEXT",
            "notes": "TEXT",
            "price": "REAL",
            "count": "INTEGER",
            "expected_delivery": "TEXT",
            "delivery_date": "TEXT",
            "try_in_date": "TEXT",
            "is_try_in": "INTEGER DEFAULT 0",
            "is_paid": "INTEGER DEFAULT 0",
            "attachment": "TEXT",
            "status": "TEXT DEFAULT 'في المعمل'",
            "created_at": "TEXT DEFAULT (datetime('now'))",
            "updated_at": "TEXT DEFAULT (datetime('now'))",
            "dental_center": "TEXT",
            "branch_name": "TEXT",
            "priority": "TEXT DEFAULT 'normal'",
            "lab_technician": "TEXT",
            "discount": "REAL DEFAULT 0",
            "tax": "REAL DEFAULT 0",
            "final_price": "REAL"
        }
        
        for col_name, col_type in case_columns.items():
            try:
                cursor.execute(f"ALTER TABLE cases ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass
        
        # Doctors table columns
        doctor_columns = {
            "is_center": "INTEGER DEFAULT 0",
            "center_parent": "TEXT",
            "phone": "TEXT",
            "email": "TEXT",
            "address": "TEXT",
            "is_active": "INTEGER DEFAULT 1",
            "notes": "TEXT",
            "created_at": "TEXT DEFAULT (datetime('now'))",
            "updated_at": "TEXT DEFAULT (datetime('now'))"
        }
        
        for col_name, col_type in doctor_columns.items():
            try:
                cursor.execute(f"ALTER TABLE doctors_list ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass
        
        # Invoices table columns
        invoice_columns = {
            "dental_center": "TEXT",
            "branch_name": "TEXT",
            "discount": "REAL DEFAULT 0",
            "tax": "REAL DEFAULT 0",
            "final_amount": "REAL",
            "is_cancelled": "INTEGER DEFAULT 0",
            "cancelled_at": "TEXT",
            "cancelled_by": "TEXT",
            "cancellation_reason": "TEXT"
        }
        
        for col_name, col_type in invoice_columns.items():
            try:
                cursor.execute(f"ALTER TABLE invoices ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass
        
        # Prices table columns
        price_columns = {
            "cost_price": "REAL DEFAULT 0",
            "notes": "TEXT",
            "is_active": "INTEGER DEFAULT 1",
            "created_at": "TEXT DEFAULT (datetime('now'))",
            "updated_at": "TEXT DEFAULT (datetime('now'))"
        }
        
        for col_name, col_type in price_columns.items():
            try:
                cursor.execute(f"ALTER TABLE doctors_prices ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass
    
    # =========================================================================
    #                         BASIC DATABASE OPERATIONS
    # =========================================================================
    
    def run_query(self, query: str, params: Tuple = ()) -> pd.DataFrame:
        """Execute SELECT query and return DataFrame"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            print(f"Query error: {e}")
            return pd.DataFrame()
    
    def run_action(self, query: str, params: Tuple = ()) -> bool:
        """Execute INSERT/UPDATE/DELETE and return success status"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except Exception as e:
            print(f"Action error: {e}")
            return False
    
    # =========================================================================
    #                         BACKUP OPERATIONS
    # =========================================================================
    
    def backup_database(self) -> Optional[str]:
        """Create timestamped backup of database"""
        if not os.path.exists(self.backup_folder):
            os.makedirs(self.backup_folder)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"lab_database_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_folder, backup_name)
        
        try:
            shutil.copy2(self.db_name, backup_path)
            self._cleanup_old_backups()
            return backup_path
        except Exception as e:
            print(f"Backup error: {e}")
            return None
    
    def _cleanup_old_backups(self, max_backups: int = 30):
        """Keep only the most recent backups"""
        backups = sorted(glob.glob(os.path.join(self.backup_folder, "*.db")))
        
        if len(backups) > max_backups:
            for old_backup in backups[:-max_backups]:
                try:
                    os.remove(old_backup)
                except:
                    pass
    
    # =========================================================================
    #                         CASE OPERATIONS
    # =========================================================================
    
    def get_next_case_code(self) -> str:
        """Generate next sequential case code"""
        timestamp = datetime.now().strftime('%y%m%d%H%M')
        return f"A1-{timestamp}"
    
    def add_case(self, case_data: Dict[str, Any]) -> Optional[str]:
        """Add new case to database"""
        case_code = self.get_next_case_code()
        
        query = """
            INSERT INTO cases (
                case_code, patient, doctor, dental_center, branch_name,
                entry_date, expected_delivery, color, teeth_map, notes,
                price, count, is_try_in, try_in_date, priority,
                lab_technician, discount, tax, final_price, attachment, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            case_code,
            case_data.get('patient'),
            case_data.get('doctor'),
            case_data.get('dental_center'),
            case_data.get('branch_name'),
            case_data.get('entry_date'),
            case_data.get('expected_delivery'),
            case_data.get('color'),
            case_data.get('teeth_map'),
            case_data.get('notes'),
            case_data.get('price'),
            case_data.get('count'),
            case_data.get('is_try_in', 0),
            case_data.get('try_in_date'),
            case_data.get('priority', 'normal'),
            case_data.get('lab_technician'),
            case_data.get('discount', 0),
            case_data.get('tax', 0),
            case_data.get('final_price'),
            case_data.get('attachment'),
            case_data.get('status', 'في المعمل')
        )
        
        if self.run_action(query, params):
            return case_code
        return None
    
    def update_case_status(self, case_code: str, new_status: str) -> bool:
        """Update case status"""
        query = """
            UPDATE cases 
            SET status = ?, updated_at = datetime('now')
            WHERE case_code = ?
        """
        return self.run_action(query, (new_status, case_code))
    
    def mark_case_delivered(self, case_id: int) -> bool:
        """Mark case as delivered with delivery date"""
        query = """
            UPDATE cases 
            SET status = 'تم التسليم',
                delivery_date = DATE('now'),
                updated_at = datetime('now')
            WHERE id = ?
        """
        return self.run_action(query, (case_id,))
    
    def get_cases_by_status(self, status: str) -> pd.DataFrame:
        """Get all cases with specific status"""
        query = "SELECT * FROM cases WHERE status = ? ORDER BY entry_date DESC"
        return self.run_query(query, (status,))
    
    def get_cases_due_soon(self, days: int = 7) -> pd.DataFrame:
        """Get cases due for delivery in next N days"""
        query = """
            SELECT * FROM cases
            WHERE status IN ('في المعمل', 'في المعمل - بعد Try-in')
            AND date(expected_delivery) BETWEEN date('now') AND date('now', '+{} days')
            ORDER BY expected_delivery ASC
        """.format(days)
        return self.run_query(query)
    
    def search_cases(self, search_term: str, search_by: str = 'patient') -> pd.DataFrame:
        """Search cases by patient, doctor, or case code"""
        if search_by == 'patient':
            query = "SELECT * FROM cases WHERE patient LIKE ? ORDER BY entry_date DESC"
        elif search_by == 'doctor':
            query = "SELECT * FROM cases WHERE doctor LIKE ? ORDER BY entry_date DESC"
        elif search_by == 'code':
            query = "SELECT * FROM cases WHERE case_code LIKE ? ORDER BY entry_date DESC"
        else:
            query = "SELECT * FROM cases WHERE patient LIKE ? OR doctor LIKE ? OR case_code LIKE ? ORDER BY entry_date DESC"
            return self.run_query(query, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        return self.run_query(query, (f'%{search_term}%',))
    
    # =========================================================================
    #                         DOCTOR/CENTER OPERATIONS
    # =========================================================================
    
    def add_doctor(self, name: str, phone: str = None, email: str = None) -> bool:
        """Add new doctor"""
        doc_code = f"D-{name[:3].upper()}"
        query = """
            INSERT OR IGNORE INTO doctors_list (name, doc_code, phone, email, is_center)
            VALUES (?, ?, ?, ?, 0)
        """
        return self.run_action(query, (name, doc_code, phone, email))
    
    def add_dental_center(self, name: str, phone: str = None, email: str = None) -> bool:
        """Add new dental center"""
        center_code = f"C-{name[:3].upper()}"
        query = """
            INSERT OR IGNORE INTO doctors_list (name, doc_code, phone, email, is_center)
            VALUES (?, ?, ?, ?, 1)
        """
        return self.run_action(query, (name, center_code, phone, email))
    
    def add_branch(self, branch_name: str, center_name: str) -> bool:
        """Add branch to dental center"""
        branch_code = f"B-{branch_name[:3].upper()}"
        query = """
            INSERT OR IGNORE INTO doctors_list (name, doc_code, is_center, center_parent)
            VALUES (?, ?, 0, ?)
        """
        return self.run_action(query, (branch_name, branch_code, center_name))
    
    def get_all_doctors(self) -> pd.DataFrame:
        """Get all active doctors"""
        query = """
            SELECT * FROM doctors_list 
            WHERE is_center = 0 AND center_parent IS NULL AND is_active = 1
            ORDER BY name
        """
        return self.run_query(query)
    
    def get_all_centers(self) -> pd.DataFrame:
        """Get all active dental centers"""
        query = """
            SELECT * FROM doctors_list 
            WHERE is_center = 1 AND is_active = 1
            ORDER BY name
        """
        return self.run_query(query)
    
    def get_branches(self, center_name: str) -> pd.DataFrame:
        """Get all branches for a dental center"""
        query = "SELECT * FROM doctors_list WHERE center_parent = ? ORDER BY name"
        return self.run_query(query, (center_name,))
    
    # =========================================================================
    #                         PRICING OPERATIONS
    # =========================================================================
    
    def add_material_price(self, doc_name: str, material: str, price: float, cost_price: float = 0) -> bool:
        """Add or update material price for doctor/center"""
        query = """
            INSERT INTO doctors_prices (doc_name, material, price, cost_price)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(doc_name, material) DO UPDATE SET 
                price = excluded.price,
                cost_price = excluded.cost_price,
                updated_at = datetime('now')
        """
        return self.run_action(query, (doc_name, material, price, cost_price))
    
    def get_price(self, doctor_name: str, material_name: str) -> float:
        """Get price for specific material and doctor"""
        query = "SELECT price FROM doctors_prices WHERE doc_name = ? AND material = ? AND is_active = 1"
        result = self.run_query(query, (doctor_name, material_name))
        return result['price'].values[0] if not result.empty else 0
    
    def get_all_prices_for_entity(self, entity_name: str) -> pd.DataFrame:
        """Get all material prices for a doctor or center"""
        query = """
            SELECT material, price, cost_price, notes 
            FROM doctors_prices 
            WHERE doc_name = ? AND is_active = 1
            ORDER BY material
        """
        return self.run_query(query, (entity_name,))
    
    # =========================================================================
    #                         BALANCE OPERATIONS
    # =========================================================================
    
    def get_or_create_balance(self, entity_name: str, entity_type: str = 'doctor', branch_name: str = None) -> Optional[Dict]:
        """Get balance record for entity, create if doesn't exist"""
        query = """
            SELECT * FROM balances 
            WHERE entity_name = ? AND COALESCE(branch_name, '') = COALESCE(?, '')
        """
        result = self.run_query(query, (entity_name, branch_name or ''))
        
        if result.empty:
            insert_query = """
                INSERT INTO balances (entity_name, entity_type, branch_name, previous_balance, outstanding_balance)
                VALUES (?, ?, ?, 0, 0)
            """
            self.run_action(insert_query, (entity_name, entity_type, branch_name))
            result = self.run_query(query, (entity_name, branch_name or ''))
        
        return result.iloc[0].to_dict() if not result.empty else None
    
    def update_balance(self, entity_name: str, branch_name: Optional[str], 
                      previous_balance: float, previous_balance_date: str,
                      outstanding_balance: float, notes: str = '') -> bool:
        """Update balance information"""
        query = """
            UPDATE balances 
            SET previous_balance = ?, 
                previous_balance_date = ?,
                outstanding_balance = ?,
                notes = ?,
                last_updated = datetime('now')
            WHERE entity_name = ? AND COALESCE(branch_name, '') = COALESCE(?, '')
        """
        return self.run_action(query, (
            previous_balance, previous_balance_date, outstanding_balance, notes,
            entity_name, branch_name or ''
        ))
    
    def record_payment(self, entity_name: str, amount: float, payment_method: str,
                      branch_name: str = None, reference_number: str = None,
                      notes: str = None, created_by: str = None) -> bool:
        """Record a payment"""
        payment_date = datetime.now().strftime('%Y-%m-%d')
        
        # Insert payment record
        query = """
            INSERT INTO payments (entity_name, branch_name, amount, payment_method, 
                                reference_number, payment_date, notes, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        success = self.run_action(query, (
            entity_name, branch_name, amount, payment_method,
            reference_number, payment_date, notes, created_by
        ))
        
        if success:
            # Update balance
            balance_query = """
                UPDATE balances 
                SET total_paid = total_paid + ?,
                    outstanding_balance = outstanding_balance - ?,
                    last_updated = datetime('now')
                WHERE entity_name = ? AND COALESCE(branch_name, '') = COALESCE(?, '')
            """
            self.run_action(balance_query, (amount, amount, entity_name, branch_name or ''))
        
        return success
    
    # =========================================================================
    #                         INVOICE OPERATIONS
    # =========================================================================
    
    def create_invoice(self, doctor_name: str, case_ids: List[int], total_amount: float,
                      dental_center: str = None, branch_name: str = None,
                      discount: float = 0, tax: float = 0,
                      created_by: str = None, notes: str = None) -> Optional[str]:
        """Create new invoice and link cases"""
        try:
            now = datetime.now()
            issue_date = now.strftime("%Y-%m-%d")
            issue_time = now.strftime("%H:%M:%S")
            
            # Generate invoice number: INV-YYYYMM-XXXX
            year_month = now.strftime("%Y%m")
            last_inv = self.run_query(
                "SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
                (f"INV-{year_month}%",)
            )
            
            seq = 1 if last_inv.empty else int(last_inv.iloc[0]['invoice_number'].split('-')[-1]) + 1
            invoice_number = f"INV-{year_month}-{seq:04d}"
            
            # Calculate final amount
            final_amount = total_amount - discount + tax
            
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Insert invoice
                cursor.execute("""
                    INSERT INTO invoices (
                        invoice_number, doctor_name, dental_center, branch_name,
                        total_amount, discount, tax, final_amount,
                        issue_date, issue_time, created_by, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (invoice_number, doctor_name, dental_center, branch_name,
                     total_amount, discount, tax, final_amount,
                     issue_date, issue_time, created_by, notes))
                
                invoice_id = cursor.lastrowid
                
                # Link cases and mark as paid
                for case_id in case_ids:
                    cursor.execute(
                        "INSERT INTO invoice_cases (invoice_id, case_id) VALUES (?, ?)",
                        (invoice_id, case_id)
                    )
                    cursor.execute(
                        "UPDATE cases SET is_paid = 1, updated_at = datetime('now') WHERE id = ?",
                        (case_id,)
                    )
                
                conn.commit()
            
            # Update outstanding balance
            entity_name = dental_center if dental_center else doctor_name
            balance_query = """
                UPDATE balances 
                SET outstanding_balance = outstanding_balance + ?,
                    total_invoiced = total_invoiced + ?,
                    last_updated = datetime('now')
                WHERE entity_name = ? AND COALESCE(branch_name, '') = COALESCE(?, '')
            """
            self.run_action(balance_query, (final_amount, final_amount, entity_name, branch_name or ''))
            
            return invoice_number
        except Exception as e:
            print(f"Error creating invoice: {e}")
            return None
    
    def get_invoice_details(self, invoice_number: str) -> pd.DataFrame:
        """Get full invoice information with linked cases"""
        query = """
            SELECT
                i.invoice_number, i.doctor_name, i.dental_center, i.branch_name,
                i.total_amount, i.discount, i.tax, i.final_amount,
                i.issue_date, i.issue_time, i.created_by, i.notes,
                c.id AS case_id, c.case_code, c.patient, c.price,
                c.teeth_map, c.notes AS case_notes, c.color, c.entry_date
            FROM invoices i
            LEFT JOIN invoice_cases ic ON i.id = ic.invoice_id
            LEFT JOIN cases c ON ic.case_id = c.id
            WHERE i.invoice_number = ?
            ORDER BY c.id
        """
        return self.run_query(query, (invoice_number,))
    
    def cancel_invoice(self, invoice_number: str, cancelled_by: str, reason: str) -> bool:
        """Cancel an invoice and update related records"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Get invoice details
                cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
                invoice = cursor.fetchone()
                
                if not invoice:
                    return False
                
                # Mark invoice as cancelled
                cursor.execute("""
                    UPDATE invoices 
                    SET is_cancelled = 1,
                        cancelled_at = datetime('now'),
                        cancelled_by = ?,
                        cancellation_reason = ?
                    WHERE invoice_number = ?
                """, (cancelled_by, reason, invoice_number))
                
                # Unmark cases as paid
                cursor.execute("""
                    UPDATE cases 
                    SET is_paid = 0, updated_at = datetime('now')
                    WHERE id IN (
                        SELECT case_id FROM invoice_cases 
                        WHERE invoice_id = (SELECT id FROM invoices WHERE invoice_number = ?)
                    )
                """, (invoice_number,))
                
                # Update balance (subtract the invoice amount)
                entity_name = invoice[3] if invoice[3] else invoice[2]  # dental_center or doctor_name
                branch_name = invoice[4] if invoice[4] else None
                final_amount = invoice[8]  # final_amount
                
                cursor.execute("""
                    UPDATE balances 
                    SET outstanding_balance = outstanding_balance - ?,
                        last_updated = datetime('now')
                    WHERE entity_name = ? AND COALESCE(branch_name, '') = COALESCE(?, '')
                """, (final_amount, entity_name, branch_name or ''))
                
                conn.commit()
            
            return True
        except Exception as e:
            print(f"Error cancelling invoice: {e}")
            return False
    
    # =========================================================================
    #                         STATISTICS & ANALYTICS
    # =========================================================================
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = {}
        
        # Total cases
        total_cases = self.run_query("SELECT COUNT(*) as count FROM cases")
        stats['total_cases'] = total_cases['count'].values[0] if not total_cases.empty else 0
        
        # Cases in lab
        in_lab = self.run_query("SELECT COUNT(*) as count FROM cases WHERE status LIKE '%في المعمل%'")
        stats['in_lab'] = in_lab['count'].values[0] if not in_lab.empty else 0
        
        # Delivered cases
        delivered = self.run_query("SELECT COUNT(*) as count FROM cases WHERE status = 'تم التسليم'")
        stats['delivered'] = delivered['count'].values[0] if not delivered.empty else 0
        
        # Total entities (doctors + centers)
        total_entities = self.run_query("SELECT COUNT(*) as count FROM doctors_list WHERE center_parent IS NULL AND is_active = 1")
        stats['total_entities'] = total_entities['count'].values[0] if not total_entities.empty else 0
        
        # Unpaid cases
        unpaid = self.run_query("SELECT COUNT(*) as count FROM cases WHERE is_paid = 0 AND status = 'تم التسليم'")
        stats['unpaid'] = unpaid['count'].values[0] if not unpaid.empty else 0
        
        # Total unpaid amount
        unpaid_amount = self.run_query("SELECT COALESCE(SUM(price), 0) as total FROM cases WHERE is_paid = 0 AND status = 'تم التسليم'")
        stats['unpaid_amount'] = unpaid_amount['total'].values[0] if not unpaid_amount.empty else 0
        
        # Monthly revenue
        monthly_revenue = self.run_query("""
            SELECT COALESCE(SUM(price), 0) as total 
            FROM cases 
            WHERE status = 'تم التسليم' 
            AND strftime('%Y-%m', delivery_date) = strftime('%Y-%m', 'now')
        """)
        stats['monthly_revenue'] = monthly_revenue['total'].values[0] if not monthly_revenue.empty else 0
        
        # Try-in cases
        tryin_cases = self.run_query("SELECT COUNT(*) as count FROM cases WHERE is_try_in = 1 AND status LIKE '%في المعمل%'")
        stats['tryin_cases'] = tryin_cases['count'].values[0] if not tryin_cases.empty else 0
        
        # Database size
        if os.path.exists(self.db_name):
            stats['db_size_mb'] = round(os.path.getsize(self.db_name) / (1024 * 1024), 2)
        else:
            stats['db_size_mb'] = 0
        
        return stats
    
    def get_doctor_statistics(self, doctor_name: str) -> Dict[str, Any]:
        """Get statistics for specific doctor/center"""
        stats = {}
        
        query = """
            SELECT 
                COUNT(*) as total_cases,
                SUM(CASE WHEN status = 'تم التسليم' THEN 1 ELSE 0 END) as delivered_cases,
                SUM(CASE WHEN status LIKE '%في المعمل%' THEN 1 ELSE 0 END) as active_cases,
                COALESCE(SUM(CASE WHEN status = 'تم التسليم' THEN price ELSE 0 END), 0) as total_revenue,
                COALESCE(SUM(CASE WHEN is_paid = 0 AND status = 'تم التسليم' THEN price ELSE 0 END), 0) as unpaid_amount,
                COALESCE(SUM(CASE WHEN is_paid = 1 THEN price ELSE 0 END), 0) as paid_amount
            FROM cases
            WHERE doctor = ? OR dental_center = ?
        """
        result = self.run_query(query, (doctor_name, doctor_name))
        
        if not result.empty:
            stats.update(result.iloc[0].to_dict())
        
        return stats
    
    def get_monthly_revenue_trend(self, months: int = 12) -> pd.DataFrame:
        """Get monthly revenue for last N months"""
        query = """
            SELECT 
                strftime('%Y-%m', delivery_date) as month,
                COUNT(*) as cases_count,
                SUM(price) as revenue
            FROM cases
            WHERE status = 'تم التسليم'
            AND date(delivery_date) >= date('now', '-{} months')
            GROUP BY month
            ORDER BY month
        """.format(months)
        return self.run_query(query)
    
    def get_material_usage_stats(self) -> pd.DataFrame:
        """Get statistics on material usage across all cases"""
        # This is complex due to JSON storage, would need custom processing
        query = "SELECT teeth_map FROM cases WHERE teeth_map IS NOT NULL"
        cases = self.run_query(query)
        
        import json
        material_counts = {}
        
        for _, row in cases.iterrows():
            try:
                teeth_data = json.loads(row['teeth_map'])
                for tooth_info in teeth_data.values():
                    material = tooth_info.get('material', 'Unknown')
                    material_counts[material] = material_counts.get(material, 0) + 1
            except:
                continue
        
        return pd.DataFrame(list(material_counts.items()), columns=['Material', 'Count'])
    
    # =========================================================================
    #                         AUDIT LOG
    # =========================================================================
    
    def log_action(self, table_name: str, record_id: int, action: str,
                   old_values: str = None, new_values: str = None, user: str = None) -> bool:
        """Log database action for audit trail"""
        query = """
            INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.run_action(query, (table_name, record_id, action, old_values, new_values, user))
    
    def get_audit_log(self, limit: int = 100, table_name: str = None) -> pd.DataFrame:
        """Get recent audit log entries"""
        if table_name:
            query = "SELECT * FROM audit_log WHERE table_name = ? ORDER BY timestamp DESC LIMIT ?"
            return self.run_query(query, (table_name, limit))
        else:
            query = "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?"
            return self.run_query(query, (limit,))
