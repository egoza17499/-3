from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

print("✅ Переменные окружения загружены!")
print(f"BOT_TOKEN: {'загружен' if os.getenv('BOT_TOKEN') else 'не загружен'}")
print(f"DATABASE_URL: {'загружен' if os.getenv('DATABASE_URL') else 'не загружен'}")