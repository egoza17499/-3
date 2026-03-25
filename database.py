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
            # 🔥 КЛЮЧЕВОЕ: разбираем URL для Neon.tech (без options параметра)
            # Neon не поддерживает options='-c statement_timeout=...' в pooled режиме
            
            # Убираем параметры которые могут вызвать ошибку
            clean_url = db_url.split('?')[0]  # Убираем ?sslmode=... если есть проблемы
            
            self.db_pool = pool.SimpleConnectionPool(
                1, 10,
                clean_url,
                cursor_factory=RealDictCursor
            )
            
            if self.db_pool:
                logger.info("✅ PostgreSQL подключена успешно!")
            
            # Создаём таблицы если нет
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
        
        logger.info("✅ Все таблицы созданы/обновлены")
    
    # ==================== ПОЛЬЗОВАТЕЛИ ====================
    
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
        """Получить пользователя по telegram_id"""
        result = self.execute_query(
            "SELECT * FROM users WHERE user_id = %s",
            (user_id,),
            fetch=True
        )
        if result:
            user = result[0]
            # ✅ Возвращаем словарь с безопасным доступом к колонкам
            return {
                'user_id': user['user_id'],
                'username': user.get('username'),
                'registered_at': user.get('registered_at'),  # ✅ Используем .get() для безопасности
                'fio': user.get('fio'),
                'rank': user.get('rank'),
                'qualification': user.get('qualification'),
                'leave_start_date': user.get('leave_start_date'),
                'leave_end_date': user.get('leave_end_date'),
                'vlk_date': user.get('vlk_date'),
                'umo_date': user.get('umo_date'),
                'exercise_4_md_m_date': user.get('exercise_4_md_m_date'),
                'exercise_7_md_m_date': user.get('exercise_7_md_m_date'),
                'exercise_4_md_90a_date': user.get('exercise_4_md_90a_date'),
                'exercise_7_md_90a_date': user.get('exercise_7_md_90a_date'),
                'parachute_jump_date': user.get('parachute_jump_date'),
                'is_registered': user.get('is_registered', False)
            }
        return None
    
    def get_all_users(self):
        result = self.execute_query("SELECT * FROM users WHERE is_registered = TRUE", fetch=True)
        if result:
            users = []
            for user in result:
                users.append({
                    'user_id': user['user_id'],
                    'username': user.get('username'),
                    'registered_at': user.get('registered_at'),
                    'fio': user.get('fio'),
                    'rank': user.get('rank'),
                    'qualification': user.get('qualification'),
                    'leave_start_date': user.get('leave_start_date'),
                    'leave_end_date': user.get('leave_end_date'),
                    'vlk_date': user.get('vlk_date'),
                    'umo_date': user.get('umo_date'),
                    'exercise_4_md_m_date': user.get('exercise_4_md_m_date'),
                    'exercise_7_md_m_date': user.get('exercise_7_md_m_date'),
                    'exercise_4_md_90a_date': user.get('exercise_4_md_90a_date'),
                    'exercise_7_md_90a_date': user.get('exercise_7_md_90a_date'),
                    'parachute_jump_date': user.get('parachute_jump_date'),
                    'is_registered': user.get('is_registered', False)
                })
            return users
        return []
    
    def search_users(self, search_text: str):
        """Поиск пользователей по ФИО или username"""
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
                users.append({
                    'user_id': user['user_id'],
                    'username': user.get('username'),
                    'registered_at': user.get('registered_at'),
                    'fio': user.get('fio'),
                    'rank': user.get('rank'),
                    'qualification': user.get('qualification'),
                    'leave_start_date': user.get('leave_start_date'),
                    'leave_end_date': user.get('leave_end_date'),
                    'vlk_date': user.get('vlk_date'),
                    'umo_date': user.get('umo_date'),
                    'exercise_4_md_m_date': user.get('exercise_4_md_m_date'),
                    'exercise_7_md_m_date': user.get('exercise_7_md_m_date'),
                    'exercise_4_md_90a_date': user.get('exercise_4_md_90a_date'),
                    'exercise_7_md_90a_date': user.get('exercise_7_md_90a_date'),
                    'parachute_jump_date': user.get('parachute_jump_date'),
                    'is_registered': user.get('is_registered', False)
                })
            return users
        return []
    
    def set_registration_complete(self, user_id: int):
        self.execute_query(
            "UPDATE users SET is_registered = TRUE WHERE user_id = %s",
            (user_id,)
        )
    
    # ==================== АДМИНЫ ====================
    
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
    
    # ==================== БЛОКИРОВКИ ИНСТАНСОВ ====================
    
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
    
    # ==================== АЭРОДРОМЫ ====================
    
    def search_aerodromes(self, keyword: str):
        """Поиск аэродромов по ключевому слову"""
        keyword = keyword.strip().lower()
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT name, city, airport_name FROM aerodromes 
                       WHERE LOWER(name) ILIKE %s 
                       OR LOWER(city) ILIKE %s 
                       OR LOWER(airport_name) ILIKE %s
                       LIMIT 10""",
                    (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
                )
                results = cursor.fetchall()
                return results
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
    
    def get_aerodrome_by_search(self, search_text: str):
        """Поиск аэродрома по названию или городу"""
        search_text = search_text.strip().lower()
        logger.info(f"🔍 Поиск аэродрома: '{search_text}'")
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM aerodromes 
                       WHERE name ILIKE %s 
                       OR city ILIKE %s 
                       OR airport_name ILIKE %s""",
                    (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%")
                )
                result = cursor.fetchone()
                
                if result:
                    logger.info(f"✅ Найдено: {result['name']} ({result['city']})")
                else:
                    logger.warning(f"❌ Не найдено по запросу: {search_text}")
                    
                    cursor.execute("SELECT COUNT(*) FROM aerodromes")
                    count = cursor.fetchone()[0]
                    logger.info(f"📊 Всего аэродромов в базе: {count}")
                    
                    cursor.execute("SELECT name, city FROM aerodromes LIMIT 5")
                    examples = cursor.fetchall()
                    logger.info(f"📋 Примеры: {[e['name'] for e in examples]}")
                
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
    
    def add_aerodrome_phone(self, aerodrome_id: int, phone_name: str, phone_number: str):
        self.execute_query(
            """INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number) 
               VALUES (%s, %s, %s)""",
            (aerodrome_id, phone_name, phone_number)
        )
    
    def delete_aerodrome_phone(self, phone_id: int):
        self.execute_query("DELETE FROM aerodrome_phones WHERE id = %s", (phone_id,))
    
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
    
    # ==================== БЛОКИ БЕЗОПАСНОСТИ ====================
    
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
    
    # ==================== ЗНАНИЯ О САМОЛЁТАХ ====================
    
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
    
    # ==================== УТИЛИТЫ ====================
    
    def close(self):
        if self.db_pool:
            self.db_pool.closeall()
            logger.info("🔌 PostgreSQL отключена")


# Глобальный экземпляр базы данных
db = None
if DATABASE_URL:
    try:
        db = Database(DATABASE_URL)
    except Exception as e:
        logger.error(f"❌ Не удалось инициализировать базу данных: {e}")
