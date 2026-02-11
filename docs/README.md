# A1 Dental Lab Management System 🦷

A comprehensive dental laboratory management system built with Python and Streamlit. Manage cases, invoices, inventory, and analytics with ease.

## Features ✨

### Core Features
- **Case Management** - Register, track, and deliver dental cases
- **Interactive Dental Chart** - Visual tooth selection with FDI notation
- **Nightguard Mode** - Quick full-arch selection for appliances
- **Try-in Scheduling** - Manage provisional fittings before final delivery
- **Invoice Generation** - PDF invoices with Arabic support
- **Balance Tracking** - Monitor outstanding payments per doctor/center
- **Multi-entity Support** - Manage both individual doctors and dental centers with branches
- **Material Pricing** - Custom pricing per doctor/center
- **Analytics Dashboard** - Revenue trends, case statistics, and insights

### Advanced Features
- **Automatic Backups** - Daily database backups with retention policy
- **File Attachments** - Upload images, PDFs, STL files per case
- **Search & Filter** - Find cases by patient, doctor, code, or date
- **Audit Log** - Track all database changes
- **Priority Management** - Mark urgent cases
- **Payment Tracking** - Record and monitor payments
- **Material Catalog** - Standardized material library

## System Requirements 📋

- Python 3.8 or higher
- Windows / Mac / Linux
- 100MB free disk space
- Internet connection (for initial setup only)

## Installation 🚀

