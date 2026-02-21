import os

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "-1003546878934"))
TOPIC_ID = int(os.getenv("TOPIC_ID", "51"))

# Admin settings
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", "393293807"))
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "393293807").split(",")]

# Database - PostgreSQL URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Date format
DATE_FORMAT = "%d.%m.%Y"

# Validation periods (in days)
VLK_PERIOD = 180          # 6 месяцев
UMO_PERIOD = 360          # 12 месяцев
EXERCISE_4_PERIOD = 180   # 6 месяцев
EXERCISE_7_PERIOD = 360   # 12 месяцев
LEAVE_PERIOD = 360        # 12 месяцев
PARACHUTE_PERIOD = 360    # 12 месяцев
WARNING_PERIOD = 30       # Предупреждение за 30 дней

# Aircraft types
AIRCRAFT_TYPES = {
    "IL76MD_M": "ИЛ-76 МД-М",
    "IL76MD_90A": "ИЛ-76 МД-90А"
}

# Проверки
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в переменных окружения!")
