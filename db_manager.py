# db_manager.py - Глобальный экземпляр базы данных и методы для работы с ней
import logging
from database import Database
from config import DATABASE_URL

logger = logging.getLogger(__name__)

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
    return db.execute_query(query, (city_name, f'%{city_name}%'), fetch=True)

def get_aerodrome_by_id(aerodrome_id: int):
    """Вернуть аэродром по ID"""
    query = """
        SELECT id, name, city, airport_name, housing_info
        FROM aerodromes
        WHERE id = %s
    """
    result = db.execute_query(query, (aerodrome_id,), fetch=True)
    return result[0] if result else None

def get_aerodrome_phones(aerodrome_id: int):
    """Вернуть все телефоны аэродрома (ОБЯЗАТЕЛЬНО с id!)"""
    query = """
        SELECT id, phone_name, phone_number
        FROM aerodrome_phones
        WHERE aerodrome_id = %s
        ORDER BY phone_name
    """
    result = db.execute_query(query, (aerodrome_id,), fetch=True)
    return result if result else []

def get_aerodrome_documents(aerodrome_id: int):
    """Вернуть все документы аэродрома"""
    query = """
        SELECT id, doc_name, doc_type, file_id
        FROM aerodrome_documents
        WHERE aerodrome_id = %s
        ORDER BY doc_name
    """
    return db.execute_query(query, (aerodrome_id,), fetch=True)

def add_aerodrome_phone(aerodrome_id: int, phone_name: str, phone_number: str):
    """Добавить телефон аэродрома"""
    query = """
        INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
        VALUES (%s, %s, %s)
    """
    db.execute_query(query, (aerodrome_id, phone_name, phone_number))

def delete_aerodrome_phone(phone_id: int):
    """Удалить телефон аэродрома"""
    query = """
        DELETE FROM aerodrome_phones WHERE id = %s
    """
    db.execute_query(query, (phone_id,))

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
    result = db.execute_query(query, (search_pattern, search_pattern, search_pattern), fetch=True)
    return result[0] if result else None

