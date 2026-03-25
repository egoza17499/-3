# db_manager.py — Глобальный экземпляр БД и удобные методы-обёртки
# Все методы работают со словарями (dict), не кортежами!

import logging
from database import Database
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Глобальный экземпляр БД (инициализируется один раз)
db = Database(DATABASE_URL)


# ============================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================

def get_user(user_id: int):
    """Получить пользователя по ID. Возвращает dict или None."""
    return db.get_user(user_id)

def add_user(user_id: int, username: str):
    """Добавить пользователя если не существует."""
    db.add_user(user_id, username)

def update_user(user_id: int, **kwargs):
    """Обновить поля пользователя."""
    db.update_user(user_id, **kwargs)

def set_registration_complete(user_id: int):
    """Отметить регистрацию завершённой."""
    db.set_registration_complete(user_id)

def get_all_users():
    """Получить всех зарегистрированных пользователей."""
    return db.get_all_users()

def search_users(search_text: str):
    """Поиск пользователей по ФИО или username."""
    return db.search_users(search_text)

def find_user_by_username(username: str):
    """Найти пользователя по username."""
    return db.find_user_by_username(username)

def delete_user(user_id: int):
    """Полностью удалить пользователя и все его данные."""
    try:
        db.execute_query(
            "DELETE FROM aerodrome_phones WHERE aerodrome_id IN (SELECT id FROM aerodromes WHERE created_by = %s)",
            (user_id,)
        )
        db.execute_query(
            "DELETE FROM aerodrome_documents WHERE aerodrome_id IN (SELECT id FROM aerodromes WHERE created_by = %s)",
            (user_id,)
        )
        db.execute_query("DELETE FROM aerodromes WHERE created_by = %s", (user_id,))
        db.execute_query("DELETE FROM safety_blocks WHERE created_by = %s", (user_id,))
        db.execute_query("DELETE FROM admins WHERE user_id = %s", (user_id,))
        db.execute_query("DELETE FROM users WHERE user_id = %s", (user_id,))
        logger.info(f"✅ Пользователь {user_id} удалён")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка удаления пользователя {user_id}: {e}")
        return False

def get_users_ready_to_fly():
    """Пользователи, у которых нет запретов на полёты."""
    from validators import check_flight_ban
    return [u for u in get_all_users() if not check_flight_ban(u)]

def get_users_cannot_fly():
    """Пользователи с запретами на полёты."""
    from validators import check_flight_ban
    return [u for u in get_all_users() if check_flight_ban(u)]


# ============================================================
# АДМИНЫ
# ============================================================

def check_admin_status(user_id: int, username: str = None):
    """Проверить является ли пользователь админом."""
    return db.check_admin_status(user_id, username)

def add_admin(user_id: int, username: str, added_by: int):
    """Добавить админа."""
    db.add_admin(user_id, username, added_by)

def remove_admin(user_id: int):
    """Удалить админа."""
    db.remove_admin(user_id)

def get_all_admins():
    """Получить всех админов."""
    return db.get_all_admins()


# ============================================================
# АЭРОДРОМЫ
# ============================================================

def get_aerodrome_by_id(aerodrome_id: int):
    """Аэродром по ID."""
    return db.get_aerodrome_by_id(aerodrome_id)

def get_aerodrome_by_search(search_text: str):
    """Найти аэродром по названию/городу (первый результат)."""
    return db.get_aerodrome_by_search(search_text)

def get_aerodromes_by_city(city_name: str):
    """Все аэродромы в городе."""
    query = """
        SELECT id, name, city, airport_name, housing_info
        FROM aerodromes
        WHERE LOWER(city) = LOWER(%s) OR LOWER(name) ILIKE %s
        ORDER BY airport_name, name
    """
    result = db.execute_query(query, (city_name, f'%{city_name}%'), fetch=True)
    return [dict(r) for r in result] if result else []

def get_all_aerodromes_list():
    """Список всех аэродромов."""
    return db.get_all_aerodromes_list()

def add_aerodrome(name: str, city: str, airport_name: str, housing_info: str, created_by: int):
    """Добавить аэродром."""
    return db.add_aerodrome(name, city, airport_name, housing_info, created_by)

def update_aerodrome(aerodrome_id: int, **kwargs):
    """Обновить аэродром."""
    db.update_aerodrome(aerodrome_id, **kwargs)

def delete_aerodrome(aerodrome_id: int):
    """Удалить аэродром."""
    db.delete_aerodrome(aerodrome_id)


# ============================================================
# ТЕЛЕФОНЫ АЭРОДРОМОВ
# ============================================================

def get_aerodrome_phones(aerodrome_id: int):
    """Телефоны аэродрома."""
    return db.get_aerodrome_phones(aerodrome_id)

def add_aerodrome_phone(aerodrome_id: int, phone_name: str, phone_number: str):
    """Добавить телефон."""
    db.add_aerodrome_phone(aerodrome_id, phone_name, phone_number)

def delete_aerodrome_phone(phone_id: int):
    """Удалить телефон."""
    db.delete_aerodrome_phone(phone_id)


# ============================================================
# ДОКУМЕНТЫ АЭРОДРОМОВ
# ============================================================

def get_aerodrome_documents(aerodrome_id: int):
    """Документы аэродрома."""
    return db.get_aerodrome_documents(aerodrome_id)

def add_aerodrome_document(aerodrome_id: int, doc_name: str, doc_type: str, file_id: str):
    """Добавить документ."""
    db.add_aerodrome_document(aerodrome_id, doc_name, doc_type, file_id)

def delete_aerodrome_document(doc_id: int):
    """Удалить документ."""
    db.delete_aerodrome_document(doc_id)


# ============================================================
# БЛОКИ БЕЗОПАСНОСТИ
# ============================================================

def get_safety_block_by_number(block_number: int):
    """Блок безопасности по номеру."""
    return db.get_safety_block_by_number(block_number)

def add_safety_block(block_number: int, block_text: str, created_by: int):
    """Добавить блок безопасности."""
    db.add_safety_block(block_number, block_text, created_by)

def get_all_safety_blocks():
    """Все блоки безопасности."""
    return db.get_all_safety_blocks()

def update_safety_block(block_number: int, block_text: str):
    """Обновить блок безопасности."""
    db.update_safety_block(block_number, block_text)

def delete_safety_block(block_number: int):
    """Удалить блок безопасности."""
    db.delete_safety_block(block_number)


# ============================================================
# ЗНАНИЯ О САМОЛЁТАХ
# ============================================================

def add_aircraft_knowledge(aircraft_type: str, knowledge_name: str, knowledge_text: str, file_id: str = None):
    """Добавить знание о самолёте."""
    db.add_aircraft_knowledge(aircraft_type, knowledge_name, knowledge_text, file_id)

def get_aircraft_knowledge_by_type(aircraft_type: str):
    """Знания по типу самолёта."""
    return db.get_aircraft_knowledge_by_type(aircraft_type)


# ============================================================
# БЛОКИРОВКА ИНСТАНСОВ (heartbeat)
# ============================================================

def check_lock_status():
    return db.check_lock_status()

def check_and_acquire_lock(instance_id: str):
    return db.check_and_acquire_lock(instance_id)

def update_heartbeat(instance_id: str):
    db.update_heartbeat(instance_id)

def release_lock(instance_id: str):
    db.release_lock(instance_id)
