from dotenv import load_dotenv
load_dotenv()

import psycopg2
from config import DATABASE_URL

print(f"🔌 Подключение к: {DATABASE_URL[:50]}...")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Проверяем аэродромы
cursor.execute("SELECT COUNT(*) FROM aerodromes;")
count = cursor.fetchone()[0]
print(f"✈️  Аэродромов в базе: {count}")

# Проверяем поиск "Иваново"
cursor.execute("""
    SELECT id, name, city FROM aerodromes 
    WHERE LOWER(name) LIKE '%иваново%' 
    OR LOWER(city) LIKE '%иваново%'
""")
results = cursor.fetchall()
print(f"🔍 Поиск 'Иваново': найдено {len(results)}")
for r in results:
    print(f"   • {r['name']} ({r['city']})")

cursor.close()
conn.close()
