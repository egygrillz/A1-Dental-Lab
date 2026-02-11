# Quick Start Guide - A1 Dental Lab 🚀

Get your dental lab management system up and running in 5 minutes!

## Installation (5 Minutes)

### Step 1: Install Python (If not already installed)
- Download from: https://www.python.org/downloads/
- During installation: **CHECK** ☑️ "Add Python to PATH"
- Click Install

### Step 2: Open Terminal/Command Prompt
**Windows:**
- Press `Windows + R`
- Type `cmd` and press Enter

**Mac:**
- Press `Cmd + Space`
- Type `terminal` and press Enter

### Step 3: Navigate to Project Folder
```bash
cd path\to\A1-Dental-Lab
```
Replace `path\to\` with your actual folder location

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```
Wait 2-3 minutes for installation to complete

### Step 5: Run the Application
```bash
streamlit run main.py
```

The application will automatically open in your browser at `http://localhost:8501`

If browser doesn't open automatically, copy the URL from terminal and paste in browser.

---

## First-Time Setup (10 Minutes)

### 1. Add Your First Doctor (2 min)

1. Click **⚙️ الإعدادات** (Settings) in the sidebar
2. Go to **👨‍⚕️ إدارة الأطباء** tab
3. Enter doctor name, example: "د/ أحمد محمد"
4. Click **إضافة**
5. Repeat for all your doctors

**OR** Add a Dental Center:
1. Go to **🏥 إدارة مراكز الأسنان** tab
2. Enter center name, example: "مركز النور لطب الأسنان"
3. Click **إضافة المركز**
4. Add branches if needed

### 2. Set Material Prices (5 min)

1. Stay in **⚙️ الإعدادات**
2. Go to **💰 قائمة الأسعار** tab
3. Select the doctor or center you just added
4. Add materials one by one:

**Example Prices:**
```
Zircon → 1200 EGP
E-max → 1000 EGP
Porcelain → 800 EGP
Metal-Ceramic → 700 EGP
PMMA → 150 EGP
Nightguard → 500 EGP
```

For each material:
- Enter material name
- Enter price
- Click **➕ حفظ السعر**

### 3. Register Your First Case (3 min)

1. Click **📥 تسجيل حالة** (New Case) in sidebar
2. Select "دكتور" and choose the doctor
3. Enter patient name, example: "محمد علي"
4. Click teeth on the dental chart (try clicking 11, 12, 13)
5. Select material (e.g., "Zircon")
6. Click **✅ تأكيد**
7. Enter shade (e.g., "A2")
8. Set delivery date (default is 7 days from now)
9. Click **💾 حفظ وتسجيل الحالة**

Done! Your first case is registered!

---

## Daily Workflow

### Morning Routine:
1. **📊 Dashboard** - Check cases due today
2. **📥 New Cases** - Register morning arrivals
3. **📤 Deliveries** - Mark completed cases as delivered

### During the Day:
- Register new cases as they arrive
- Update status of Try-in cases
- Check upcoming deadlines

### End of Day:
1. **🧾 Invoices** - Generate invoices for deliveries
2. **💾 Backup** - Click backup button in sidebar
3. **📊 Dashboard** - Review daily performance

---

## Common Tasks (With Screenshots)

### Register a Crown

1. **📥 New Case**
2. Select doctor → Enter patient name
3. Click ONE tooth (e.g., 21)
4. Select material → Click ✅ تأكيد
5. Add details → Click 💾 Save

**Time:** 2 minutes

### Register a Bridge

1. **📥 New Case**
2. Select doctor → Enter patient name
3. Click MULTIPLE consecutive teeth (e.g., 11, 12, 13)
4. Select material → Click ✅ تأكيد
5. Add details → Click 💾 Save

**Time:** 2 minutes

### Register a Nightguard

1. **📥 New Case**
2. Select doctor → Enter patient name
3. Check ☑️ **تسجيل Nightguard**
4. Click **الفك العلوي** or **الفك السفلي**
5. Add details → Click 💾 Save

**Time:** 1 minute

### Deliver a Case

1. **📤 تسليم حالات**
2. Find the case (use search if needed)
3. If Try-in case:
   - First click: **تم تسليم الـ Try-in** (Try-in delivered)
   - Later click: **تم التسليم النهائي** (Final delivery)
4. If regular case:
   - Click: **تم التسليم النهائي**
5. Confirm by clicking button again

**Time:** 30 seconds per case

### Generate Invoice

