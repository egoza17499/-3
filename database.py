import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE,
            last_name TEXT,
            first_name TEXT,
            patronymic TEXT,
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
            registration_complete BOOLEAN
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS aerodromes (
            aerodrome_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            location TEXT
        )''')

        self.conn.commit()

    def add_user(self, chat_id, last_name, first_name, patronymic, rank, qualification, leave_start_date, leave_end_date, vlk_date, umo_date, exercise_4_md_m_date, exercise_7_md_m_date, exercise_4_md_90a_date, exercise_7_md_90a_date, parachute_jump_date, registration_complete):
        self.cursor.execute('''INSERT INTO users (chat_id, last_name, first_name, patronymic, rank, qualification, leave_start_date, leave_end_date, vlk_date, umo_date, exercise_4_md_m_date, exercise_7_md_m_date, exercise_4_md_90a_date, exercise_7_md_90a_date, parachute_jump_date, registration_complete) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (chat_id, last_name, first_name, patronymic, rank, qualification, leave_start_date, leave_end_date, vlk_date, umo_date, exercise_4_md_m_date, exercise_7_md_m_date, exercise_4_md_90a_date, exercise_7_md_90a_date, parachute_jump_date, registration_complete))
        self.conn.commit()

    def update_user(self, user_id, **fields):
        set_clause = ', '.join(f'{key} = ?' for key in fields)
        self.cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', (*fields.values(), user_id))
        self.conn.commit()

    def check_admin_status(self, user_id):
        self.cursor.execute('SELECT * FROM admins WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone() is not None

    def get_all_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    def search_users_by_last_name(self, last_name):
        self.cursor.execute('SELECT * FROM users WHERE last_name = ?', (last_name,))
        return self.cursor.fetchall()

    def search_aerodromes(self, name):
        self.cursor.execute('SELECT * FROM aerodromes WHERE name LIKE ?', (f'%{name}%',))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

# Usage example
# db = Database('database.db')
# db.add_user(chat_id=1, last_name='Doe', first_name='John', patronymic='J.', rank='Captain', qualification='Pilot', leave_start_date='2026-01-01', leave_end_date='2026-01-10', vlk_date='2026-01-05', umo_date='2026-01-06', exercise_4_md_m_date='2026-01-07', exercise_7_md_m_date='2026-01-08', exercise_4_md_90a_date='2026-01-09', exercise_7_md_90a_date='2026-01-10', parachute_jump_date='2026-01-11', registration_complete=True)