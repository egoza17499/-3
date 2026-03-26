#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗄️ db_manager.py — Глобальный экземпляр БД и удобные методы-обёртки
✅ Все методы работают со словарями (dict), не кортежами!
✅ Централизованное управление подключениями к PostgreSQL
"""

import logging
from database import Database
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# ============================================================
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР БАЗЫ ДАННЫХ
# ============================================================

# Инициализируется один раз при импорте модуля
db = Database(DATABASE_URL)


# ============================================================
# 👤 ПОЛЬЗОВАТЕЛИ
# ============================================================

def get_user(user_id: int) -> dict | None:
    """
    Получить пользователя по Telegram ID.
    
    Args:
        user_id: Telegram ID пользователя
        
    Returns:
        dict с данными пользователя или None если не найден
    """
    return db.get_user(user_id)


def add_user(user_id: int, username: str) -> None:
    """
    Добавить нового пользователя если не существует.
    
    Args:
        user_id: Telegram ID
        username: Username пользователя
    """
    db.add_user(user_id, username)


def update_user(user_id: int, **kwargs) -> None:
    """
    Обновить поля пользователя.
    
    Args:
        user_id: Telegram ID
        **kwargs: Поля для обновления (fio, rank, qualification, и т.д.)
    """
    db.update_user(user_id, **kwargs)


def set_registration_complete(user_id: int) -> None:
    """
    Отметить регистрацию пользователя завершённой.
    
    Args:
        user_id: Telegram ID пользователя
    """
    db.set_registration_complete(user_id)


def get_all_users() -> list[dict]:
    """
    Получить всех зарегистрированных пользователей.
    
    Returns:
        Список словарей с данными пользователей
    """
    return db.get_all_users()


def search_users(search_text: str) -> list[dict]:
    """
    Поиск пользователей по ФИО или username.
    
    Args:
        search_text: Текст для поиска
        
    Returns:
        Список найденных пользователей (dict)
    """
    return db.search_users(search_text)


def find_user_by_username(username: str) -> dict | None:
    """
    Найти пользователя по username (частичное совпадение).
    
    Args:
        username: Username пользователя (с @ или без)
        
    Returns:
        dict с данными пользователя или None
    """
    return db.find_user_by_username(username)


def delete_user(user_id: int) -> bool:
    """
    Полностью удалить пользователя и все связанные данные.
    
    ⚠️ Каскадное удаление:
    - Телефоны аэродромов созданных пользователем
    - Документы аэродромов созданных пользователем
    - Аэродромы созданные пользователем
    - Блоки безопасности созданные пользователем
    - Запись в таблице admins
    - Запись в таблице users
    
    Args:
        user_id: Telegram ID пользователя
        
    Returns:
        bool: True если удалено успешно, иначе False
    """
    try:
        # Удаляем связанные данные каскадно
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
        db.execute_query("DELETE FROM aircraft_knowledge WHERE created_by = %s", (user_id,))
        db.execute_query("DELETE FROM admins WHERE user_id = %s", (user_id,))
        db.execute_query("DELETE FROM users WHERE user_id = %s", (user_id,))
        
        logger.info(f"✅ Пользователь {user_id} полностью удалён")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка удаления пользователя {user_id}: {e}")
        return False


def get_users_ready_to_fly() -> list[dict]:
    """
    Получить пользователей, у которых нет запретов на полёты.
    
    Returns:
        Список пользователей готовых к полётам
    """
    from validators import check_flight_ban
    return [u for u in get_all_users() if not check_flight_ban(u)]


def get_users_cannot_fly() -> list[dict]:
    """
    Получить пользователей с запретами на полёты.
    
    Returns:
        Список пользователей с запретами
    """
    from validators import check_flight_ban
    return [u for u in get_all_users() if check_flight_ban(u)]


# ============================================================
# 👮 АДМИНЫ
# ============================================================

def check_admin_status(user_id: int, username: str = None) -> bool:
    """
    Проверить является ли пользователь админом.
    
    Проверяет в трёх источниках:
    1. ADMIN_IDS из config.py
    2. ADMIN_USERNAMES из config.py
    3. Таблица admins в БД
    
    Args:
        user_id: Telegram ID пользователя
        username: Username пользователя (опционально)
        
    Returns:
        bool: True если админ, иначе False
    """
    return db.check_admin_status(user_id, username)


def add_admin(user_id: int, username: str, added_by: int) -> None:
    """
    Добавить пользователя в админы.
    
    Args:
        user_id: Telegram ID нового админа
        username: Username нового админа
        added_by: Telegram ID того кто добавил
    """
    db.add_admin(user_id, username, added_by)


def remove_admin(user_id: int) -> None:
    """
    Удалить пользователя из админов.
    
    Args:
        user_id: Telegram ID админа для удаления
    """
    db.remove_admin(user_id)


def get_all_admins() -> list[dict]:
    """
    Получить всех админов из базы данных.
    
    Returns:
        Список словарей с данными админов
    """
    return db.get_all_admins()


# ============================================================
# ✈️ АЭРОДРОМЫ
# ============================================================

def get_aerodrome_by_id(aerodrome_id: int) -> dict | None:
    """
    Получить аэродром по ID.
    
    Args:
        aerodrome_id: ID аэродрома в БД
        
    Returns:
        dict с данными аэродрома или None
    """
    return db.get_aerodrome_by_id(aerodrome_id)


def get_aerodrome_by_search(search_text: str) -> dict | None:
    """
    Найти аэродром по названию/городу (первый результат).
    
    Args:
        search_text: Текст для поиска
        
    Returns:
        dict с данными аэродрома или None
    """
    return db.get_aerodrome_by_search(search_text)


def get_aerodromes_by_city(city_name: str) -> list[dict]:
    """
    Получить все аэродромы в городе.
    
    Args:
        city_name: Название города
        
    Returns:
        Список аэродромов (dict) в этом городе
    """
    query = """
        SELECT id, name, city, airport_name, housing_info
        FROM aerodromes
        WHERE LOWER(city) = LOWER(%s) OR LOWER(name) ILIKE %s
        ORDER BY airport_name, name
    """
    result = db.execute_query(query, (city_name, f'%{city_name}%'), fetch=True)
    return [dict(r) for r in result] if result else []


def get_all_aerodromes_list() -> list[dict]:
    """
    Получить список всех аэродромов.
    
    Returns:
        Список всех аэродромов (dict)
    """
    return db.get_all_aerodromes_list()


def add_aerodrome(name: str, city: str, airport_name: str, 
                  housing_info: str, created_by: int) -> int | None:
    """
    Добавить новый аэродром.
    
    Args:
        name: Название аэродрома/города
        city: Город
        airport_name: Название аэропорта (опционально)
        housing_info: Информация о жилье
        created_by: Telegram ID создателя
        
    Returns:
        ID нового аэродрома или None при ошибке
    """
    return db.add_aerodrome(name, city, airport_name, housing_info, created_by)


def update_aerodrome(aerodrome_id: int, **kwargs) -> None:
    """
    Обновить данные аэродрома.
    
    Args:
        aerodrome_id: ID аэродрома
        **kwargs: Поля для обновления (name, city, airport_name, housing_info)
    """
    db.update_aerodrome(aerodrome_id, **kwargs)


def delete_aerodrome(aerodrome_id: int) -> None:
    """
    Удалить аэродром (каскадно удаляет телефоны и документы).
    
    Args:
        aerodrome_id: ID аэродрома для удаления
    """
    db.delete_aerodrome(aerodrome_id)


# ============================================================
# 📞 ТЕЛЕФОНЫ АЭРОДРОМОВ
# ============================================================

def get_aerodrome_phones(aerodrome_id: int) -> list[dict]:
    """
    Получить все телефоны аэродрома.
    
    Args:
        aerodrome_id: ID аэродрома
        
    Returns:
        Список телефонов (dict)
    """
    return db.get_aerodrome_phones(aerodrome_id)


def add_aerodrome_phone(aerodrome_id: int, phone_name: str, phone_number: str) -> None:
    """
    Добавить телефон для аэродрома.
    
    Args:
        aerodrome_id: ID аэродрома
        phone_name: Название телефона (АДП, Диспетчер, и т.д.)
        phone_number: Номер телефона
    """
    db.add_aerodrome_phone(aerodrome_id, phone_name, phone_number)


def delete_aerodrome_phone(phone_id: int) -> None:
    """
    Удалить телефон по ID.
    
    Args:
        phone_id: ID записи в таблице aerodrome_phones
    """
    db.delete_aerodrome_phone(phone_id)


# ============================================================
# 📄 ДОКУМЕНТЫ АЭРОДРОМОВ
# ============================================================

def get_aerodrome_documents(aerodrome_id: int) -> list[dict]:
    """
    Получить все документы аэродрома.
    
    Args:
        aerodrome_id: ID аэродрома
        
    Returns:
        Список документов (dict)
    """
    return db.get_aerodrome_documents(aerodrome_id)


def add_aerodrome_document(aerodrome_id: int, doc_name: str, 
                           doc_type: str, file_id: str) -> None:
    """
    Добавить документ для аэродрома.
    
    Args:
        aerodrome_id: ID аэродрома
        doc_name: Название документа
        doc_type: Тип документа
        file_id: ID файла в Telegram или путь на Яндекс Диске
    """
    db.add_aerodrome_document(aerodrome_id, doc_name, doc_type, file_id)


def delete_aerodrome_document(doc_id: int) -> None:
    """
    Удалить документ по ID.
    
    Args:
        doc_id: ID записи в таблице aerodrome_documents
    """
    db.delete_aerodrome_document(doc_id)


# ============================================================
# 🛡️ БЛОКИ БЕЗОПАСНОСТИ
# ============================================================

def get_safety_block_by_number(block_number: int) -> dict | None:
    """
    Получить блок безопасности по номеру.
    
    Args:
        block_number: Номер блока
        
    Returns:
        dict с данными блока или None
    """
    return db.get_safety_block_by_number(block_number)


def add_safety_block(block_number: int, block_text: str, created_by: int) -> None:
    """
    Добавить новый блок безопасности.
    
    Args:
        block_number: Номер блока (уникальный)
        block_text: Текст блока
        created_by: Telegram ID создателя
    """
    db.add_safety_block(block_number, block_text, created_by)


def get_all_safety_blocks() -> list[dict]:
    """
    Получить все блоки безопасности.
    
    Returns:
        Список всех блоков (dict)
    """
    return db.get_all_safety_blocks()


def update_safety_block(block_number: int, block_text: str) -> None:
    """
    Обновить текст блока безопасности.
    
    Args:
        block_number: Номер блока
        block_text: Новый текст блока
    """
    db.update_safety_block(block_number, block_text)


def delete_safety_block(block_number: int) -> None:
    """
    Удалить блок безопасности по номеру.
    
    Args:
        block_number: Номер блока для удаления
    """
    db.delete_safety_block(block_number)


# ============================================================
# ✈️ ЗНАНИЯ О САМОЛЁТАХ
# ============================================================

def add_aircraft_knowledge(aircraft_type: str, knowledge_name: str, 
                           knowledge_text: str, file_id: str = None) -> None:
    """
    Добавить знание о самолёте.
    
    Args:
        aircraft_type: Тип самолёта (Ил-76МД, Ил-76МД-М, Ил-76МД-90А)
        knowledge_name: Название материала
        knowledge_text: Текст материала (опционально)
        file_id: ID файла в Telegram или путь на Яндекс Диске (опционально)
    """
    db.add_aircraft_knowledge(aircraft_type, knowledge_name, knowledge_text, file_id)


def get_aircraft_knowledge_by_type(aircraft_type: str) -> list[dict]:
    """
    Получить знания по типу самолёта.
    
    Args:
        aircraft_type: Тип самолёта
        
    Returns:
        Список знаний (dict) для этого типа
    """
    return db.get_aircraft_knowledge_by_type(aircraft_type)


def delete_aircraft_knowledge(knowledge_id: int) -> bool:
    """
    ✅ Удалить знание о самолёте по ID.
    
    Args:
        knowledge_id: ID записи в таблице aircraft_knowledge
        
    Returns:
        bool: True если удалено успешно, иначе False
    """
    try:
        db.execute_query(
            "DELETE FROM aircraft_knowledge WHERE id = %s",
            (knowledge_id,)
        )
        logger.info(f"✅ Знание {knowledge_id} удалено")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка удаления знания {knowledge_id}: {e}")
        return False


# ============================================================
# 🔒 БЛОКИРОВКА ИНСТАНСОВ (heartbeat для Render)
# ============================================================

def check_lock_status() -> dict | None:
    """
    Проверить текущий статус блокировки экземпляра.
    
    Returns:
        dict с данными блокировки или None
    """
    return db.check_lock_status()


def check_and_acquire_lock(instance_id: str) -> bool:
    """
    Попытаться захватить блокировку для экземпляра бота.
    
    Предотвращает запуск нескольких копий бота одновременно.
    
    Args:
        instance_id: Уникальный идентификатор экземпляра
        
    Returns:
        bool: True если блокировка захвачена, иначе False
    """
    return db.check_and_acquire_lock(instance_id)


def update_heartbeat(instance_id: str) -> None:
    """
    Обновить heartbeat для активного экземпляра.
    
    Args:
        instance_id: ID экземпляра который обновляет heartbeat
    """
    db.update_heartbeat(instance_id)


def release_lock(instance_id: str) -> None:
    """
    Освободить блокировку при корректной остановке.
    
    Args:
        instance_id: ID экземпляра который освобождает блокировку
    """
    db.release_lock(instance_id)


# ============================================================
# 🔧 УТИЛИТЫ
# ============================================================

def close_db_connection() -> None:
    """
    Закрыть все подключения к базе данных.
    Вызывается при остановке бота.
    """
    if db:
        db.close()
        logger.info("🔌 Все подключения к БД закрыты")


# ============================================================
# 📦 ЭКСПОРТ ВСЕХ ФУНКЦИЙ
# ============================================================

__all__ = [
    # Глобальный экземпляр
    'db',
    
    # Пользователи
    'get_user', 'add_user', 'update_user', 'set_registration_complete',
    'get_all_users', 'search_users', 'find_user_by_username', 'delete_user',
    'get_users_ready_to_fly', 'get_users_cannot_fly',
    
    # Админы
    'check_admin_status', 'add_admin', 'remove_admin', 'get_all_admins',
    
    # Аэродромы
    'get_aerodrome_by_id', 'get_aerodrome_by_search', 'get_aerodromes_by_city',
    'get_all_aerodromes_list', 'add_aerodrome', 'update_aerodrome', 'delete_aerodrome',
    
    # Телефоны
    'get_aerodrome_phones', 'add_aerodrome_phone', 'delete_aerodrome_phone',
    
    # Документы
    'get_aerodrome_documents', 'add_aerodrome_document', 'delete_aerodrome_document',
    
    # Блоки безопасности
    'get_safety_block_by_number', 'add_safety_block', 'get_all_safety_blocks',
    'update_safety_block', 'delete_safety_block',
    
    # Знания о самолётах
    'add_aircraft_knowledge', 'get_aircraft_knowledge_by_type', 'delete_aircraft_knowledge',
    
    # Блокировка инстансов
    'check_lock_status', 'check_and_acquire_lock', 'update_heartbeat', 'release_lock',
    
    # Утилиты
    'close_db_connection',
]
