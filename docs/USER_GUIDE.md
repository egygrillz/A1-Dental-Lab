# 📖 User Guide - دليل المستخدم

<div dir="rtl">

## دليل المستخدم الشامل لنظام إدارة معمل A1

هذا الدليل يشرح كيفية استخدام جميع ميزات النظام خطوة بخطوة.

</div>

---

## Table of Contents / الفهرس

1. [Getting Started / البدء](#getting-started)
2. [Dashboard / لوحة المعلومات](#dashboard)
3. [Case Entry / تسجيل الحالات](#case-entry)
4. [Case Delivery / تسليم الحالات](#case-delivery)
5. [Invoicing / الفواتير](#invoicing)
6. [Archive / الأرشيف](#archive)
7. [Settings / الإعدادات](#settings)
8. [Tips & Tricks / نصائح وحيل](#tips-and-tricks)

---

## Getting Started / البدء

### First Login / أول تسجيل دخول

When you first open the application:
1. The sidebar shows the main menu
2. Start with **Settings** to configure your lab
3. Add doctors and their pricing
4. You're ready to register cases!

### Navigation / التنقل

**Sidebar Menu:**
- 📊 Dashboard - Overview and analytics
- 📥 Register Case - Add new cases
- 📤 Deliver Cases - Checkout and delivery
- 🧾 Invoices - Generate invoices
- 🗄️ Archive - Search and history
- ⚙️ Settings - Configuration

---

## Dashboard / لوحة المعلومات

### Overview Metrics / المؤشرات العامة

**Top Row Shows:**
- 🔵 **Cases in Lab** - Currently active cases
- 🟢 **Delivered This Month** - Completed this month
- 💰 **Monthly Revenue** - Total earnings this month
- ⚠️ **Unpaid Cases** - Outstanding payments

### Upcoming Deliveries / المواعيد القادمة

Shows cases due in the next 7 days with color coding:
- 🔴 Overdue (past due date)
- 🟠 Tomorrow
- 🟡 In 2 days
- 🟢 3+ days away

### Charts & Analytics / الرسوم البيانية

**Statistics Tab:**
- New cases trend (last 30 days)
- Weekly revenue (last 8 weeks)

**Doctors Tab:**
- Cases per doctor
- Revenue per doctor
- Unpaid amounts

**Calendar Tab:**
- Cases grouped by delivery date
- Quick overview of workload

---

## Case Entry / تسجيل الحالات

### Basic Information / المعلومات الأساسية

1. **Select Doctor** - Choose from dropdown
2. **Patient Name** - Enter patient's name
3. **Material** - Main material for the case

### Tooth Selection / اختيار الأسنان

#### Interactive Tooth Map / خريطة الأسنان التفاعلية

The tooth map uses FDI notation (international standard):

**Upper Jaw:**
```
18 17 16 15 14 13 12 11 | 21 22 23 24 25 26 27 28
```

**Lower Jaw:**
```
48 47 46 45 44 43 42 41 | 31 32 33 34 35 36 37 38
```

**How to Select:**
1. Click on individual teeth
2. Selected teeth are marked with ●
3. Continue clicking to select multiple teeth
4. Choose material for the group
5. Click confirm to add

**Tooth Status Indicators:**
- Regular number = Not selected
- Number with ● = Selected (pending)
- Number with ✓ = Confirmed

#### Nightguard Mode / وضع الواقي الليلي

For full-arch nightguards:
1. Check "🌙 هل تريد تسجيل Nightguard؟"
2. Choose upper or lower arch
3. Entire arch is automatically selected
4. Nightguard material and price applied

### Material Selection / اختيار الخامات

**For Crowns/Bridges:**
- Select teeth first
- Choose material (Zircon, E-max, etc.)
- System shows price per tooth
- Confirm to add

**For Multiple Groups:**
- Select first group → choose material → confirm
- Select second group → choose material → confirm
- Continue until all teeth are covered

### Dates & Scheduling / المواعيد والجدولة

**Entry Date / تاريخ الدخول:**
- When case entered the lab
- Usually today's date

**Try-in (Optional) / التجربة:**
- Check "إضافة مرحلة Try-in" if needed
- Set try-in appointment date
- PMMA cost automatically added
- Must be between entry and delivery dates

**Expected Delivery / موعد التسليم:**
- When case should be ready
- Must be after entry date
- Used for scheduling and reminders

### Additional Details / التفاصيل الإضافية

**Shade/Color / اللون:**
- Enter shade guide reference (e.g., A2, B1)
- Important for matching patient's teeth

**Notes / الملاحظات:**
- Special instructions
- Material preferences
- Patient requests
- Internal notes

**File Attachment / إرفاق الملفات:**
- Upload photos
- STL files
- Prescription scans
- Reference images
- Supported: JPG, PNG, PDF, STL, ZIP, RAR

### Saving the Case / حفظ الحالة

Before saving, system validates:
- ✅ Patient name is entered
- ✅ At least one tooth confirmed
- ✅ Valid date range
- ✅ Try-in date (if applicable) is correct

Click **💾 حفظ وتسجيل الحالة** to save.

**After Saving:**
- Case code is generated (e.g., A1-260207130)
- Total price is calculated
- Case appears in delivery page
- All data is backed up

---

## Case Delivery / تسليم الحالات

### Viewing Active Cases / عرض الحالات النشطة

The delivery page shows all cases currently in the lab.

**Search Options:**
- 🔍 Search by patient name
- 🔍 Search by case code

**Case Information Displayed:**
- Case code and patient name
- Doctor name
- Entry date
- Expected delivery date
- Tooth count and shade
- Try-in status

### Try-in Workflow / سير عمل التجربة

**For cases with Try-in:**

**Step 1 - Try-in Delivery:**
1. When try-in is ready
2. Click "تم تسليم الـ Try-in"
3. Confirm by clicking again
4. Status changes to "في المعمل - بعد Try-in"
5. Case remains in lab

**Step 2 - Final Delivery:**
1. After adjustments from try-in
2. Final work is complete
3. Click "تم التسليم النهائي"
4. Confirm by clicking again
5. Case is removed from delivery page
6. Delivery date is recorded

### Regular Delivery / التسليم العادي

**For cases without Try-in:**
1. When work is complete
2. Click "تم التسليم النهائي"
3. Confirm by clicking again
4. Case is marked as delivered
5. Removed from active list

### Confirmation System / نظام التأكيد

**Two-Click Confirmation:**
- First click shows warning
- Second click confirms action
- Prevents accidental deliveries
- No undo after confirmation

---

## Invoicing / الفواتير

### Generating Invoices / إصدار الفواتير

**Step 1 - Select Doctor:**
- Choose doctor from dropdown
- System loads unpaid cases

**Step 2 - Select Cases:**
- Check boxes next to cases to include
- Can select multiple cases
- Running total is displayed

**Step 3 - Generate PDF:**
1. Review selected cases and total
2. Click "📄 إصدار فاتورة PDF"
3. PDF is generated with:
   - Invoice number (INV-YYYYMM-XXXX)
   - Date and time
   - Doctor information
   - Detailed case list
   - Material breakdown
   - Total amount

**Step 4 - Download:**
- Click "📥 تحميل الملف"
- Save PDF to computer
- Print or email to doctor

**Step 5 - Record Payment:**
- Click "✅ تأكيد التحصيل (مدفوع)"
- Cases are marked as paid
- Removed from unpaid list

### Invoice Details / تفاصيل الفاتورة

**Professional PDF includes:**
- **Header:** "A1 DENTAL LAB" logo and title
- **Invoice Number:** Unique sequential number
- **Issue Date:** Current date in Arabic and English
- **Doctor Name:** In Arabic with proper formatting
- **Case Table:**
  - Case code
  - Patient name
  - Material type
  - Quantity (teeth count)
  - Shade/color
  - Entry date
  - Price
- **Total:** Bold, highlighted total amount
- **Multi-material cases:** Separate rows per material

### Payment Tracking / تتبع الدفعات

**Paid Status:**
- Cases marked as paid won't appear again
- Historical invoices in archive
- Can view past invoices anytime

**Unpaid Cases:**
- Remain in the invoice list
- Can be re-invoiced
- Highlighted in dashboard metrics

---

## Archive / الأرشيف

### Search & Filter / البحث والتصفية

**Search Options:**
- 🔍 **By Patient Name** - Find specific patient
- 👨‍⚕️ **By Doctor** - View all cases for a doctor
- Can combine both filters

### Case Details / تفاصيل الحالة

Each case in archive shows:
- Case code and basic info
- Tooth map and materials
- All prices (including PMMA if applicable)
- Final total
- Shade and notes
- Attached files

### File Management / إدارة الملفات

**Upload Additional Files:**
1. Click on a case in archive
2. Use file uploader
3. Select new file
4. Click "حفظ الملف"
5. File is attached to case

**View Existing Files:**
- Files shown in case details
- Click to download
- Photos displayed inline

### Generate Reports / إصدار التقارير

**Detailed PDF Report:**
1. Expand case in archive
2. Click "📑 تقرير مفصل (عربي)"
3. PDF generated with:
   - Case code and dates
   - Doctor and patient info
   - Complete tooth breakdown
   - Material details and prices
   - PMMA costs (if applicable)
   - Final total
   - Shade information
   - Notes
   - Attached images

**Report Uses:**
- Record keeping
- Quality control
- Client communication
- Historical reference

### Delete Cases / حذف الحالات

**⚠️ Warning: Deletion is permanent!**

To delete a case:
1. Expand case in archive
2. Click "🗑️ حذف"
3. Confirm deletion
4. Case is permanently removed

**When to Delete:**
- Duplicate entries
- Test cases
- Cancelled work
- **Not recommended** for completed cases (keep for history)

---

## Settings / الإعدادات

### Doctor Management / إدارة الأطباء

**Add New Doctor:**
1. Go to Settings → "👨‍⚕️ إدارة الأطباء"
2. Enter doctor name
3. Click "إضافة"
4. Doctor code auto-generated (D-XXX)

**Delete Doctor:**
1. Find doctor in list
2. Click 🗑️ button
3. Doctor removed
4. **Note:** Cannot delete if doctor has cases

### Price Management / إدارة الأسعار

**Setting Material Prices:**

1. Select doctor from dropdown
2. Enter material name (e.g., "Zircon")
3. Enter price (e.g., 500)
4. Click "➕ حفظ السعر"

**Common Materials to Add:**
- Zircon (زركون)
- E-max (إي-ماكس)
- Porcelain (بورسلين)
- Metal-Ceramic (معدن بورسلين)
- PMMA (for try-in)
- Nightguard (واقي ليلي)

**Edit Existing Prices:**
1. Select doctor
2. View price table
3. Click in "price" column
4. Edit value
5. Click "💾 حفظ التعديلات"

**Price Per Doctor:**
- Each doctor can have different prices
- Same material, different price
- Allows flexible pricing strategy

---

## Tips & Tricks / نصائح وحيل

### Efficiency Tips / نصائح للكفاءة

**Quick Case Entry:**
1. Keep common materials in price list
2. Use descriptive patient names
3. Add notes for special cases
4. Attach photos immediately

**Batch Processing:**
1. Enter all morning cases first
2. Then set expected delivery dates
3. Group similar materials together

**Search Shortcuts:**
1. Use partial names (e.g., "Moh" for Mohammed)
2. Case codes are searchable
3. Combine patient + doctor search

### Best Practices / أفضل الممارسات

**Daily Routine:**
1. Start day checking dashboard
2. Review upcoming deliveries
3. Register new cases
4. Update delivery status
5. End day with manual backup

**Weekly Tasks:**
1. Generate invoices for the week
2. Follow up on unpaid cases
3. Review dashboard analytics
4. Archive old cases

**Monthly Tasks:**
1. Check revenue reports
2. Review doctor statistics
3. Update prices if needed
4. Clean up test data

### Data Safety / أمان البيانات

**Automatic Backups:**
- Created in `backups/` folder
- Last 30 backups retained
- Timestamped filenames

**Manual Backups:**
1. Click "💾 نسخة احتياطية" in sidebar
2. Backup created instantly
3. Success message shown

**External Backups:**
1. Weekly: Copy `lab_database.db` to USB
2. Monthly: Upload to cloud storage
3. Before major changes: Manual backup

### Keyboard Shortcuts / اختصارات لوحة المفاتيح

**In Streamlit:**
- `Ctrl + R` - Refresh page
- `Ctrl + K` - Focus search (if available)
- `Tab` - Navigate between fields

### Common Mistakes to Avoid / أخطاء شائعة يجب تجنبها

❌ **Don't:**
- Skip Try-in dates for Try-in cases
- Delete delivered cases (keep for history)
- Forget to backup regularly
- Use unclear patient names

✅ **Do:**
- Validate dates before saving
- Add detailed notes
- Attach reference photos
- Backup before major changes

### Troubleshooting / حل المشكلات

**Case not showing in delivery:**
- Check if it was already delivered
- Verify status in archive
- Search by case code

**PDF not generating:**
- Check fonts are installed
- Verify Arabic text support
- Try refreshing page

**Price not calculating:**
- Check material is in price list
- Verify doctor has prices set
- Confirm teeth are confirmed, not just selected

---

## Keyboard Reference / مرجع اختصارات

### Quick Actions
| Action | Shortcut |
|--------|----------|
| New Case | Navigate to 📥 menu |
| Dashboard | Navigate to 📊 menu |
| Search | Click search box |
| Backup | Sidebar button |
| Refresh | `Ctrl + R` or `F5` |

---

## Glossary / المصطلحات

### Terms Used in System

- **Case Code** - Unique identifier (A1-YYMMDDHHSS)
- **FDI Notation** - International tooth numbering
- **Try-in** - Temporary fitting before final work
- **PMMA** - Material used for try-in
- **Shade** - Color reference for teeth
- **Nightguard** - Full-arch protective appliance

### Status Values

- **في المعمل** - In lab (active)
- **في المعمل - بعد Try-in** - In lab after try-in
- **تم التسليم** - Delivered (completed)

---

## Support / الدعم الفني

If you need help:
1. Check this user guide
2. Review error messages
3. Check SETUP.md for installation issues
4. Contact system administrator

---

**Happy Managing! إدارة موفقة!**

*This system is designed to make your dental lab operations smooth and efficient.*
