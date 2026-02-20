import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Подключение к базе данных"""
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Создание таблиц"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE,
                username TEXT,
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
                registration_complete BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS aerodromes (
                aerodrome_id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_lock (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                instance_id TEXT NOT NULL,
                acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def add_user(self, chat_id, username=None):
        """Добавление нового пользователя"""
        try:
            self.cursor.execute('''
                INSERT INTO users (chat_id, username) VALUES (?, ?)
                ON CONFLICT(chat_id) DO NOTHING
            ''', (chat_id, username))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя: {e}")
            return False

    def update_user(self, chat_id, **fields):
        """Обновление данных пользователя"""
        if not fields:
            return False
        
        set_clause = ', '.join(f'{key} = ?' for key in fields.keys())
        values = list(fields.values())
        values.append(chat_id)
        
        try:
            self.cursor.execute(f'''
                UPDATE users SET {set_clause} WHERE chat_id = ?
            ''', values)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления: {e}")
            return False

    def get_user(self, chat_id):
        """Получение данных пользователя"""
        self.cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        return self.cursor.fetchone()

    def check_admin_status(self, user_id):
        """Проверка статуса администратора"""
        self.cursor.execute('SELECT * FROM admins WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone() is not None

    def add_admin(self, user_id, added_by):
        """Добавление администратора"""
        try:
            self.cursor.execute('''
                INSERT INTO admins (user_id, added_by) VALUES (?, ?)
                ON CONFLICT(user_id) DO NOTHING
            ''', (user_id, added_by))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления админа: {e}")
            return False

    def remove_admin(self, user_id):
        """Удаление администратора"""
        try:
            self.cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления админа: {e}")
            return False

    def get_all_users(self):
        """Получение всех пользователей"""
        self.cursor.execute('SELECT * FROM users WHERE registration_complete = TRUE')
        return self.cursor.fetchall()

    def search_users_by_fio(self, search_term):
        """Поиск пользователей по ФИО"""
        self.cursor.execute('''
            SELECT * FROM users 
            WHERE fio LIKE ? OR rank LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%'))
        return self.cursor.fetchall()

    def add_aerodrome(self, keyword, content):
        """Добавление информации об аэродроме"""
        try:
            self.cursor.execute('''
                INSERT INTO aerodromes (keyword, content) VALUES (?, ?)
            ''', (keyword, content))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления аэродрома: {e}")
            return False

    def search_aerodromes(self, keyword):
        """Поиск аэродромов"""
        self.cursor.execute('''
            SELECT content FROM aerodromes 
            WHERE keyword LIKE ?
        ''', (f'%{keyword}%',))
        return self.cursor.fetchall()

    def set_registration_complete(self, chat_id):
        """Завершение регистрации"""
        return self.update_user(chat_id, registration_complete=True)

    def check_and_acquire_lock(self, instance_id):
        """Проверка и захват блокировки"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO bot_lock (id, instance_id, acquired_at, last_heartbeat)
                VALUES (1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (instance_id,))
            
            self.cursor.execute('SELECT instance_id, acquired_at FROM bot_lock WHERE id = 1')
            row = self.cursor.fetchone()
            self.conn.commit()
            
            if row and row[0] == instance_id:
                logger.info(f"✅ Блокировка захвачена: {instance_id}")
                return True
            else:
                logger.warning(f"❌ Блокировка занята: {row[0] if row else 'неизвестно'}")
                return False
        except Exception as e:
            logger.error(f"Ошибка захвата блокировки: {e}")
            return False

    def release_lock(self, instance_id):
        """Освобождение блокировки"""
        try:
            self.cursor.execute('DELETE FROM bot_lock WHERE id = 1 AND instance_id = ?', (instance_id,))
            self.conn.commit()
            logger.info(f"🔓 Блокировка освобождена: {instance_id}")
        except Exception as e:
            logger.error(f"Ошибка освобождения блокировки: {e}")

    def update_heartbeat(self, instance_id):
        """Обновление heartbeat"""
        try:
            self.cursor.execute('''
                UPDATE bot_lock 
                SET last_heartbeat = CURRENT_TIMESTAMP 
                WHERE id = 1 AND instance_id = ?
            ''', (instance_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка heartbeat: {e}")

    def check_lock_status(self):
        """Проверка статуса блокировки"""
        try:
            self.cursor.execute('SELECT instance_id, acquired_at, last_heartbeat FROM bot_lock WHERE id = 1')
            row = self.cursor.fetchone()
            if row:
                return {
                    'instance_id': row[0],
                    'acquired_at': row[1],
                    'last_heartbeat': row[2]
                }
            return None
        except Exception as e:
            logger.error(f"Ошибка проверки блокировки: {e}")
            return None

    def close(self):
        """Закрытие подключения"""
        if self.conn:
            self.conn.close()
            logger.info("🔌 База данных закрыта")
