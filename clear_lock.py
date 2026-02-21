import psycopg2
import os
from config import DATABASE_URL

# Подключаемся к БД
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Очищаем блокировку
cursor.execute("DELETE FROM instance_lock")
conn.commit()

print("✅ Блокировка очищена!")

cursor.close()
conn.close()
