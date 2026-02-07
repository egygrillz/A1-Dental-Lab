# Database Information

## Database File

The main database file `lab_database.db` is created automatically when you first run the application.

## Initial State

On first run, the database contains:
- Empty tables (structure only)
- No doctors
- No cases
- No invoices

## Schema Version

Current schema version: 2.0

### Tables Created

1. **doctors_list** - Doctor information
2. **cases** - All case records
3. **doctors_prices** - Material pricing per doctor
4. **invoices** - Invoice records
5. **invoice_cases** - Invoice-to-case linking

### Indexes

Performance indexes are automatically created on:
- `cases.doctor`
- `cases.status`
- `cases.entry_date`
- `cases.is_paid`
- `cases.expected_delivery`

## Backup Information

- Backups stored in: `backups/` folder
- Format: `lab_database_backup_YYYYMMDD_HHMMSS.db`
- Retention: Last 30 backups
- Recommended: Weekly external backups

## Migration

The database schema auto-upgrades when you run newer versions:
- New columns added safely
- Existing data preserved
- No manual migration needed

## Example Database

An example database with sample data is **not included** for security reasons.

To create sample data:
1. Run the application
2. Add a test doctor
3. Add test prices
4. Create a few test cases
5. This becomes your example/demo database

## Restoration

To restore from backup:
1. Stop the application
2. Backup current `lab_database.db`
3. Copy backup file to main folder
4. Rename to `lab_database.db`
5. Restart application

---

**Note:** Never commit actual database files to Git (they're in `.gitignore`)
