# -*- coding: utf-8 -*-
"""
Constants and configuration for A1 Dental Lab Management System
"""

# =============================================================================
#                           TOOTH NUMBERING
# =============================================================================

# FDI World Dental Federation notation (ISO 3950)
UPPER_RIGHT_TEETH = [18, 17, 16, 15, 14, 13, 12, 11]
UPPER_LEFT_TEETH = [21, 22, 23, 24, 25, 26, 27, 28]
LOWER_RIGHT_TEETH = [48, 47, 46, 45, 44, 43, 42, 41]
LOWER_LEFT_TEETH = [31, 32, 33, 34, 35, 36, 37, 38]

ALL_UPPER_TEETH = UPPER_RIGHT_TEETH + UPPER_LEFT_TEETH
ALL_LOWER_TEETH = LOWER_RIGHT_TEETH + LOWER_LEFT_TEETH
ALL_TEETH = ALL_UPPER_TEETH + ALL_LOWER_TEETH

# =============================================================================
#                           PRICING
# =============================================================================

# Fallback prices if not found in database
DEFAULT_PMMA_PRICE = 150  # ج.م
DEFAULT_NIGHTGUARD_PRICE = 500  # ج.م

# =============================================================================
#                           FILE PATHS
# =============================================================================

UPLOAD_FOLDER = "uploads"
BACKUP_FOLDER = "backups"
FONT_FOLDER = "dejavu-fonts-ttf-2.37/ttf"
FONT_FOLDER_FALLBACK = "fonts"

# =============================================================================
#                           DATABASE
# =============================================================================

DATABASE_NAME = "lab_database.db"
MAX_BACKUPS_TO_KEEP = 30  # Number of backup files to retain

# =============================================================================
#                           CASE STATUS
# =============================================================================

STATUS_IN_LAB = "في المعمل"
STATUS_IN_LAB_AFTER_TRYIN = "في المعمل - بعد Try-in"
STATUS_DELIVERED = "تم التسليم"

ALL_STATUSES = [STATUS_IN_LAB, STATUS_IN_LAB_AFTER_TRYIN, STATUS_DELIVERED]

# Status emoji mapping
STATUS_EMOJI = {
    STATUS_IN_LAB: "🔵",
    STATUS_IN_LAB_AFTER_TRYIN: "🟣",
    STATUS_DELIVERED: "🟢",
}

# =============================================================================
#                           MATERIAL TYPES
# =============================================================================

MATERIAL_TYPES = {
    "crown": "تاج",
    "bridge": "جسر",
    "nightguard": "واقي ليلي",
    "pmma": "PMMA"
}

# Common materials (examples - actual list comes from database)
COMMON_MATERIALS = [
    "Zircon",
    "E-max",
    "Porcelain",
    "Metal-Ceramic",
    "PMMA",
    "Nightguard"
]

# =============================================================================
#                           UI CONFIGURATION
# =============================================================================

# Colors for UI elements
PRIMARY_COLOR = "#1f77b4"
SUCCESS_COLOR = "#2ca02c"
WARNING_COLOR = "#ff7f0e"
ERROR_COLOR = "#d62728"

# Page configuration
PAGE_TITLE = "A1 Dental Lab"
PAGE_ICON = "🦷"
LAYOUT = "wide"

# Date formats
DATE_FORMAT_DISPLAY = "%Y-%m-%d"  # For display
DATE_FORMAT_FILE = "%Y%m%d_%H%M%S"  # For filenames

# =============================================================================
#                           VALIDATION
# =============================================================================

# Minimum and maximum values
MIN_PRICE = 0
MAX_PRICE = 100000  # ج.م
MIN_TEETH_COUNT = 1
MAX_TEETH_COUNT = 32

# File upload limits
MAX_FILE_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]
ALLOWED_DOCUMENT_EXTENSIONS = ["pdf", "doc", "docx"]
ALLOWED_3D_EXTENSIONS = ["stl", "obj"]
ALLOWED_ARCHIVE_EXTENSIONS = ["zip", "rar", "7z"]

ALL_ALLOWED_EXTENSIONS = (
    ALLOWED_IMAGE_EXTENSIONS + 
    ALLOWED_DOCUMENT_EXTENSIONS + 
    ALLOWED_3D_EXTENSIONS + 
    ALLOWED_ARCHIVE_EXTENSIONS
)

# =============================================================================
#                           NOTIFICATION SETTINGS
# =============================================================================

# Days before delivery to send reminder
DELIVERY_REMINDER_DAYS = [2, 1]  # Send reminders 2 days and 1 day before

# Email configuration (use environment variables in production!)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# SMTP_EMAIL and SMTP_PASSWORD should be set via environment variables

# =============================================================================
#                           REPORTING
# =============================================================================

# PDF settings
PDF_MARGIN = 10
PDF_FONT_SIZE_TITLE = 22
PDF_FONT_SIZE_HEADER = 12
PDF_FONT_SIZE_BODY = 10
PDF_FONT_SIZE_SMALL = 8

