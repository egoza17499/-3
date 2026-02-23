import os
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# TELEGRAM BOT SETTINGS
# ============================================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в переменных окружения!")

GROUP_ID = int(os.getenv("GROUP_ID", "-1003546878934"))
TOPIC_ID = int(os.getenv("TOPIC_ID", "51"))

# ============================================================================
# ADMIN SETTINGS
# ============================================================================

# Главный админ (из переменных окружения или по умолчанию)
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", "393293807"))

# Список ID админов (через запятую в переменной окружения)
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "393293807")
if ADMIN_IDS_RAW:
    ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip()]
else:
    ADMIN_IDS = []

# Гарантируем что главный админ всегда в списке
if MAIN_ADMIN_ID not in ADMIN_IDS:
    ADMIN_IDS.append(MAIN_ADMIN_ID)

# Список username админов (без @, через запятую)
ADMIN_USERNAMES_RAW = os.getenv("ADMIN_USERNAMES", "")
if ADMIN_USERNAMES_RAW:
    ADMIN_USERNAMES = [
        u.strip().lstrip('@').lower() 
        for u in ADMIN_USERNAMES_RAW.split(",") 
        if u.strip()
    ]
else:
    ADMIN_USERNAMES = []

# Логирование настроек админов
logger.info(f"✅ Главный админ ID: {MAIN_ADMIN_ID}")
logger.info(f"✅ Список админ ID: {ADMIN_IDS}")
logger.info(f"✅ Список админ username: {ADMIN_USERNAMES}")

# ============================================================================
# DATABASE SETTINGS
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не найден в переменных окружения!")

logger.info("✅ PostgreSQL URL найден")

# ============================================================================
# DATE AND VALIDATION SETTINGS
# ============================================================================

DATE_FORMAT = "%d.%m.%Y"

# Периоды валидности (в днях)
VLK_PERIOD = 180              # 6 месяцев
UMO_PERIOD = 360              # 12 месяцев
EXERCISE_4_PERIOD = 180       # 6 месяцев
EXERCISE_7_PERIOD = 360       # 12 месяцев
LEAVE_PERIOD = 360            # 12 месяцев
PARACHUTE_PERIOD = 360        # 12 месяцев
WARNING_PERIOD = 30           # Предупреждение за 30 дней

# ============================================================================
# AIRCRAFT TYPES
# ============================================================================

AIRCRAFT_TYPES = {
    "IL76MD_M": "Ил-76 МД-М",
    "IL76MD_90A": "Ил-76 МД-90А",
    "IL76MD": "Ил-76 МД"
}

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Проверка конфигурации"""
    errors = []
    
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN не найден")
    
    if not DATABASE_URL:
        errors.append("DATABASE_URL не найден")
    
    if not ADMIN_IDS:
        errors.append("ADMIN_IDS пуст")
    
    if MAIN_ADMIN_ID not in ADMIN_IDS:
        errors.append("MAIN_ADMIN_ID не в ADMIN_IDS")
    
    if errors:
        for error in errors:
            logger.error(f"❌ {error}")
        raise ValueError("❌ Ошибки в конфигурации: " + ", ".join(errors))
    
    logger.info("✅ Конфигурация проверена успешно!")
    return True

# Запускаем проверку при импорте
validate_config()
