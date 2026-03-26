#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗄️ database.py — Подключение к PostgreSQL (Neon.tech) и работа с базой данных
✅ Все методы возвращают dict (словари), не кортежи!
✅ Поддержка connection pooling для производительности
✅ Безопасная инициализация без crash при ошибке подключения
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных PostgreSQL"""
    
    def __init__(self, db_url: str):
        """
        Инициализация пула подключений к базе данных.
        
        Args:
            db_url: Строка подключения к PostgreSQL (Neon.tech)
        """
        try:
            self.db_url = db_url
            
            # Создаём пул подключений для Neon.tech
            # ✅ connect_timeout=10 — защита от зависаний
            # ✅ cursor_factory=RealDictCursor — результаты как dict
            self.db_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=db_url,
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
            
            if self.db_pool:
                logger.info("✅ PostgreSQL подключена успешно!")
                self.create_tables()
                
        except psycopg2.OperationalError as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка инициализации БД: {e}")
            raise

    def get_connection(self):
        """Получить подключение из пула"""
        return self.db_pool.getconn()

    def release_connection(self, conn):
        """Вернуть подключение в пул"""
        self.db_pool.putconn(conn)

    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """
        Выполнить SQL-запрос.
        
        Args:
            query: SQL-запрос с плейсхолдерами %s
            params: Кортеж параметров для подстановки
            fetch: Если True — вернуть результаты (fetchall)
            
        Returns:
            list[dict] если fetch=True и есть результаты, иначе None
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                
                if fetch:
                    result = cursor.fetchall()
                else:
                    result = None
                    
                conn.commit()
                return result
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Ошибка выполнения запроса: {e}")
            logger.error(f"   Query: {query[:200]}...")
            raise
            
        finally:
            self.release_connection(conn)

    def create_tables(self):
        """Создать все таблицы если они не существуют"""
        
        # ==================== ПОЛЬЗОВАТЕЛИ ====================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fio TEXT,
                rank TEXT,
                qualification TEXT,
                leave_start_date TEXT,
                leave_end_date TEXT,
                vlk_date TEXT,
                umo_date TEXT,
                exercise_4_md_m_date TEXT,
                exercise_7_md_m_date TEXT,
                exercise_4_md_90a_date TEXT,
                exercise_7_md_90a_date TEXT,
                parachute_jump_date TEXT,
                is_registered BOOLEAN DEFAULT FALSE
            )
        """)
        
        # ==================== АДМИНЫ ====================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE,
                username TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                added_by BIGINT
            )
        """)
        
        # ==================== БЛОКИРОВКИ ИНСТАНСОВ ====================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS instance_lock (
                id SERIAL PRIMARY KEY,
                instance_id TEXT UNIQUE,
                heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ==================== АЭРОДРОМЫ ====================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS aerodromes (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT,
                airport_name TEXT,
                housing_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by BIGINT
            )
        """)
        
        # ==================== ТЕЛЕФОНЫ АЭРОДРОМОВ ====================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS aerodrome_phones (
                id SERIAL PRIMARY KEY,
                aerodrome_id INTEGER REFERENCES aerodromes(id) ON DELETE CASCADE,
                phone_name TEXT,
                phone_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ==================== ДОКУМЕНТЫ АЭРОДРОМОВ ====================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS aerodrome_documents (
                id SERIAL PRIMARY KEY,
                aerodrome_id INTEGER REFERENCES aerodromes(id) ON DELETE CASCADE,
                doc_name TEXT,
                doc_type TEXT,
                file_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ==================== БЛОКИ БЕЗОПАСНОСТИ ====================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS safety_blocks (
                id SERIAL PRIMARY KEY,
                block_number INTEGER UNIQUE NOT NULL,
                block_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by BIGINT
            )
        """)
        
        # ==================== ЗНАНИЯ О САМОЛЁТАХ ====================
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS aircraft_knowledge (
                id SERIAL PRIMARY KEY,
                aircraft_type TEXT NOT NULL,
                knowledge_name TEXT,
                knowledge_text TEXT,
                file_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("✅ Все таблицы созданы/проверены")

    # ============================================================
    # 👤 ПОЛЬЗОВАТЕЛИ
    # ============================================================

    def add_user(self, user_id: int, username: str) -> None:
        """Добавить пользователя если не существует"""
        self.execute_query(
            "INSERT INTO users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING",
            (user_id, username)
        )

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Обновить поля пользователя.
        
        Args:
            user_id: Telegram ID пользователя
            **kwargs: Поля для обновления (только из allowed_fields)
        """
        if not kwargs:
            return
            
        # Whitelist допустимых полей для защиты от SQL-инъекций
        allowed_fields = {
            'username', 'fio', 'rank', 'qualification',
            'leave_start_date', 'leave_end_date', 'vlk_date', 'umo_date',
            'exercise_4_md_m_date', 'exercise_7_md_m_date',
            'exercise_4_md_90a_date', 'exercise_7_md_90a_date',
            'parachute_jump_date', 'is_registered'
        }
        
        filtered = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not filtered:
            return
            
        set_clause = ", ".join([f"{key} = %s" for key in filtered.keys()])
        values = list(filtered.values()) + [user_id]
        query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
        self.execute_query(query, tuple(values))

    def get_user(self, user_id: int) -> dict | None:
        """
        Получить пользователя по Telegram ID.
        
        Returns:
            dict с данными пользователя или None
        """
        result = self.execute_query(
            "SELECT * FROM users WHERE user_id = %s",
            (user_id,),
            fetch=True
        )
        if result:
            return dict(result[0])
        return None

    def get_all_users(self) -> list[dict]:
        """Получить всех зарегистрированных пользователей"""
        result = self.execute_query(
            "SELECT * FROM users WHERE is_registered = TRUE ORDER BY fio ASC",
            fetch=True
        )
        return [dict(r) for r in result] if result else []

    def search_users(self, search_text: str) -> list[dict]:
        """
        Поиск пользователей по ФИО или username.
        
        Args:
            search_text: Текст для поиска
            
        Returns:
            Список пользователей (dict)
        """
        search_text = search_text.strip()
        if not search_text:
            return []
            
        result = self.execute_query(
            """SELECT * FROM users WHERE is_registered = TRUE
               AND (LOWER(fio) ILIKE %s OR LOWER(username) ILIKE %s)
               ORDER BY fio ASC""",
            (f"%{search_text.lower()}%", f"%{search_text.lower()}%"),
            fetch=True
        )
        return [dict(r) for r in result] if result else []

    def set_registration_complete(self, user_id: int) -> None:
        """Отметить регистрацию пользователя завершённой"""
        self.execute_query(
            "UPDATE users SET is_registered = TRUE WHERE user_id = %s",
            (user_id,)
        )

    def find_user_by_username(self, username: str) -> dict | None:
        """Найти пользователя по username (частичное совпадение)"""
        username_clean = username.lstrip('@')
        result = self.execute_query(
            "SELECT user_id, username FROM users WHERE username ILIKE %s",
            (f"%{username_clean}%",),
            fetch=True
        )
        return dict(result[0]) if result else None

    # ============================================================
    # 👮 АДМИНЫ
    # ============================================================

    def check_admin_status(self, user_id: int, username: str = None) -> bool:
        """
        Проверить является ли пользователь админом.
        
        Args:
            user_id: Telegram ID
            username: Username пользователя (опционально)
            
        Returns:
            True если админ, иначе False
        """
        from config import ADMIN_IDS, ADMIN_USERNAMES
        
        # Проверка по ID из config
        if user_id in ADMIN_IDS:
            return True
            
        # Проверка по username из config
        if username:
            username_clean = username.lstrip('@').lower()
            if username_clean in [u.lower() for u in ADMIN_USERNAMES]:
                return True
                
        # Проверка в БД по user_id
        result = self.execute_query(
            "SELECT user_id FROM admins WHERE user_id = %s",
            (user_id,), fetch=True
        )
        if result:
            return True
            
        # Проверка в БД по username
        if username:
            username_clean = username.lstrip('@')
            result = self.execute_query(
                "SELECT user_id FROM admins WHERE username ILIKE %s",
                (username_clean,), fetch=True
            )
            if result:
                return True
                
        return False

    def add_admin(self, user_id: int, username: str, added_by: int) -> None:
        """Добавить пользователя в админы"""
        username_clean = username.lstrip('@') if username else None
        self.execute_query(
            """INSERT INTO admins (user_id, username, added_by)
               VALUES (%s, %s, %s)
               ON CONFLICT (user_id) DO UPDATE SET username = %s""",
            (user_id, username_clean, added_by, username_clean)
        )

    def remove_admin(self, user_id: int) -> None:
        """Удалить пользователя из админов"""
        self.execute_query("DELETE FROM admins WHERE user_id = %s", (user_id,))

    def get_all_admins(self) -> list[dict]:
        """Получить всех админов из БД"""
        result = self.execute_query("SELECT * FROM admins", fetch=True)
        return [dict(r) for r in result] if result else []

    # ============================================================
    # 🔒 БЛОКИРОВКА ИНСТАНСОВ (heartbeat)
    # ============================================================

    def check_lock_status(self) -> dict | None:
        """Проверить текущий статус блокировки"""
        result = self.execute_query(
            "SELECT instance_id, heartbeat FROM instance_lock WHERE id = 1",
            fetch=True
        )
        return dict(result[0]) if result else None

    def check_and_acquire_lock(self, instance_id: str) -> bool:
        """
        Попытаться захватить блокировку для экземпляра бота.
        
        Args:
            instance_id: Уникальный идентификатор экземпляра
            
        Returns:
            True если блокировка захвачена, иначе False
        """
        existing = self.execute_query(
            "SELECT instance_id, heartbeat FROM instance_lock WHERE id = 1",
            fetch=True
        )
        now = datetime.now()
        
        if not existing:
            # Блокировка свободна — захватываем
            self.execute_query(
                "INSERT INTO instance_lock (id, instance_id, heartbeat) VALUES (1, %s, %s)",
                (instance_id, now)
            )
            return True
        else:
            # Проверяем время последнего heartbeat
            last_heartbeat = existing[0]['heartbeat']
            if (now - last_heartbeat).total_seconds() > 60:
                # Предыдущий экземпляр "умер" — перехватываем блокировку
                self.execute_query(
                    "UPDATE instance_lock SET instance_id = %s, heartbeat = %s WHERE id = 1",
                    (instance_id, now)
                )
                return True
            return False

    def update_heartbeat(self, instance_id: str) -> None:
        """Обновить heartbeat для активного экземпляра"""
        self.execute_query(
            "UPDATE instance_lock SET heartbeat = %s WHERE instance_id = %s AND id = 1",
            (datetime.now(), instance_id)
        )

    def release_lock(self, instance_id: str) -> None:
        """Освободить блокировку при корректной остановке"""
        self.execute_query(
            "DELETE FROM instance_lock WHERE instance_id = %s AND id = 1",
            (instance_id,)
        )

    # ============================================================
    # ✈️ АЭРОДРОМЫ
    # ============================================================

    def get_aerodrome_by_search(self, search_text: str) -> dict | None:
        """
        Найти аэродром по названию/городу (первый результат).
        
        Args:
            search_text: Текст для поиска
            
        Returns:
            dict с данными аэродрома или None
        """
        search_text = search_text.strip()
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM aerodromes
                       WHERE name ILIKE %s OR city ILIKE %s OR airport_name ILIKE %s
                       LIMIT 1""",
                    (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%")
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"❌ Ошибка поиска аэродрома: {e}")
            return None
        finally:
            self.release_connection(conn)

    def search_aerodromes(self, keyword: str) -> list[dict]:
        """
        Поиск аэродромов по ключевому слову (до 10 результатов).
        
        Args:
            keyword: Ключевое слово для поиска
            
        Returns:
            Список аэродромов (dict)
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT id, name, city, airport_name FROM aerodromes
                       WHERE name ILIKE %s OR city ILIKE %s OR airport_name ILIKE %s
                       LIMIT 10""",
                    (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
                )
                results = cursor.fetchall()
                return [dict(r) for r in results]
        except Exception as e:
            logger.error(f"❌ Ошибка поиска аэродромов: {e}")
            return []
        finally:
            self.release_connection(conn)

    def add_aerodrome(self, name: str, city: str, airport_name: str, 
                      housing_info: str, created_by: int) -> int | None:
        """
        Добавить новый аэродром.
        
        Returns:
            ID нового аэродрома или None при ошибке
        """
        result = self.execute_query(
            """INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (name, city, airport_name, housing_info, created_by),
            fetch=True
        )
        return result[0]['id'] if result else None

    def get_aerodrome_by_id(self, aerodrome_id: int) -> dict | None:
        """Получить аэродром по ID"""
        result = self.execute_query(
            "SELECT * FROM aerodromes WHERE id = %s",
            (aerodrome_id,), fetch=True
        )
        return dict(result[0]) if result else None

    def get_all_aerodromes_list(self) -> list[dict]:
        """Получить список всех аэродромов"""
        result = self.execute_query(
            "SELECT * FROM aerodromes ORDER BY name", fetch=True
        )
        return [dict(r) for r in result] if result else []

    def update_aerodrome(self, aerodrome_id: int, **kwargs) -> None:
        """Обновить данные аэродрома"""
        allowed_fields = {'name', 'city', 'airport_name', 'housing_info'}
        filtered = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not filtered:
            return
        set_clause = ", ".join([f"{key} = %s" for key in filtered.keys()])
        values = list(filtered.values()) + [aerodrome_id]
        self.execute_query(f"UPDATE aerodromes SET {set_clause} WHERE id = %s", tuple(values))

    def delete_aerodrome(self, aerodrome_id: int) -> None:
        """Удалить аэродром (CASCADE удалит телефоны и документы)"""
        self.execute_query("DELETE FROM aerodromes WHERE id = %s", (aerodrome_id,))

    # ============================================================
    # 📞 ТЕЛЕФОНЫ АЭРОДРОМОВ
    # ============================================================

    def get_aerodrome_phones(self, aerodrome_id: int) -> list[dict]:
        """Получить все телефоны аэродрома"""
        result = self.execute_query(
            "SELECT * FROM aerodrome_phones WHERE aerodrome_id = %s ORDER BY phone_name",
            (aerodrome_id,), fetch=True
        )
        return [dict(r) for r in result] if result else []

    def add_aerodrome_phone(self, aerodrome_id: int, phone_name: str, phone_number: str) -> None:
        """Добавить телефон для аэродрома"""
        self.execute_query(
            "INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number) VALUES (%s, %s, %s)",
            (aerodrome_id, phone_name, phone_number)
        )

    def delete_aerodrome_phone(self, phone_id: int) -> None:
        """Удалить телефон по ID"""
        self.execute_query("DELETE FROM aerodrome_phones WHERE id = %s", (phone_id,))

    # ============================================================
    # 📄 ДОКУМЕНТЫ АЭРОДРОМОВ
    # ============================================================

    def get_aerodrome_documents(self, aerodrome_id: int) -> list[dict]:
        """Получить все документы аэродрома"""
        result = self.execute_query(
            "SELECT * FROM aerodrome_documents WHERE aerodrome_id = %s",
            (aerodrome_id,), fetch=True
        )
        return [dict(r) for r in result] if result else []

    def add_aerodrome_document(self, aerodrome_id: int, doc_name: str, 
                               doc_type: str, file_id: str) -> None:
        """Добавить документ для аэродрома"""
        self.execute_query(
            "INSERT INTO aerodrome_documents (aerodrome_id, doc_name, doc_type, file_id) VALUES (%s, %s, %s, %s)",
            (aerodrome_id, doc_name, doc_type, file_id)
        )

    def delete_aerodrome_document(self, doc_id: int) -> None:
        """Удалить документ по ID"""
        self.execute_query("DELETE FROM aerodrome_documents WHERE id = %s", (doc_id,))

    # ============================================================
    # 🛡️ БЛОКИ БЕЗОПАСНОСТИ
    # ============================================================

    def add_safety_block(self, block_number: int, block_text: str, created_by: int) -> None:
        """Добавить блок безопасности"""
        self.execute_query(
            "INSERT INTO safety_blocks (block_number, block_text, created_by) VALUES (%s, %s, %s)",
            (block_number, block_text, created_by)
        )

    def get_safety_block_by_number(self, block_number: int) -> dict | None:
        """Получить блок безопасности по номеру"""
        result = self.execute_query(
            "SELECT * FROM safety_blocks WHERE block_number = %s",
            (block_number,), fetch=True
        )
        return dict(result[0]) if result else None

    def get_all_safety_blocks(self) -> list[dict]:
        """Получить все блоки безопасности"""
        result = self.execute_query(
            "SELECT * FROM safety_blocks ORDER BY block_number", fetch=True
        )
        return [dict(r) for r in result] if result else []

    def update_safety_block(self, block_number: int, block_text: str) -> None:
        """Обновить текст блока безопасности"""
        self.execute_query(
            "UPDATE safety_blocks SET block_text = %s WHERE block_number = %s",
            (block_text, block_number)
        )

    def delete_safety_block(self, block_number: int) -> None:
        """Удалить блок безопасности"""
        self.execute_query("DELETE FROM safety_blocks WHERE block_number = %s", (block_number,))

    # ============================================================
    # ✈️ ЗНАНИЯ О САМОЛЁТАХ
    # ============================================================

    def add_aircraft_knowledge(self, aircraft_type: str, knowledge_name: str, 
                               knowledge_text: str, file_id: str = None) -> None:
        """Добавить знание о самолёте"""
        self.execute_query(
            "INSERT INTO aircraft_knowledge (aircraft_type, knowledge_name, knowledge_text, file_id) VALUES (%s, %s, %s, %s)",
            (aircraft_type, knowledge_name, knowledge_text, file_id)
        )

    def get_aircraft_knowledge_by_type(self, aircraft_type: str) -> list[dict]:
        """Получить знания по типу самолёта"""
        result = self.execute_query(
            "SELECT * FROM aircraft_knowledge WHERE aircraft_type = %s",
            (aircraft_type,), fetch=True
        )
        return [dict(r) for r in result] if result else []

    def delete_aircraft_knowledge(self, knowledge_id: int) -> None:
        """Удалить знание по ID"""
        self.execute_query("DELETE FROM aircraft_knowledge WHERE id = %s", (knowledge_id,))

    # ============================================================
    # 🔧 УТИЛИТЫ
    # ============================================================

    def close(self) -> None:
        """Закрыть все подключения в пуле"""
        if self.db_pool:
            self.db_pool.closeall()
            logger.info("🔌 PostgreSQL отключена")


# ============================================================
# 🌍 ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР БАЗЫ ДАННЫХ
# ============================================================

from config import DATABASE_URL

db: Database | None = None

try:
    if DATABASE_URL:
        db = Database(DATABASE_URL)
        logger.info("✅ Глобальный экземпляр БД инициализирован")
    else:
        logger.warning("⚠️ DATABASE_URL не задан — БД не инициализирована")
        
except Exception as e:
    # ❌ НЕ выбрасываем исключение — бот должен запуститься даже без БД
    logger.error(f"❌ Не удалось инициализировать базу данных: {e}")
    logger.warning("⚠️ Бот запустится в ограниченном режиме (без доступа к БД)")
    db = None
