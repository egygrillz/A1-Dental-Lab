# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
from datetime import datetime
import shutil
import os
import glob

class DatabaseManager:
    def __init__(self, db_name="lab_database.db"):
        self.db_name = db_name
        self.backup_folder = "backups"
        self.init_db()

    def init_db(self):
        """Create tables if they don't exist + add missing columns safely"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # -------------------------------------------------
            # Table: doctors_list
            # -------------------------------------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS doctors_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    doc_code TEXT,
                    phone TEXT,
                    email TEXT
                )
            """)

            # -------------------------------------------------
            # Table: cases
            # -------------------------------------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_code TEXT UNIQUE NOT NULL,
                    patient TEXT NOT NULL,
                    doctor TEXT NOT NULL,
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
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                )
            """)

            # -------------------------------------------------
            # Table: doctors_prices
            # -------------------------------------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS doctors_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_name TEXT NOT NULL,
                    material TEXT NOT NULL,
                    price REAL NOT NULL,
                    UNIQUE(doc_name, material)
                )
            """)

            # -------------------------------------------------
            # Table: invoices
            # -------------------------------------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    doctor_name TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    issue_date TEXT NOT NULL,
                    issue_time TEXT NOT NULL,
                    created_by TEXT,
                    notes TEXT,
                    is_cancelled INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)

            # -------------------------------------------------
            # Table: invoice_cases (linking table)
            # -------------------------------------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoice_cases (
                    invoice_id INTEGER NOT NULL,
                    case_id INTEGER NOT NULL,
                    PRIMARY KEY (invoice_id, case_id),
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            """)

            # -------------------------------------------------
            # Add any missing columns to cases table
            # -------------------------------------------------
            column_definitions = {
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
                "updated_at": "TEXT DEFAULT (datetime('now'))"
            }

            for col_name, col_type in column_definitions.items():
                try:
                    cursor.execute(f"ALTER TABLE cases ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    pass  # Column already exists

            # -------------------------------------------------
            # Create indexes for better performance
            # -------------------------------------------------
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_cases_doctor ON cases(doctor)",
                "CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status)",
                "CREATE INDEX IF NOT EXISTS idx_cases_entry_date ON cases(entry_date)",
                "CREATE INDEX IF NOT EXISTS idx_cases_is_paid ON cases(is_paid)",
                "CREATE INDEX IF NOT EXISTS idx_cases_expected_delivery ON cases(expected_delivery)",
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)

            conn.commit()

    def run_query(self, query, params=()):
        """
        Execute a SELECT query and return results as pandas DataFrame
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            print(f"Query error: {e}")
            return pd.DataFrame()

    def run_action(self, query, params=()):
        """
        Execute INSERT / UPDATE / DELETE and commit changes
        Returns True if at least one row was affected
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            print(f"Integrity error: {e}")
            return False
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def get_last_insert_id(self):
        """Return the ID of the last inserted row"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT last_insert_rowid()")
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error getting last insert ID: {e}")
            return None

    # =============================================================================
    #                           BACKUP FUNCTIONALITY
    # =============================================================================

    def backup_database(self):
        """
        Create a timestamped backup of the database
        Returns the path to the backup file
        """
        try:
            # Create backup folder if it doesn't exist
            if not os.path.exists(self.backup_folder):
                os.makedirs(self.backup_folder)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"lab_database_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_folder, backup_filename)
            
            # Copy database file
            shutil.copy2(self.db_name, backup_path)
            
            # Clean up old backups (keep only last 30)
            self._cleanup_old_backups(max_backups=30)
            
            return backup_path
        except Exception as e:
            print(f"Backup error: {e}")
            return None

    def _cleanup_old_backups(self, max_backups=30):
        """Remove old backup files, keeping only the most recent ones"""
        try:
            backup_files = sorted(
                glob.glob(os.path.join(self.backup_folder, "*.db")),
                key=os.path.getmtime,
                reverse=True
            )
            
            # Remove old backups beyond the limit
            for old_backup in backup_files[max_backups:]:
                os.remove(old_backup)
                print(f"Removed old backup: {old_backup}")
        except Exception as e:
            print(f"Cleanup error: {e}")

    def restore_from_backup(self, backup_path):
        """
        Restore database from a backup file
        WARNING: This will overwrite the current database!
        """
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Create a safety backup of current database first
            safety_backup = f"{self.db_name}.before_restore.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.db_name, safety_backup)
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_name)
            
            return True
        except Exception as e:
            print(f"Restore error: {e}")
            return False

    def list_backups(self):
        """List all available backup files"""
        try:
            backup_files = sorted(
                glob.glob(os.path.join(self.backup_folder, "*.db")),
                key=os.path.getmtime,
                reverse=True
            )
            
            backups = []
            for backup_file in backup_files:
                file_size = os.path.getsize(backup_file) / (1024 * 1024)  # MB
                mod_time = datetime.fromtimestamp(os.path.getmtime(backup_file))
                
                backups.append({
                    'path': backup_file,
                    'filename': os.path.basename(backup_file),
                    'size_mb': round(file_size, 2),
                    'date': mod_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return backups
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []

    # =============================================================================
    #                           HELPER METHODS
    # =============================================================================

    def get_material_price(self, doctor_name, material_name):
        """
        Get price for a specific material for a doctor
        Returns the price or 0 if not found
        """
        result = self.run_query(
            "SELECT price FROM doctors_prices WHERE doc_name = ? AND material = ?",
            (doctor_name, material_name)
        )
        return result['price'].values[0] if not result.empty else 0

    def create_invoice(self, doctor_name, case_ids, total_amount, created_by=None, notes=None):
        """
        Create a new invoice and link selected cases to it.
        Returns the new invoice number or None on failure.
        """
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

            if last_inv.empty:
                seq = 1
            else:
                last_num = int(last_inv.iloc[0]['invoice_number'].split('-')[-1])
                seq = last_num + 1

            invoice_number = f"INV-{year_month}-{seq:04d}"

            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Insert main invoice record
                cursor.execute("""
                    INSERT INTO invoices (
                        invoice_number, doctor_name, total_amount,
                        issue_date, issue_time, created_by, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (invoice_number, doctor_name, total_amount, issue_date, issue_time, created_by, notes))

                invoice_id = cursor.lastrowid

                # Link each selected case to the invoice
                for case_id in case_ids:
                    cursor.execute(
                        "INSERT INTO invoice_cases (invoice_id, case_id) VALUES (?, ?)",
                        (invoice_id, case_id)
                    )
                    # Mark case as paid
                    cursor.execute(
                        "UPDATE cases SET is_paid = 1 WHERE id = ?",
                        (case_id,)
                    )

                conn.commit()

            return invoice_number
        except Exception as e:
            print(f"Error creating invoice: {e}")
            return None

    def get_invoice_details(self, invoice_number):
        """Get full invoice information including linked cases"""
        query = """
            SELECT
                i.invoice_number, i.doctor_name, i.total_amount,
                i.issue_date, i.issue_time, i.created_by, i.notes,
                c.id AS case_id, c.case_code, c.patient, c.price,
                c.teeth_map, c.notes AS case_notes
            FROM invoices i
            LEFT JOIN invoice_cases ic ON i.id = ic.invoice_id
            LEFT JOIN cases c ON ic.case_id = c.id
            WHERE i.invoice_number = ?
            ORDER BY c.id
        """
        return self.run_query(query, (invoice_number,))

    def get_invoices_for_doctor(self, doctor_name):
        """Get list of invoices for a specific doctor"""
        query = """
            SELECT
                invoice_number, issue_date, issue_time,
                total_amount, created_by, notes, is_cancelled
            FROM invoices
            WHERE doctor_name = ?
            ORDER BY issue_date DESC, issue_time DESC
        """
        return self.run_query(query, (doctor_name,))

    def get_database_stats(self):
        """Get general statistics about the database"""
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
        
        # Total doctors
        total_doctors = self.run_query("SELECT COUNT(*) as count FROM doctors_list")
        stats['total_doctors'] = total_doctors['count'].values[0] if not total_doctors.empty else 0
        
        # Unpaid cases
        unpaid = self.run_query("SELECT COUNT(*) as count FROM cases WHERE is_paid = 0 AND status = 'تم التسليم'")
        stats['unpaid'] = unpaid['count'].values[0] if not unpaid.empty else 0
        
        # Database file size
        if os.path.exists(self.db_name):
            stats['db_size_mb'] = round(os.path.getsize(self.db_name) / (1024 * 1024), 2)
        else:
            stats['db_size_mb'] = 0
        
        return stats
