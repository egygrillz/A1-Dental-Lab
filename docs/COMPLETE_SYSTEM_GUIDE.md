# A1 Dental Lab - Complete System Guide
## نظام إدارة المعمل الشامل مع صلاحيات متعددة المستخدمين

---

## 🎯 New Features - الميزات الجديدة

### 1. Multi-User Authentication System (نظام المستخدمين المتعدد)

#### ✅ User Management
- **إنشاء حسابات متعددة** - Unlimited user accounts
- **4 مستويات صلاحيات:**
  - 👑 **Admin (مدير النظام)** - Full system control
  - 👨‍💼 **Manager (مدير)** - Cases, invoices, reports
  - 💰 **Accountant (محاسب)** - Invoices and payments
  - 🔧 **Technician (فني)** - Case entry and updates

#### ✅ Security Features
- **🔐 Encrypted Passwords** - SHA-256 hashing
- **🔑 Session Management** - Secure login/logout
- **⏱️ Activity Tracking** - Every action logged
- **👥 User Profiles** - Full name, email, phone
- **🚫 Account Control** - Enable/disable accounts

---

### 2. Role-Based Permissions (الصلاحيات حسب الدور)

#### 📋 Permission Matrix

| الصلاحية | الحالات | الأطباء | الفواتير | التقارير | الإعدادات | المستخدمين |
|----------|--------|---------|----------|-----------|-----------|------------|
| **مدير النظام** | ✅ الكل | ✅ الكل | ✅ الكل | ✅ الكل | ✅ الكل | ✅ الكل |
| **مدير** | ✅ الكل | ✅ الكل | ✅ الكل | ✅ الكل | ✅ عرض | ✅ عرض |
| **محاسب** | ✅ عرض + تصدير | ✅ عرض | ✅ الكل | ✅ عرض + تصدير | ❌ | ❌ |
| **فني** | ✅ عرض + إنشاء + تعديل | ✅ عرض | ✅ عرض | ✅ عرض | ❌ | ❌ |

#### 🔧 Customizable Permissions
- تخصيص صلاحيات كل دور
- 5 أنواع صلاحيات لكل قسم:
  - **عرض** (View)
  - **إنشاء** (Create)
  - **تعديل** (Edit)
  - **حذف** (Delete)
  - **تصدير** (Export)

---

### 3. Complete Activity Log (سجل النشاطات الشامل)

#### 📊 What's Tracked
Every single action is logged:
- ✅ **Login/Logout** - تسجيل الدخول والخروج
- ✅ **Case Creation** - إنشاء الحالات
- ✅ **Case Updates** - تعديل الحالات
- ✅ **Case Delivery** - تسليم الحالات
- ✅ **Invoice Generation** - إصدار الفواتير
- ✅ **Payment Recording** - تسجيل المدفوعات
- ✅ **User Management** - إدارة المستخدمين
- ✅ **Settings Changes** - تعديل الإعدادات
- ✅ **Data Deletion** - حذف البيانات

#### 🔍 Activity Log Features
- **تتبع تفصيلي:**
  - من قام بالإجراء
  - متى تم الإجراء (تاريخ ووقت)
  - نوع الإجراء
  - القسم المتأثر
  - البيانات القديمة والجديدة
  - وصف تفصيلي

- **فلترة متقدمة:**
  - حسب المستخدم
  - حسب القسم
  - حسب نوع الإجراء
  - حسب التاريخ (من - إلى)
  - عدد السجلات المطلوبة

- **تحليلات:**
  - رسوم بيانية للنشاط
  - توزيع الإجراءات
  - النشاط بمرور الوقت
  - أكثر المستخدمين نشاطاً

- **تصدير:**
  - تصدير إلى Excel
  - تقارير مفصلة

---

### 4. Enhanced Data Security (أمان محسّن للبيانات)

#### 🔒 Security Layers
1. **User Authentication** - مصادقة المستخدم
2. **Session Tokens** - رموز الجلسة الآمنة
3. **Password Hashing** - تشفير كلمات المرور
4. **Permission Checks** - فحص الصلاحيات
5. **Activity Logging** - تسجيل النشاطات
6. **Data Validation** - التحقق من صحة البيانات