# Invoice numbering format
INVOICE_NUMBER_FORMAT = "INV-{year_month}-{sequence:04d}"  # e.g., INV-202402-0001

# =============================================================================
#                           ERROR MESSAGES (Arabic)
# =============================================================================

ERROR_MESSAGES = {
    "no_patient_name": "يجب إدخال اسم المريض",
    "no_teeth_selected": "يجب اختيار الأسنان المطلوبة",
    "invalid_date_range": "تاريخ التسليم يجب أن يكون بعد تاريخ الدخول",
    "invalid_tryin_date": "موعد Try-in يجب أن يكون بين تاريخ الدخول والتسليم",
    "no_doctor_selected": "يجب اختيار الطبيب",
    "database_error": "حدث خطأ في قاعدة البيانات",
    "file_upload_error": "فشل رفع الملف",
    "invalid_file_type": "نوع الملف غير مدعوم",
    "file_too_large": "حجم الملف كبير جداً",
}

# =============================================================================
#                           SUCCESS MESSAGES (Arabic)
# =============================================================================

SUCCESS_MESSAGES = {
    "case_saved": "✅ تم حفظ الحالة بنجاح",
    "case_delivered": "✅ تم تسليم الحالة",
    "invoice_generated": "✅ تم إنشاء الفاتورة",
    "payment_recorded": "✅ تم تسجيل الدفع",
    "doctor_added": "✅ تم إضافة الطبيب",
    "price_updated": "✅ تم تحديث السعر",
    "backup_created": "✅ تم إنشاء نسخة احتياطية",
}

# =============================================================================
#                           HELPER FUNCTIONS
# =============================================================================

def get_status_display(status):
    """Get emoji + text for status"""
    emoji = STATUS_EMOJI.get(status, "⚪")
    return f"{emoji} {status}"


def is_valid_tooth_number(tooth_num):
    """Check if tooth number is valid according to FDI notation"""
    try:
        tooth = int(tooth_num)
        return tooth in ALL_TEETH
    except (ValueError, TypeError):
        return False


def format_price(price):
    """Format price with thousands separator"""
    return f"{price:,.2f} ج.م"


def get_arch_from_tooth(tooth_num):
    """Determine which arch a tooth belongs to"""
    tooth = int(tooth_num)
    if tooth in ALL_UPPER_TEETH:
        return "upper"
    elif tooth in ALL_LOWER_TEETH:
        return "lower"
    else:
        return "unknown"


def group_consecutive_teeth(teeth_list):
    """
    Group consecutive tooth numbers together.
    Example: [11, 12, 13, 21, 22] → [[11, 12, 13], [21, 22]]
    """
    if not teeth_list:
        return []
    
    sorted_teeth = sorted(teeth_list)
    groups = []
    current_group = [sorted_teeth[0]]
    
    for tooth in sorted_teeth[1:]:
        if tooth == current_group[-1] + 1:
            current_group.append(tooth)
        else:
            groups.append(current_group)
            current_group = [tooth]
    
    groups.append(current_group)
    return groups


def teeth_to_display_string(teeth_list):
    """
    Convert list of teeth to display string.
    Example: [11, 12, 13] → "11-13"
    Example: [11, 13] → "11, 13"
    """
    groups = group_consecutive_teeth(teeth_list)
    result = []
    
    for group in groups:
        if len(group) == 1:
            result.append(str(group[0]))
        elif len(group) == 2:
            result.append(f"{group[0]}, {group[1]}")
        else:
            result.append(f"{group[0]}-{group[-1]}")
    
    return " | ".join(result)


# =============================================================================
#                           EXPORT
# =============================================================================

__all__ = [
    # Tooth numbers
    'ALL_UPPER_TEETH',
    'ALL_LOWER_TEETH',
    'ALL_TEETH',
    'UPPER_RIGHT_TEETH',
    'UPPER_LEFT_TEETH',
    'LOWER_RIGHT_TEETH',
    'LOWER_LEFT_TEETH',
    
    # Prices
    'DEFAULT_PMMA_PRICE',
    'DEFAULT_NIGHTGUARD_PRICE',
    
    # Paths
    'UPLOAD_FOLDER',
    'BACKUP_FOLDER',
    'FONT_FOLDER',
    'DATABASE_NAME',
    
    # Status
    'STATUS_IN_LAB',
    'STATUS_IN_LAB_AFTER_TRYIN',
    'STATUS_DELIVERED',
    'ALL_STATUSES',
    'STATUS_EMOJI',
    
    # Functions
    'get_status_display',
    'is_valid_tooth_number',
    'format_price',
    'get_arch_from_tooth',
    'group_consecutive_teeth',
    'teeth_to_display_string',
    
    # Messages
    'ERROR_MESSAGES',
    'SUCCESS_MESSAGES',
]
