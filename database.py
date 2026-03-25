import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_url):
        try:
            # Neon.tech: убираем только ?options=... если есть, но сохраняем sslmode
            # Лучший способ — передать параметры явно
            self.db_url = db_url
            self.db_pool = pool.SimpleConnectionPool(
                1, 10,
                db_url,
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
            if self.db_pool:
                logger.info("✅ PostgreSQL подключена успешно!")
                self.create_tables()
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            raise

    def get_connection(self):
        return self.db_pool.getconn()

    def release_connection(self, conn):
        self.db_pool.putconn(conn)

    def execute_query(self, query, params=None, fetch=False):
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
            raise
        finally:
            self.release_connection(conn)

    def create_tables(self):
        """Создать все таблицы если они не существуют"""

        # Таблица пользователей
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

        # Таблица админов
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE,
                username TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                added_by BIGINT
            )
        """)

        # Таблица блокировок инстансов
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS instance_lock (
                id SERIAL PRIMARY KEY,
                instance_id TEXT UNIQUE,
                heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица аэродромов (CREATE IF NOT EXISTS — не трогает существующие данные!)
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

        # Таблица телефонов аэродромов
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS aerodrome_phones (
                id SERIAL PRIMARY KEY,
                aerodrome_id INTEGER REFERENCES aerodromes(id) ON DELETE CASCADE,
                phone_name TEXT,
                phone_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица документов аэродромов
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

        # Таблица блоков безопасности
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS safety_blocks (
                id SERIAL PRIMARY KEY,
                block_number INTEGER UNIQUE NOT NULL,
                block_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by BIGINT
            )
        """)

        # Таблица знаний о самолётах
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

    # ==================== ПОЛЬЗОВАТЕЛИ ====================

    def add_user(self, user_id: int, username: str):
        self.execute_query(
            "INSERT INTO users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING",
            (user_id, username)
        )

    def update_user(self, user_id: int, **kwargs):
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

    def get_user(self, user_id: int):
        """Получить пользователя по telegram_id — возвращает dict"""
        result = self.execute_query(
            "SELECT * FROM users WHERE user_id = %s",
            (user_id,),
            fetch=True
        )
        if result:
            return dict(result[0])
        return None

    def get_all_users(self):
        result = self.execute_query(
            "SELECT * FROM users WHERE is_registered = TRUE ORDER BY fio ASC",
            fetch=True
        )
        return [dict(r) for r in result] if result else []

    def search_users(self, search_text: str):
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

    def set_registration_complete(self, user_id: int):
        self.execute_query(
            "UPDATE users SET is_registered = TRUE WHERE user_id = %s",
            (user_id,)
        )

    def find_user_by_username(self, username: str):
        username_clean = username.lstrip('@')
        result = self.execute_query(
            "SELECT user_id, username FROM users WHERE username ILIKE %s",
            (f"%{username_clean}%",),
            fetch=True
        )
        return dict(result[0]) if result else None

    # ==================== АДМИНЫ ====================

    def check_admin_status(self, user_id: int, username: str = None):
        from config import ADMIN_IDS, ADMIN_USERNAMES
        if user_id in ADMIN_IDS:
            return True
        if username:
            username_clean = username.lstrip('@').lower()
            if username_clean in [u.lower() for u in ADMIN_USERNAMES]:
                return True
        result = self.execute_query(
            "SELECT user_id FROM admins WHERE user_id = %s",
            (user_id,), fetch=True
        )
        if result:
            return True
        if username:
            username_clean = username.lstrip('@')
            result = self.execute_query(
                "SELECT user_id FROM admins WHERE username ILIKE %s",
                (username_clean,), fetch=True
            )
            if result:
                return True
        return False

    def add_admin(self, user_id: int, username: str, added_by: int):
        username_clean = username.lstrip('@') if username else None
        self.execute_query(
            """INSERT INTO admins (user_id, username, added_by)
               VALUES (%s, %s, %s)
               ON CONFLICT (user_id) DO UPDATE SET username = %s""",
            (user_id, username_clean, added_by, username_clean)
        )

    def remove_admin(self, user_id: int):
        self.execute_query("DELETE FROM admins WHERE user_id = %s", (user_id,))

    def get_all_admins(self):
        result = self.execute_query("SELECT * FROM admins", fetch=True)
        return [dict(r) for r in result] if result else []

    # ==================== БЛОКИРОВКИ ====================

    def check_lock_status(self):
        result = self.execute_query(
            "SELECT instance_id, heartbeat FROM instance_lock WHERE id = 1",
            fetch=True
        )
        return dict(result[0]) if result else None

    def check_and_acquire_lock(self, instance_id: str):
        existing = self.execute_query(
            "SELECT instance_id, heartbeat FROM instance_lock WHERE id = 1",
            fetch=True
        )
        now = datetime.now()
        if not existing:
            self.execute_query(
                "INSERT INTO instance_lock (id, instance_id, heartbeat) VALUES (1, %s, %s)",
                (instance_id, now)
            )
            return True
        else:
            last_heartbeat = existing[0]['heartbeat']
            if (now - last_heartbeat).total_seconds() > 60:
                self.execute_query(
                    "UPDATE instance_lock SET instance_id = %s, heartbeat = %s WHERE id = 1",
                    (instance_id, now)
                )
                return True
            return False

    def update_heartbeat(self, instance_id: str):
        self.execute_query(
            "UPDATE instance_lock SET heartbeat = %s WHERE instance_id = %s AND id = 1",
            (datetime.now(), instance_id)
        )

    def release_lock(self, instance_id: str):
        self.execute_query(
            "DELETE FROM instance_lock WHERE instance_id = %s AND id = 1",
            (instance_id,)
        )

    # ==================== АЭРОДРОМЫ ====================

    def get_aerodrome_by_search(self, search_text: str):
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

    def search_aerodromes(self, keyword: str):
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

    def add_aerodrome(self, name: str, city: str, airport_name: str, housing_info: str, created_by: int):
        result = self.execute_query(
            """INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (name, city, airport_name, housing_info, created_by),
            fetch=True
        )
        return result[0]['id'] if result else None

    def get_aerodrome_by_id(self, aerodrome_id: int):
        result = self.execute_query(
            "SELECT * FROM aerodromes WHERE id = %s",
            (aerodrome_id,), fetch=True
        )
        return dict(result[0]) if result else None

    def get_all_aerodromes_list(self):
        result = self.execute_query(
            "SELECT * FROM aerodromes ORDER BY name", fetch=True
        )
        return [dict(r) for r in result] if result else []

    def update_aerodrome(self, aerodrome_id: int, **kwargs):
        allowed_fields = {'name', 'city', 'airport_name', 'housing_info'}
        filtered = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not filtered:
            return
        set_clause = ", ".join([f"{key} = %s" for key in filtered.keys()])
        values = list(filtered.values()) + [aerodrome_id]
        self.execute_query(f"UPDATE aerodromes SET {set_clause} WHERE id = %s", tuple(values))

    def delete_aerodrome(self, aerodrome_id: int):
        self.execute_query("DELETE FROM aerodromes WHERE id = %s", (aerodrome_id,))

    def get_aerodrome_phones(self, aerodrome_id: int):
        result = self.execute_query(
            "SELECT * FROM aerodrome_phones WHERE aerodrome_id = %s ORDER BY phone_name",
            (aerodrome_id,), fetch=True
        )
        return [dict(r) for r in result] if result else []

    def add_aerodrome_phone(self, aerodrome_id: int, phone_name: str, phone_number: str):
        self.execute_query(
            "INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number) VALUES (%s, %s, %s)",
            (aerodrome_id, phone_name, phone_number)
        )

    def delete_aerodrome_phone(self, phone_id: int):
        self.execute_query("DELETE FROM aerodrome_phones WHERE id = %s", (phone_id,))

    def add_aerodrome_document(self, aerodrome_id: int, doc_name: str, doc_type: str, file_id: str):
        self.execute_query(
            "INSERT INTO aerodrome_documents (aerodrome_id, doc_name, doc_type, file_id) VALUES (%s, %s, %s, %s)",
            (aerodrome_id, doc_name, doc_type, file_id)
        )

    def get_aerodrome_documents(self, aerodrome_id: int):
        result = self.execute_query(
            "SELECT * FROM aerodrome_documents WHERE aerodrome_id = %s",
            (aerodrome_id,), fetch=True
        )
        return [dict(r) for r in result] if result else []

    def delete_aerodrome_document(self, doc_id: int):
        self.execute_query("DELETE FROM aerodrome_documents WHERE id = %s", (doc_id,))

    # ==================== БЛОКИ БЕЗОПАСНОСТИ ====================

    def add_safety_block(self, block_number: int, block_text: str, created_by: int):
        self.execute_query(
            "INSERT INTO safety_blocks (block_number, block_text, created_by) VALUES (%s, %s, %s)",
            (block_number, block_text, created_by)
        )

    def get_safety_block_by_number(self, block_number: int):
        result = self.execute_query(
            "SELECT * FROM safety_blocks WHERE block_number = %s",
            (block_number,), fetch=True
        )
        return dict(result[0]) if result else None

    def get_all_safety_blocks(self):
        result = self.execute_query(
            "SELECT * FROM safety_blocks ORDER BY block_number", fetch=True
        )
        return [dict(r) for r in result] if result else []

    def update_safety_block(self, block_number: int, block_text: str):
        self.execute_query(
            "UPDATE safety_blocks SET block_text = %s WHERE block_number = %s",
            (block_text, block_number)
        )

    def delete_safety_block(self, block_number: int):
        self.execute_query("DELETE FROM safety_blocks WHERE block_number = %s", (block_number,))

    # ==================== ЗНАНИЯ О САМОЛЁТАХ ====================

    def add_aircraft_knowledge(self, aircraft_type: str, knowledge_name: str, knowledge_text: str, file_id: str = None):
        self.execute_query(
            "INSERT INTO aircraft_knowledge (aircraft_type, knowledge_name, knowledge_text, file_id) VALUES (%s, %s, %s, %s)",
            (aircraft_type, knowledge_name, knowledge_text, file_id)
        )

    def get_aircraft_knowledge_by_type(self, aircraft_type: str):
        result = self.execute_query(
            "SELECT * FROM aircraft_knowledge WHERE aircraft_type = %s",
            (aircraft_type,), fetch=True
        )
        return [dict(r) for r in result] if result else []

    def delete_aircraft_knowledge(self, knowledge_id: int):
        self.execute_query("DELETE FROM aircraft_knowledge WHERE id = %s", (knowledge_id,))

    # ==================== УТИЛИТЫ ====================

    def close(self):
        if self.db_pool:
            self.db_pool.closeall()
            logger.info("🔌 PostgreSQL отключена")


# Глобальный экземпляр
from config import DATABASE_URL

db = None
try:
    db = Database(DATABASE_URL)
except Exception as e:
    logger.error(f"❌ Не удалось инициализировать базу данных: {e}")
    raise