def add_aerodrome(name: str, city: str, airport_name: str, housing_info: str, created_by: int):
    """Добавить аэродром"""
    query = """
        INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    result = db.execute_query(query, (name, city, airport_name, housing_info, created_by), fetch=True)
    return result[0]['id'] if result else None

def update_aerodrome(aerodrome_id: int, **kwargs):
    """Обновить информацию об аэродроме"""
    set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
    values = list(kwargs.values()) + [aerodrome_id]
    query = f"UPDATE aerodromes SET {set_clause} WHERE id = %s"
    db.execute_query(query, tuple(values))

def get_all_aerodromes_list():
    """Получить список всех аэродромов"""
    query = """
        SELECT id, name, city, airport_name, housing_info
        FROM aerodromes
        ORDER BY name, airport_name
    """
    return db.execute_query(query, fetch=True)

# ============================================================
# МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ
# ============================================================

def get_all_users():
    """Получить всех зарегистрированных пользователей"""
    query = """
        SELECT user_id, username, registered_at, fio, rank, qualification,
               leave_start_date, leave_end_date, vlk_date, umo_date,
               exercise_4_md_m_date, exercise_7_md_m_date,
               exercise_4_md_90a_date, exercise_7_md_90a_date,
               parachute_jump_date, is_registered
        FROM users
        WHERE is_registered = TRUE
        ORDER BY fio ASC
    """
    return db.execute_query(query, fetch=True)

def search_users(search_text: str):
    """Поиск пользователей по ФИО или username"""
    search_text = search_text.strip().lower()
    if not search_text:
        return []
    
    query = """
        SELECT user_id, username, registered_at, fio, rank, qualification,
               leave_start_date, leave_end_date, vlk_date, umo_date,
               exercise_4_md_m_date, exercise_7_md_m_date,
               exercise_4_md_90a_date, exercise_7_md_90a_date,
               parachute_jump_date, is_registered
        FROM users
        WHERE is_registered = TRUE
          AND (LOWER(fio) ILIKE %s OR LOWER(username) ILIKE %s)
        ORDER BY fio ASC
    """
    return db.execute_query(query, (f"%{search_text}%", f"%{search_text}%"), fetch=True)

def get_users_ready_to_fly():
    """Получить пользователей готовых к полётам"""
    all_users = get_all_users()
    ready_users = []
    
    for user in all_users:
        from validators import check_flight_ban
        bans = check_flight_ban(user)
        if not bans:
            ready_users.append(user)
    
    return ready_users

def get_users_cannot_fly():
    """Получить пользователей кто не может летать"""
    all_users = get_all_users()
    cannot_fly_users = []
    
    for user in all_users:
        from validators import check_flight_ban
        bans = check_flight_ban(user)
        if bans:
            cannot_fly_users.append(user)
    
    return cannot_fly_users

def find_user_by_username(username: str):
    """Найти пользователя по username"""
    username_clean = username.lstrip('@')
    query = """
        SELECT user_id, username FROM users
        WHERE username ILIKE %s
    """
    result = db.execute_query(query, (f"%{username_clean}%",), fetch=True)
    return result[0] if result else None

def delete_user(user_id: int):
    """✅ Полностью удалить пользователя из базы данных"""
    try:
        # Сначала удаляем связанные записи (чтобы не было ошибок FK)
        # Удаляем аэродромы созданные пользователем
        db.execute_query("DELETE FROM aerodrome_phones WHERE aerodrome_id IN (SELECT id FROM aerodromes WHERE created_by = %s)", (user_id,))
        db.execute_query("DELETE FROM aerodrome_documents WHERE aerodrome_id IN (SELECT id FROM aerodromes WHERE created_by = %s)", (user_id,))
        db.execute_query("DELETE FROM aerodromes WHERE created_by = %s", (user_id,))
        
        # Удаляем блоки безопасности созданные пользователем
        db.execute_query("DELETE FROM safety_blocks WHERE created_by = %s", (user_id,))
        
        # Удаляем из админов
        db.execute_query("DELETE FROM admins WHERE user_id = %s", (user_id,))
        
        # Удаляем пользователя
        query = "DELETE FROM users WHERE user_id = %s"
        db.execute_query(query, (user_id,))
        
        logger.info(f"✅ Пользователь {user_id} полностью удалён из БД")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка при удалении пользователя {user_id}: {e}")
        return False
# ============================================================
# МЕТОДЫ ДЛЯ РАБОТЫ С АДМИНАМИ
# ============================================================

def check_admin_status(user_id: int, username: str = None):
    """Проверить статус админа"""
    from config import ADMIN_IDS, ADMIN_USERNAMES
    
    if user_id in ADMIN_IDS:
        return True
    
    if username:
        username_clean = username.lstrip('@').lower()
        if username_clean in [u.lower() for u in ADMIN_USERNAMES]:
            return True
    
    result = db.execute_query(
        "SELECT user_id FROM admins WHERE user_id = %s",
        (user_id,),
        fetch=True
    )
    if result:
        return True
    
    if username:
        username_clean = username.lstrip('@')
        result = db.execute_query(
            "SELECT user_id FROM admins WHERE username ILIKE %s",
            (username_clean,),
            fetch=True
        )
        if result:
            return True
    
    return False

def add_admin(user_id: int, username: str, added_by: int):
    """Добавить админа"""
    username_clean = username.lstrip('@') if username else None
    query = """
        INSERT INTO admins (user_id, username, added_by)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET username = %s
    """
    db.execute_query(query, (user_id, username_clean, added_by, username_clean))

def remove_admin(user_id: int):
    """Удалить админа"""
    query = "DELETE FROM admins WHERE user_id = %s"
    db.execute_query(query, (user_id,))

def get_all_admins():
    """Получить всех админов из БД"""
    query = "SELECT * FROM admins"
    return db.execute_query(query, fetch=True)

# ============================================================
# МЕТОДЫ ДЛЯ РАБОТЫ С БЛОКАМИ БЕЗОПАСНОСТИ
# ============================================================

def get_safety_block_by_number(block_number: int):
    """Вернуть блок безопасности по номеру"""
    query = """
        SELECT block_number, block_text
        FROM safety_blocks
        WHERE block_number = %s
    """
    result = db.execute_query(query, (block_number,), fetch=True)
    return result[0] if result else None

def add_safety_block(block_number: int, block_text: str, created_by: int):
    """Добавить блок безопасности"""
    query = """
        INSERT INTO safety_blocks (block_number, block_text, created_by)
        VALUES (%s, %s, %s)
    """
    db.execute_query(query, (block_number, block_text, created_by))

def get_all_safety_blocks():
    """Получить все блоки безопасности"""
    query = "SELECT * FROM safety_blocks ORDER BY block_number"
    return db.execute_query(query, fetch=True)

# ============================================================
# МЕТОДЫ ДЛЯ РАБОТЫ С ЗНАНИЯМИ ПО САМОЛЁТАМ
# ============================================================

def add_aircraft_knowledge(aircraft_type: str, knowledge_name: str, knowledge_text: str, file_id: str = None):
    """Добавить знание по самолёту"""
    query = """
        INSERT INTO aircraft_knowledge (aircraft_type, knowledge_name, knowledge_text, file_id)
        VALUES (%s, %s, %s, %s)
    """
    db.execute_query(query, (aircraft_type, knowledge_name, knowledge_text, file_id))

def get_aircraft_knowledge_by_type(aircraft_type: str):
    """Получить знания по типу самолёта"""
    query = """
        SELECT * FROM aircraft_knowledge
        WHERE aircraft_type = %s
    """
    return db.execute_query(query, (aircraft_type,), fetch=True)

# ============================================================
# МЕТОДЫ ДЛЯ РАБОТЫ С БЛОКИРОВКОЙ (HEARTBEAT)
# ============================================================

def check_lock_status():
    """Проверить статус блокировки"""
    query = "SELECT instance_id, heartbeat FROM instance_lock WHERE id = 1"
    result = db.execute_query(query, fetch=True)
    return result[0] if result else None

def check_and_acquire_lock(instance_id: str):
    """Проверить и захватить блокировку"""
    from datetime import datetime
    
    existing = db.execute_query(
        "SELECT instance_id, heartbeat FROM instance_lock WHERE id = 1",
        fetch=True
    )
    
    now = datetime.now()
    
    if not existing:
        db.execute_query(
            "INSERT INTO instance_lock (id, instance_id, heartbeat) VALUES (1, %s, %s)",
            (instance_id, now)
        )
        return True
    else:
        last_heartbeat = existing[0]['heartbeat']
        if (now - last_heartbeat).total_seconds() > 60:
            db.execute_query(
                "UPDATE instance_lock SET instance_id = %s, heartbeat = %s WHERE id = 1",
                (instance_id, now)
            )
            return True
        else:
            return False

def update_heartbeat(instance_id: str):
    """Обновить heartbeat"""
    from datetime import datetime
    
    query = "UPDATE instance_lock SET heartbeat = %s WHERE instance_id = %s AND id = 1"
    db.execute_query(query, (datetime.now(), instance_id))

def release_lock(instance_id: str):
    """Освободить блокировку"""
    query = "DELETE FROM instance_lock WHERE instance_id = %s AND id = 1"
    db.execute_query(query, (instance_id,))