#### 🛡️ Protection Features
- لا يمكن حذف المدير الرئيسي
- لا يمكن للمستخدمين عرض إلا ما يسمح لهم به
- تسجيل خروج تلقائي عند إغلاق المتصفح
- إمكانية تعطيل الحسابات بدلاً من الحذف
- نسخ احتياطي تلقائي قبل الإجراءات الحساسة

---

### 5. User Management Dashboard (لوحة إدارة المستخدمين)

#### 👥 Features
1. **عرض جميع المستخدمين:**
   - الاسم الكامل
   - اسم المستخدم
   - الصلاحية
   - الحالة (نشط/معطل)
   - آخر دخول
   - عدد مرات الدخول
   - البريد الإلكتروني
   - رقم الهاتف

2. **إضافة مستخدم جديد:**
   - اسم المستخدم (فريد)
   - كلمة المرور (مشفرة)
   - الاسم الكامل
   - البريد الإلكتروني (اختياري)
   - رقم الهاتف (اختياري)
   - الصلاحية
   - ملاحظات (اختيارية)

3. **تعديل المستخدمين:**
   - تغيير الاسم
   - تغيير الصلاحية
   - تحديث البيانات الشخصية
   - تغيير كلمة المرور
   - تفعيل/تعطيل الحساب

4. **إحصائيات:**
   - إجمالي المستخدمين
   - المستخدمون النشطون
   - المستخدمون المعطلون
   - إجمالي مرات الدخول
   - توزيع الأدوار
   - أكثر المستخدمين نشاطاً
   - المستخدمون الجدد

---

### 6. Enhanced Case Entry (تسجيل حالات محسّن)

#### ✨ New Features in Case Entry
- **تحديد الأولوية:**
  - عادي (Normal)
  - مهم (Important)
  - عاجل (Urgent)

- **تخصيص الفني:**
  - اختيار الفني المسؤول عن الحالة
  - تتبع من عمل ماذا

- **تتبع كامل:**
  - من أنشأ الحالة
  - متى تم الإنشاء
  - آخر تعديل
  - من قام بالتعديل

---

### 7. Advanced Reporting (تقارير متقدمة)

#### 📊 Available Reports
1. **تقرير النشاطات:**
   - جميع الإجراءات
   - حسب المستخدم
   - حسب الفترة الزمنية
   - حسب نوع النشاط

2. **تقرير المستخدمين:**
   - نشاط كل مستخدم
   - الحالات المسجلة
   - الفواتير المصدرة
   - أوقات العمل

3. **تقرير الحالات:**
   - الحالات النشطة
   - الحالات المكتملة
   - الحالات المتأخرة
   - حسب الأولوية

4. **تقرير المالي:**
   - الإيرادات
   - المديونيات
   - المدفوعات
   - حسب الدكتور/المركز

---

## 📦 File Structure - هيكل الملفات

```
A1-Dental-Lab/
├── main.py                         # نقطة الدخول مع المصادقة
├── auth_manager.py                 # إدارة المصادقة والصلاحيات ⭐ NEW
├── login_page.py                   # صفحة تسجيل الدخول ⭐ NEW
├── user_management_page.py         # إدارة المستخدمين ⭐ NEW
├── activity_log_page.py            # سجل النشاطات ⭐ NEW
├── database.py                     # محسّن ✨ ENHANCED
├── entry_page.py                   # تسجيل الحالات - محسّن ✨ ENHANCED
├── checkout_page.py                # تسليم الحالات
├── invoice_page.py                 # الفواتير
├── archive_page.py                 # الأرشيف
├── dashboard_page.py               # لوحة المعلومات
├── doctors_page.py                 # إدارة الأطباء والإعدادات
├── constants.py                    # الثوابت
├── requirements.txt                # المكتبات المطلوبة
├── lab_database.db                 # قاعدة البيانات
├── uploads/                        # ملفات الحالات
├── backups/                        # النسخ الاحتياطية
└── fonts/                          # الخطوط العربية
```

---

## 🗄️ Database Schema - قاعدة البيانات

### New Tables (الجداول الجديدة):

