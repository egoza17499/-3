import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from config import DATABASE_URL
import logging

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
        
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE,
                username TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                added_by BIGINT
            )
        """)
        
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS instance_lock (
                id SERIAL PRIMARY KEY,
                instance_id TEXT UNIQUE,
                heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("✅ Таблицы созданы/обновлены")
    
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
        """Поиск пользователей по ФИО"""
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
        """Получить пользователей готовых к полётам"""
        all_users = self.get_all_users()
        ready_users = []
        
        for user in all_users:
            from validators import check_flight_ban
            bans = check_flight_ban(user)
            if not bans:
                ready_users.append(user)
        
        return ready_users
    
    def get_users_cannot_fly(self):
        """Получить пользователей кто не может летать"""
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
    
    def close(self):
        if self.db_pool:
            self.db_pool.closeall()
            logger.info("🔌 PostgreSQL отключена")
