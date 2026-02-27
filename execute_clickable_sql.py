import psycopg2
from config import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_sql_file():
    """Выполнить SQL файл с кликабельными номерами"""
    
    logger.info("📄 Читаю SQL файл: complete_aerodromes_clickable.sql")
    
    with open('complete_aerodromes_clickable.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    logger.info("🔌 Подключаюсь к базе данных...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        logger.info("⚡ Выполняю SQL запросы (это может занять несколько минут)...")
        cursor.execute(sql_script)
        conn.commit()
        
        # Проверка результата
        cursor.execute("SELECT COUNT(*) FROM aerodromes")
        aerodromes_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM aerodrome_phones")
        phones_count = cursor.fetchone()[0]
        
        logger.info("="*70)
        logger.info("✅ БАЗА ДАННЫХ ОБНОВЛЕНА УСПЕШНО!")
        logger.info("="*70)
        logger.info(f"📊 Аэродромов: {aerodromes_count}")
        logger.info(f"📱 Телефонов: {phones_count}")
        logger.info("📞 Все номера теперь кликабельные!")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    execute_sql_file()