#### 1. users (المستخدمون)
```sql
- id: معرف
- username: اسم المستخدم (فريد)
- password_hash: كلمة المرور المشفرة
- full_name: الاسم الكامل
- email: البريد الإلكتروني
- phone: رقم الهاتف
- role: الصلاحية
- is_active: نشط/معطل
- created_at: تاريخ الإنشاء
- created_by: من أنشأه
- last_login: آخر دخول
- login_count: عدد مرات الدخول
- notes: ملاحظات
```

#### 2. permissions (الصلاحيات)
```sql
- id: معرف
- role: الدور
- module: القسم
- can_view: يمكن العرض
- can_create: يمكن الإنشاء
- can_edit: يمكن التعديل
- can_delete: يمكن الحذف
- can_export: يمكن التصدير
```

#### 3. user_sessions (جلسات المستخدمين)
```sql
- id: معرف
- username: اسم المستخدم
- session_token: رمز الجلسة
- login_time: وقت الدخول
- logout_time: وقت الخروج
- ip_address: عنوان IP
- is_active: نشط/منتهي
```

#### 4. activity_log (سجل النشاطات)
```sql
- id: معرف
- username: اسم المستخدم
- action_type: نوع الإجراء
- module: القسم
- description: الوصف
- record_id: معرف السجل المتأثر
- old_data: البيانات القديمة
- new_data: البيانات الجديدة
- ip_address: عنوان IP
- timestamp: الوقت والتاريخ
```

### Enhanced Tables (جداول محسّنة):

#### cases (الحالات) - إضافات جديدة:
```sql
+ priority: الأولوية (normal/important/urgent)
+ lab_technician: الفني المسؤول
+ discount: الخصم
+ tax: الضريبة
+ final_price: السعر النهائي
```

---

## 🚀 Installation & Setup - التثبيت والإعداد

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: First Run
```bash
streamlit run main.py
```

### Step 3: Default Login
```
Username: admin
Password: admin123
```

### Step 4: Change Admin Password
1. Login as admin
2. Go to إدارة المستخدمين (User Management)
3. Edit admin user
4. Change password
5. Save

### Step 5: Create Users
1. Go to إدارة المستخدمين
2. Click إضافة مستخدم جديد
3. Fill in details
4. Assign role
5. Save

---

## 👥 User Roles Explained - شرح الصلاحيات

### 👑 Admin (مدير النظام)
**Full system access - صلاحيات كاملة**

✅ Can do everything:
- Create, edit, delete cases
- Manage doctors and centers
- Generate and cancel invoices
- Create and manage users
- Change permissions
- View all reports
- Export all data
- Modify settings
- View activity log

**Use case:** System owner, lab manager

---

### 👨‍💼 Manager (مدير)
**Operations management - إدارة العمليات**

✅ Can:
- Create, edit, delete cases
- Manage doctors and centers
- Generate and cancel invoices
- View all reports
- Export data
- View users (cannot modify)

❌ Cannot:
- Create or edit users
- Change permissions
- Modify system settings

**Use case:** Lab manager, operations manager

---

### 💰 Accountant (محاسب)
**Financial management - الإدارة المالية**

✅ Can:
- View all cases
- Generate invoices
- Record payments
- View financial reports
- Export financial data

❌ Cannot:
- Create or edit cases
- Manage doctors
- Manage users
- Change settings

**Use case:** Accountant, financial manager

---

### 🔧 Technician (فني)
**Case entry only - تسجيل الحالات فقط**

✅ Can:
- View cases
- Create new cases
- Edit cases they created
- View doctors list

❌ Cannot:
- Delete cases
- Generate invoices
- Manage doctors
- Manage users
- Access settings

**Use case:** Lab technician, case entry clerk

---

## 📱 Daily Workflow Examples - أمثلة سير العمل اليومي

### Scenario 1: New Case Entry (فني)
1. Login as technician
2. Go to تسجيل حالة
3. Select doctor
4. Enter patient name
5. Select teeth
6. Choose materials
7. Set priority
8. Add your name as technician
9. Save

✅ Activity logged:
- "Technician John created case A1-260211001 for patient Ahmed"

---

### Scenario 2: Case Delivery (مدير)
1. Login as manager
2. Go to تسليم حالات
3. Find case
4. Click تم التسليم
5. Confirm

✅ Activity logged:
- "Manager Sarah delivered case A1-260211001"

---

### Scenario 3: Invoice Generation (محاسب)
1. Login as accountant
2. Go to الفواتير
3. Select doctor
4. Check unpaid cases
5. Generate PDF
6. Mark as paid

