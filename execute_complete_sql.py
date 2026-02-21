"""
Выполнение ПОЛНОГО SQL скрипта
"""
from dotenv import load_dotenv
load_dotenv()

import psycopg2
from config import DATABASE_URL
import os

def main():
    print("🔌 Подключение к базе данных...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Подключено!")
        
        if not os.path.exists('complete_aerodromes.sql'):
            print("❌ Файл complete_aerodromes.sql не найден!")
            return
        
        print("📖 Чтение SQL файла...")
        with open('complete_aerodromes.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("⚡ Выполнение SQL скрипта...")
        cursor.execute(sql_script)
        conn.commit()
        
        print("\n✅ База данных ПОЛНОСТЬЮ заполнена!")
        
        cursor.execute("SELECT COUNT(*) FROM aerodromes;")
        count = cursor.fetchone()[0]
        print(f"📊 Аэродромов в базе: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM aerodrome_phones;")
        phones = cursor.fetchone()[0]
        print(f"📱 Телефонов в базе: {phones}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    main()