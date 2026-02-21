import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from config import DATABASE_URL
import logging
import json

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_url):
        try:
            self.db_pool = pool.SimpleConnectionPool(
                1, 10,
                db_url,
                cursor_factory=RealDictCursor
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
        finally:
            self.release_connection(conn)
    
    def create_tables(self):
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
        
        # Таблица блокировок
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS instance_lock (
                id SERIAL PRIMARY KEY,
                instance_id TEXT UNIQUE,
                heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица аэродромов
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
        
        # Таблица знаний по самолётам
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
        
        logger.info("✅ Все таблицы созданы/обновлены")
    
    def add_user(self, user_id: int, username: str):
        self.execute_query(
            "INSERT INTO users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING",
            (user_id, username)
        )
    
    def update_user(self, user_id: int, **kwargs):
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
        self.execute_query(query, tuple(values))
    
    def get_user(self, user_id: int):
        result = self.execute_query(
            "SELECT * FROM users WHERE user_id = %s",
            (user_id,),
            fetch=True
        )
        if result:
            user = result[0]
            return (
                user['user_id'],
                user['username'],
                user['registered_at'],
                user['fio'],
                user['rank'],
                user['qualification'],
                user['leave_start_date'],
                user['leave_end_date'],
                user['vlk_date'],
                user['umo_date'],
                user['exercise_4_md_m_date'],
                user['exercise_7_md_m_date'],
                user['exercise_4_md_90a_date'],
                user['exercise_7_md_90a_date'],
                user['parachute_jump_date'],
                user['is_registered']
            )
        return None
    
    def get_all_users(self):
        result = self.execute_query("SELECT * FROM users WHERE is_registered = TRUE", fetch=True)
        if result:
            users = []
            for user in result:
                users.append((
                    user['user_id'],
                    user['username'],
                    user['registered_at'],
                    user['fio'],
                    user['rank'],
                    user['qualification'],
                    user['leave_start_date'],
                    user['leave_end_date'],
                    user['vlk_date'],
                    user['umo_date'],
                    user['exercise_4_md_m_date'],
                    user['exercise_7_md_m_date'],
                    user['exercise_4_md_90a_date'],
                    user['exercise_7_md_90a_date'],
                    user['parachute_jump_date'],
                    user['is_registered']
                ))
            return users
        return []
    
    def search_users(self, search_text: str):
        search_text = search_text.strip().lower()
        if not search_text:
            return []
        
        result = self.execute_query(
            """SELECT * FROM users WHERE is_registered = TRUE 
               AND (LOWER(fio) LIKE %s OR LOWER(username) ILIKE %s)""",
            (f"%{search_text}%", f"%{search_text}%"),
            fetch=True
        )
        
        if result:
            users = []
            for user in result:
                users.append((
                    user['user_id'],
                    user['username'],
                    user['registered_at'],
                    user['fio'],
                    user['rank'],
                    user['qualification'],
                    user['leave_start_date'],
                    user['leave_end_date'],
                    user['vlk_date'],
                    user['umo_date'],
                    user['exercise_4_md_m_date'],
                    user['exercise_7_md_m_date'],
                    user['exercise_4_md_90a_date'],
                    user['exercise_7_md_90a_date'],
                    user['parachute_jump_date'],
                    user['is_registered']
                ))
            return users
        return []
    
    def get_users_ready_to_fly(self):
        all_users = self.get_all_users()
        ready_users = []
        
        for user in all_users:
            from validators import check_flight_ban
            bans = check_flight_ban(user)
            if not bans:
                ready_users.append(user)
        
        return ready_users
    
    def get_users_cannot_fly(self):
        all_users = self.get_all_users()
        cannot_fly_users = []
        
        for user in all_users:
            from validators import check_flight_ban
            bans = check_flight_ban(user)
            if bans:
                cannot_fly_users.append(user)
        
        return cannot_fly_users
    
    def set_registration_complete(self, user_id: int):
        self.execute_query(
            "UPDATE users SET is_registered = TRUE WHERE user_id = %s",
            (user_id,)
        )
    
    def check_admin_status(self, user_id: int, username: str = None):
        from config import ADMIN_IDS, ADMIN_USERNAMES
        
        if user_id in ADMIN_IDS:
            return True
        
        if username:
            username_clean = username.lstrip('@')
            if username_clean in ADMIN_USERNAMES:
                return True
        
        result = self.execute_query(
            "SELECT user_id FROM admins WHERE user_id = %s",
            (user_id,),
            fetch=True
        )
        if result:
            return True
        
        if username:
            username_clean = username.lstrip('@')
            result = self.execute_query(
                "SELECT user_id FROM admins WHERE username = %s",
                (username_clean,),
                fetch=True
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
        self.execute_query(
            "DELETE FROM admins WHERE user_id = %s",
            (user_id,)
        )
    
    def get_all_admins(self):
        return self.execute_query("SELECT * FROM admins", fetch=True)
    
    def find_user_by_username(self, username: str):
        username_clean = username.lstrip('@')
        result = self.execute_query(
            "SELECT user_id, username FROM users WHERE username ILIKE %s",
            (f"%{username_clean}%",),
            fetch=True
        )
        return result[0] if result else None
    
    def check_lock_status(self):
        result = self.execute_query(
            "SELECT instance_id, heartbeat FROM instance_lock WHERE id = 1",
            fetch=True
        )
        return result[0] if result else None
    
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
            else:
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
    
    def search_aerodromes(self, keyword: str):
        return []
    
    # ==================== НОВЫЕ МЕТОДЫ ДЛЯ БАЗЫ ЗНАНИЙ ====================
    
    # АЭРОДРОМЫ
    def add_aerodrome(self, name: str, city: str, airport_name: str, housing_info: str, created_by: int):
        result = self.execute_query(
            """INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (name, city, airport_name, housing_info, created_by),
            fetch=True
        )
        return result[0]['id'] if result else None
        
    def get_aerodrome_by_search(self, search_text: str):
    search_text = search_text.strip().lower()
    
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM aerodromes 
                   WHERE LOWER(name) LIKE %s 
                   OR LOWER(city) LIKE %s 
                   OR LOWER(airport_name) LIKE %s""",
                (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%")
            )
            result = cursor.fetchone()
            return result
    finally:
        self.release_connection(conn)
    
    def get_all_aerodromes_list(self):
        return self.execute_query("SELECT * FROM aerodromes ORDER BY name", fetch=True)
    
    def update_aerodrome(self, aerodrome_id: int, **kwargs):
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values()) + [aerodrome_id]
        query = f"UPDATE aerodromes SET {set_clause} WHERE id = %s"
        self.execute_query(query, tuple(values))
    
    def delete_aerodrome(self, aerodrome_id: int):
        self.execute_query("DELETE FROM aerodromes WHERE id = %s", (aerodrome_id,))
    
    # ТЕЛЕФОНЫ
    def add_aerodrome_phone(self, aerodrome_id: int, phone_name: str, phone_number: str):
        self.execute_query(
            """INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number) 
               VALUES (%s, %s, %s)""",
            (aerodrome_id, phone_name, phone_number)
        )
        
    def get_aerodrome_phones(self, aerodrome_id: int):
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM aerodrome_phones WHERE aerodrome_id = %s ORDER BY phone_name",
                (aerodrome_id,)
            )
            return cursor.fetchall()
    finally:
        self.release_connection(conn)
    
    def delete_aerodrome_phone(self, phone_id: int):
        self.execute_query("DELETE FROM aerodrome_phones WHERE id = %s", (phone_id,))
    
    # ДОКУМЕНТЫ
    def add_aerodrome_document(self, aerodrome_id: int, doc_name: str, doc_type: str, file_id: str):
        self.execute_query(
            """INSERT INTO aerodrome_documents (aerodrome_id, doc_name, doc_type, file_id) 
               VALUES (%s, %s, %s, %s)""",
            (aerodrome_id, doc_name, doc_type, file_id)
        )
    
    def get_aerodrome_documents(self, aerodrome_id: int):
        return self.execute_query(
            "SELECT * FROM aerodrome_documents WHERE aerodrome_id = %s",
            (aerodrome_id,),
            fetch=True
        )
    
    def delete_aerodrome_document(self, doc_id: int):
        self.execute_query("DELETE FROM aerodrome_documents WHERE id = %s", (doc_id,))
    
    # БЛОКИ БЕЗОПАСНОСТИ
    def add_safety_block(self, block_number: int, block_text: str, created_by: int):
        self.execute_query(
            """INSERT INTO safety_blocks (block_number, block_text, created_by) 
               VALUES (%s, %s, %s)""",
            (block_number, block_text, created_by)
        )
    
    def get_safety_block_by_number(self, block_number: int):
        result = self.execute_query(
            "SELECT * FROM safety_blocks WHERE block_number = %s",
            (block_number,),
            fetch=True
        )
        return result[0] if result else None
    
    def get_all_safety_blocks(self):
        return self.execute_query("SELECT * FROM safety_blocks ORDER BY block_number", fetch=True)
    
    def update_safety_block(self, block_number: int, block_text: str):
        self.execute_query(
            "UPDATE safety_blocks SET block_text = %s WHERE block_number = %s",
            (block_text, block_number)
        )
    
    def delete_safety_block(self, block_number: int):
        self.execute_query("DELETE FROM safety_blocks WHERE block_number = %s", (block_number,))
    
    # ЗНАНИЯ ПО САМОЛЕТАМ
    def add_aircraft_knowledge(self, aircraft_type: str, knowledge_name: str, knowledge_text: str, file_id: str = None):
        self.execute_query(
            """INSERT INTO aircraft_knowledge (aircraft_type, knowledge_name, knowledge_text, file_id) 
               VALUES (%s, %s, %s, %s)""",
            (aircraft_type, knowledge_name, knowledge_text, file_id)
        )
    
    def get_aircraft_knowledge_by_type(self, aircraft_type: str):
        return self.execute_query(
            "SELECT * FROM aircraft_knowledge WHERE aircraft_type = %s",
            (aircraft_type,),
            fetch=True
        )
    
    def delete_aircraft_knowledge(self, knowledge_id: int):
        self.execute_query("DELETE FROM aircraft_knowledge WHERE id = %s", (knowledge_id,))
    
    def close(self):
        if self.db_pool:
            self.db_pool.closeall()
            logger.info("🔌 PostgreSQL отключена")
