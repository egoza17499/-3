# db_manager.py - Глобальный экземпляр базы данных
from database import Database
from config import DATABASE_URL

# Создаём и экспортируем глобальный экземпляр БД
db = Database(DATABASE_URL)

# ============================================================
# МЕТОДЫ ДЛЯ РАБОТЫ С АЭРОДРОМАМИ
# ============================================================

def get_aerodromes_by_city(city_name: str):
    """Вернуть ВСЕ аэродромы в городе"""
    query = """
        SELECT id, name, city, airport_name, housing_info
        FROM aerodromes
        WHERE LOWER(city) = LOWER(%s)
           OR LOWER(name) ILIKE %s
        ORDER BY airport_name, name
    """
    return db.fetch_all(query, city_name, f'%{city_name}%')

def get_aerodrome_by_id(aerodrome_id: int):
    """Вернуть аэродром по ID"""
    query = """
        SELECT id, name, city, airport_name, housing_info
        FROM aerodromes
        WHERE id = %s
    """
    return db.fetch_one(query, aerodrome_id)

def get_aerodrome_phones(aerodrome_id: int):
    """Вернуть все телефоны аэродрома"""
    query = """
        SELECT phone_name, phone_number
        FROM aerodrome_phones
        WHERE aerodrome_id = %s
        ORDER BY phone_name
    """
    return db.fetch_all(query, aerodrome_id)

def get_aerodrome_documents(aerodrome_id: int):
    """Вернуть все документы аэродрома"""
    query = """
        SELECT doc_name, doc_text
        FROM aerodrome_documents
        WHERE aerodrome_id = %s
        ORDER BY doc_name
    """
    return db.fetch_all(query, aerodrome_id)

def get_aerodrome_by_search(search_text: str):
    """Найти аэродром по названию (возвращает первый результат)"""
    query = """
        SELECT id, name, city, airport_name, housing_info
        FROM aerodromes
        WHERE LOWER(name) ILIKE %s
           OR LOWER(city) ILIKE %s
           OR LOWER(airport_name) ILIKE %s
        LIMIT 1
    """
    search_pattern = f'%{search_text}%'
    return db.fetch_one(query, search_pattern, search_pattern, search_pattern)

def get_safety_block_by_number(block_number: int):
    """Вернуть блок безопасности по номеру"""
    query = """
        SELECT block_number, block_text
        FROM safety_blocks
        WHERE block_number = %s
    """
    return db.fetch_one(query, block_number)