✅ Activity logged:
- "Accountant Ali created invoice INV-202602-0015 for Dr. Ahmed"
- "Accountant Ali marked 3 cases as paid"

---

### Scenario 4: User Management (مدير النظام)
1. Login as admin
2. Go to إدارة المستخدمين
3. Click إضافة مستخدم
4. Fill details
5. Assign role
6. Save

✅ Activity logged:
- "Admin created new user: Mohamed Ali (technician)"

---

## 🔍 Activity Log Use Cases - استخدامات سجل النشاطات

### Use Case 1: Track Who Delivered Cases
**السؤال:** من قام بتسليم الحالة رقم A1-260211001؟

**الحل:**
1. Go to سجل النشاطات
2. Filter by: Module = "cases", Action = "update"
3. Search for case code
4. See: "Manager Sarah delivered case at 14:30"

---

### Use Case 2: Monitor User Activity
**السؤال:** ماذا فعل الفني أحمد اليوم؟

**الحل:**
1. Go to سجل النشاطات
2. Filter by: User = "ahmad", Date = Today
3. See all actions:
   - Created 5 cases
   - Updated 2 cases
   - Logged in at 08:00
   - Logged out at 17:00

---

### Use Case 3: Audit Financial Changes
**السؤال:** من أصدر الفواتير هذا الأسبوع؟

**الحل:**
1. Go to سجل النشاطات
2. Filter by: Module = "invoices", Date = This week
3. See all invoice activities with details

---

### Use Case 4: Track Setting Changes
**السؤال:** من غيّر أسعار المواد للدكتور أحمد؟

**الحل:**
1. Go to سجل النشاطات
2. Filter by: Module = "settings", Action = "update"
3. See old and new prices with timestamp

---

## ⚠️ Important Notes - ملاحظات مهمة

### Security Best Practices:
1. **Change admin password immediately** - غيّر كلمة مرور المدير فوراً
2. **Use strong passwords** - استخدم كلمات مرور قوية
3. **Don't share accounts** - لا تشارك الحسابات
4. **Regular backups** - نسخ احتياطية منتظمة
5. **Review activity log weekly** - راجع سجل النشاطات أسبوعياً

### Admin Responsibilities:
1. Create user accounts for all staff
2. Assign appropriate roles
3. Monitor system activity
4. Review and export logs monthly
5. Disable accounts of ex-employees immediately
6. Regular password changes (quarterly)

### User Best Practices:
1. Don't share your password
2. Logout when leaving computer
3. Report suspicious activity
4. Keep contact info updated

---

## 🆘 Troubleshooting - حل المشاكل

### Problem: Can't login
**Solution:**
- Check username (case-sensitive)
- Check if account is active
- Contact admin to reset password

### Problem: Permission denied
**Solution:**
- Check your role
- Contact admin to update permissions
- Verify you're in the right module

### Problem: Activity not showing in log
**Solution:**
- Wait a few seconds and refresh
- Check filter settings
- Verify date range

---

## 📊 Reports You Can Generate - التقارير المتاحة

### 1. User Activity Report
- Activities per user
- Login/logout times
- Actions performed
- Excel export

### 2. Case History Report
- All changes to a case
- Who created, modified, delivered
- Complete audit trail

### 3. Financial Audit Report
- All invoices generated
- Payments recorded
- By user and date
- Excel export

### 4. System Usage Report
- Peak usage hours
- Most active users
- Most used features
- Activity trends

---

## 🎓 Training Recommendations - توصيات التدريب

### For Admin:
- 2 hours: User management
- 1 hour: Permission configuration
- 1 hour: Activity log review
- 1 hour: Report generation

### For Manager:
- 1 hour: Case management
- 1 hour: Invoice generation
- 30 min: Report viewing

### For Accountant:
- 1 hour: Invoice system
- 30 min: Payment recording
- 30 min: Financial reports

### For Technician:
- 1 hour: Case entry
- 30 min: Material selection
- 30 min: System basics

---

**System Ready for Production! 🚀**
**النظام جاهز للاستخدام! 🎉**

---

*Version 2.0 with Multi-User Support*
*الإصدار 2.0 مع دعم المستخدمين المتعددين*
