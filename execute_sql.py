"""
Скрипт для выполнения SQL и заполнения базы аэродромов
"""

import psycopg2
from config import DATABASE_URL
import os

def main():
    print("🔌 Подключение к базе данных...")
    
    try:
        # Подключаемся к PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Подключено!")
        
        # Проверяем что SQL файл существует
        if not os.path.exists('aerodromes_insert.sql'):
            print("❌ Файл aerodromes_insert.sql не найден!")
            print("📝 Сначала запустите: python aerodromes_complete.py")
            return
        
        # Читаем SQL файл
        print("📖 Чтение SQL файла...")
        with open('aerodromes_insert.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("⚡ Выполнение SQL скрипта...")
        print("⏳ Это может занять несколько секунд...")
        
        # Выполняем SQL
        cursor.execute(sql_script)
        conn.commit()
        
        print("\n✅ База данных заполнена успешно!")
        
        # Проверяем результат
        print("\n📊 ПРОВЕРКА РЕЗУЛЬТАТОВ:")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM aerodromes;")
        aerodromes_count = cursor.fetchone()[0]
        print(f"✈️  Аэродромов в базе: {aerodromes_count}")
        
        cursor.execute("SELECT COUNT(*) FROM aerodrome_phones;")
        phones_count = cursor.fetchone()[0]
        print(f"📱 Телефонов в базе: {phones_count}")
        
        # Показываем несколько примеров
        print("\n📋 ПРИМЕРЫ АЭРОДРОМОВ:")
        print("-" * 40)
        cursor.execute("""
            SELECT a.name, a.city, COUNT(p.id) as phone_count
            FROM aerodromes a
            LEFT JOIN aerodrome_phones p ON a.id = p.aerodrome_id
            GROUP BY a.id, a.name, a.city
            ORDER BY a.name
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            name, city, count = row
            print(f"  • {name} ({city}) — {count} тел.")
        
        print("\n" + "=" * 40)
        print("🎉 ГОТОВО! Теперь проверьте через бота:")
        print("   1. /start")
        print("   2. 📚 Полезная информация")
        print("   3. ✈️ Поиск информации об аэродроме")
        print("   4. Напишите: Нижний Новгород")
        print("=" * 40)
        
    except psycopg2.Error as e:
        print(f"\n❌ Ошибка базы данных: {e}")
        print("\n💡 Проверьте:")
        print("   1. DATABASE_URL в файле .env")
        print("   2. Подключение к интернету")
        print("   3. Доступность PostgreSQL на Render")
        
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()
            print("\n🔌 Отключено от базы данных")

if __name__ == "__main__":
    main()