### Step 1: Install Python
Download and install Python from [python.org](https://www.python.org/downloads/)

**Windows:** Check "Add Python to PATH" during installation

### Step 2: Download the Project
```bash
# Clone or download the project
cd A1-Dental-Lab
```

### Step 3: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the Application
```bash
streamlit run main.py
```

The application will open in your default browser at `http://localhost:8501`

## First-Time Setup 🎯

### 1. Add Doctors/Centers
1. Go to **⚙️ الإعدادات** (Settings)
2. Add individual doctors or dental centers
3. For centers, add branches if needed

### 2. Set Material Prices
1. In Settings, select a doctor/center
2. Add materials with prices (e.g., Zircon: 1200 EGP)
3. Set cost prices for profit tracking (optional)

### 3. Register First Case
1. Go to **📥 تسجيل حالة** (New Case)
2. Select doctor/center
3. Enter patient name
4. Click teeth on dental chart
5. Select materials and confirm
6. Add details and save

## Usage Guide 📖

### Dashboard (لوحة المعلومات)
- View key metrics: cases in lab, deliveries, revenue
- See upcoming deliveries
- Track unpaid cases
- Analyze trends

### Register Case (تسجيل حالة)
1. **Select Entity**: Choose doctor or dental center/branch
2. **Enter Patient Name**: Required field
3. **Select Teeth**:
   - Click teeth on the dental chart
   - Consecutive teeth are grouped as bridges
   - Single teeth are crowns
4. **Choose Material**: Select from available materials
5. **Set Dates**:
   - Entry date (today by default)
   - Expected delivery date
   - Try-in date (if applicable)
6. **Add Details**:
   - Shade/color
   - Lab technician
   - Priority level
   - Notes
   - File attachments
7. **Save**: Click "حفظ وتسجيل الحالة"

### Nightguard Mode
1. Enable "تسجيل Nightguard" checkbox
2. Click "الفك العلوي" (Upper) or "الفك السفلي" (Lower)
3. Entire arch is selected automatically
4. Continue with case details

### Delivery (تسليم حالات)
1. View cases currently in lab
2. Search by patient name or code
3. **Try-in Cases**:
   - Click "تم تسليم الـ Try-in" when Try-in is delivered
   - Status changes to "في المعمل - بعد Try-in"
4. **Final Delivery**:
   - Click "تم التسليم النهائي"
   - Case is removed from lab and marked as delivered

### Invoices (الفواتير)
1. Select doctor or dental center
2. View unpaid cases
3. **Manage Balances**:
   - Enter previous balance and date
   - System tracks outstanding balance automatically
4. **Select Cases**: Check cases to include in invoice
5. **Generate PDF**: Create printable invoice with balances
6. **Confirm Payment**: Mark cases as paid

Invoice PDF includes:
- Entity details
- Case details (patient, code, materials, teeth)
- Previous balance
- Outstanding balance
- Current invoice subtotal
- Grand total due

### Archive (الأرشيف)
- View all cases (delivered and in-lab)
- Search by patient or doctor
- View complete case details
- Update attachments
- Generate detailed PDF reports
- Delete cases

### Settings (الإعدادات)
**Doctors Management:**
- Add/remove individual doctors
- Update contact information

**Dental Centers:**
- Add/remove centers
- Manage branches per center
- Each branch can have separate pricing

**Price Lists:**
- Set material prices per entity
- Track cost prices for profit analysis
- Add notes per material
- Activate/deactivate materials

## File Structure 📁

```
A1-Dental-Lab/
├── main.py                 # Application entry point
├── database.py             # Database manager
├── entry_page.py           # Case registration
├── checkout_page.py        # Case delivery
├── invoice_page.py         # Invoice generation
├── archive_page.py         # Case archive
├── dashboard_page.py       # Analytics dashboard
├── doctors_page.py         # Settings/management
├── constants.py            # System constants
├── requirements.txt        # Python dependencies
├── lab_database.db         # SQLite database
├── uploads/                # Case attachments
├── backups/                # Database backups
├── fonts/                  # Arabic fonts
└── dejavu-fonts-ttf-2.37/  # Font files
```

## Database Schema 🗄️

### Main Tables
- **cases** - All dental cases
- **doctors_list** - Doctors and dental centers
- **doctors_prices** - Material pricing per entity
- **invoices** - Generated invoices
- **invoice_cases** - Links cases to invoices
- **balances** - Account balances
- **payments** - Payment records
- **audit_log** - Change tracking
- **material_catalog** - Standard materials

## Backup & Recovery 💾

### Automatic Backups
- Backups created via sidebar button
- Stored in `backups/` folder
- Named with timestamp: `lab_database_backup_YYYYMMDD_HHMMSS.db`
- Last 30 backups retained automatically

### Manual Backup
1. Click "💾 نسخة احتياطية" in sidebar
2. Backup file created in `backups/` folder
3. Copy file to external drive/cloud for safety

### Restore from Backup
1. Stop the application
2. Rename current `lab_database.db` to `lab_database_old.db`
3. Copy backup file and rename to `lab_database.db`
4. Restart application

## Customization 🎨

### Modify Materials
Edit default materials in `database.py` → `_create_material_catalog_table()`

### Change Dates Format
Edit `constants.py` → `DATE_FORMAT_DISPLAY`

### Adjust Backup Retention
Edit `database.py` → `_cleanup_old_backups(max_backups=30)`

### Custom Status Values
Edit `constants.py` → `STATUS_IN_LAB`, `STATUS_DELIVERED`, etc.

## Troubleshooting 🔧

### Application Won't Start
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

### Database Errors
```bash
# Restore from backup
cp backups/lab_database_backup_LATEST.db lab_database.db

# Or create fresh database (WARNING: deletes all data)
rm lab_database.db
# Restart application - database will be recreated
```

### PDF Generation Fails
- Ensure fonts folder exists with DejaVu fonts
- Check `dejavu-fonts-ttf-2.37/ttf/` contains:
  - DejaVuSans.ttf
  - DejaVuSans-Bold.ttf

### Arabic Text Not Displaying
1. Verify font files are present
2. Install arabic-reshaper: `pip install arabic-reshaper python-bidi`
3. Restart application

### File Upload Issues
- Check `uploads/` folder exists and is writable
- Verify file size < 10MB
- Supported formats: JPG, PNG, PDF, STL, ZIP, RAR

## Security Considerations 🔒

### Data Protection
- Database file contains sensitive patient information
- Store backups securely (encrypted external drive)
- Limit access to application computer
- Use strong Windows/Mac password

### Regular Backups
- Create backups before major updates
- Store backups in 3 locations (3-2-1 rule):
  - 3 copies total
  - 2 different media types
  - 1 off-site location

### Multi-User Setup
- For multiple users, host on local network server
- Configure Streamlit for network access
- See Streamlit documentation for deployment

## Performance Tips ⚡

### Speed Up Application
- Keep database size under 1GB
- Archive old cases (export to Excel, delete from DB)
- Regular backups (keep 30 max)
- Close unused browser tabs

### Large Labs
- For 1000+ cases/month, consider PostgreSQL migration
- Use dedicated server
- Enable caching in Streamlit

## Updates & Maintenance 🔄

### Check for Updates
```bash
pip list --outdated
```

### Update Dependencies
```bash
pip install --upgrade streamlit pandas fpdf2
```

### Database Migrations
- Automatic for new columns
- Manual for structural changes (contact developer)

## Support & Contact 📞

### Getting Help
1. Check this README thoroughly
2. Review error messages carefully
3. Check backup files
4. Contact system administrator

### Reporting Issues
Include:
- Error message (screenshot)
- Steps to reproduce
- Python version: `python --version`
- OS version
- Database backup (if sharing, remove patient data)

## License 📄

This system is proprietary software developed for A1 Dental Lab.
All rights reserved © 2024-2026

---

## Quick Reference Card 🎴

### Common Tasks

| Task | Location | Key Steps |
|------|----------|-----------|
| Add Doctor | Settings → Doctors | Enter name → Add |
| Set Prices | Settings → Price Lists | Select entity → Add material & price |
| Register Case | New Case | Select doctor → Choose teeth → Select material → Save |
| Deliver Case | Delivery | Find case → Click "تم التسليم النهائي" |
| Create Invoice | Invoices | Select entity → Check cases → Generate PDF / Confirm |
| Search Cases | Archive | Use search boxes |
| Backup Database | Sidebar | Click "💾 نسخة احتياطية" |

### Keyboard Shortcuts
- `Ctrl + R` - Refresh page
- `Ctrl + Click` - Multi-select (in some browsers)
- `Tab` - Navigate fields
- `Enter` - Submit forms

### Status Meanings
- 🔵 **في المعمل** - Currently in lab
- 🟣 **في المعمل - بعد Try-in** - In lab after Try-in delivered
- 🟢 **تم التسليم** - Delivered to doctor

### Priority Levels
- **عادي** (Normal) - Standard cases
- **مهم** (Important) - Rush cases
- **عاجل** (Urgent) - Emergency cases

---

**Built with ❤️ for A1 Dental Lab**

**Version:** 2.0 | **Last Updated:** February 2026