1. **🧾 الفواتير**
2. Select doctor or center
3. View unpaid cases
4. Check ☑️ cases to include
5. Click **📄 إصدار فاتورة PDF**
6. Download and print
7. After payment, click **✅ تأكيد التحصيل**

**Time:** 2 minutes

---

## Tips & Tricks 💡

### Speed Tips:
- **Tab key** - Navigate between fields quickly
- **Enter key** - Submit forms
- **Search bar** - Find cases instantly
- **Select all checkbox** - Invoice multiple cases at once

### Best Practices:
✅ Enter cases immediately when received
✅ Update delivery status promptly
✅ Generate invoices weekly
✅ Create backups daily
✅ Archive old cases monthly

### Common Shortcuts:
- Add doctor: Settings → Doctors → Enter name → Add
- Set price: Settings → Prices → Select entity → Enter material & price → Save
- New case: New Case → Select doctor → Patient → Teeth → Material → Save
- Deliver: Delivery → Find case → Click deliver → Confirm
- Invoice: Invoices → Select → Check cases → Generate PDF

---

## Troubleshooting 🔧

### Problem: Application won't start
**Solution:**
```bash
pip install --upgrade streamlit
streamlit run main.py
```

### Problem: Can't find my case
**Solution:**
- Use search bar in 🗄️ الأرشيف (Archive)
- Search by patient name or case code

### Problem: PDF has weird characters
**Solution:**
- Ensure fonts folder exists with DejaVu fonts
- Reinstall: `pip install --upgrade fpdf2`

### Problem: Forgot to backup
**Solution:**
- Click **💾 نسخة احتياطية** in sidebar NOW
- Set daily reminder to backup

### Problem: Made a mistake in case
**Solution:**
- Go to 🗄️ الأرشيف
- Find the case
- Click 🗑️ حذف to delete
- Register again correctly

### Problem: Lost database
**Solution:**
- Look in `backups/` folder
- Copy latest backup file
- Rename to `lab_database.db`
- Restart application

---

## Keyboard Reference 

| Key | Action |
|-----|--------|
| Tab | Next field |
| Shift + Tab | Previous field |
| Enter | Submit / Confirm |
| Ctrl + R | Refresh page |
| Esc | Close popup |

---

## Status Indicators 🚦

| Icon/Color | Meaning |
|------------|---------|
| 🔵 في المعمل | In lab - working on it |
| 🟣 في المعمل - بعد Try-in | In lab after Try-in |
| 🟢 تم التسليم | Delivered to doctor |
| ✅ مدفوع | Paid |
| ⏳ غير مدفوع | Unpaid |
| ⚡ عاجل | Urgent priority |

---

## Getting Help 📞

### Before Asking for Help:
1. ✅ Read the error message carefully
2. ✅ Check this Quick Start Guide
3. ✅ Review the full README.md
4. ✅ Restart the application
5. ✅ Check if backup exists

### When Reporting Issues:
Include:
- What you were trying to do
- What happened instead
- Error message (screenshot)
- When it started happening

---

## Next Steps 🎯

Now that you're set up:

**Week 1:**
- Register all incoming cases
- Deliver completed cases
- Get familiar with the interface

**Week 2:**
- Generate your first invoices
- Start using Try-in feature
- Explore the dashboard

**Week 3:**
- Set up all your doctors and centers
- Configure all material prices
- Create backup routine

**Month 1:**
- Review analytics on dashboard
- Archive old cases
- Optimize your workflow

---

## Resource Quick Links 🔗

- **Full Manual:** README.md
- **Technical Details:** OPTIMIZATION_REPORT.md
- **Python Help:** https://www.python.org/
- **Streamlit Docs:** https://docs.streamlit.io/

---

## Success Checklist ✅

After following this guide, you should be able to:

- [ ] Start the application
- [ ] Add doctors/centers
- [ ] Set material prices
- [ ] Register a crown case
- [ ] Register a bridge case
- [ ] Register a nightguard
- [ ] Deliver a case
- [ ] Generate an invoice
- [ ] Create a backup
- [ ] Search for cases

If you can do all these, you're ready to use the system full-time!

---

## Remember 💭

- **Save Often** - Click that backup button daily!
- **Stay Organized** - Update case statuses promptly
- **Be Consistent** - Use standard material names
- **Keep Learning** - Explore all features
- **Ask Questions** - Don't hesitate to seek help

---

**You're all set! 🎉**

**Ready to manage your dental lab like a pro? Let's go!**

---

*Last Updated: February 2026*
*System Version: 2.0*
*Quick Start Guide v1.0*
