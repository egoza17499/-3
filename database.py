import sqlite3

class Database:
    def __init__(self, db_name='user_data.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        self.connection.commit()

    def add_user(self, username, email):
        self.cursor.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
        self.connection.commit()

    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()

    def update_user(self, user_id, username=None, email=None):
        if username:
            self.cursor.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
        if email:
            self.cursor.execute('UPDATE users SET email = ? WHERE id = ?', (email, user_id))
        self.connection.commit()

    def delete_user(self, user_id):
        self.cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.connection.commit()

    def close(self):
        self.connection.close()

# Example usage (uncomment to run)
# db = Database()
# db.create_table()
# db.add_user('john_doe', 'john@example.com')
# print(db.get_user(1))
# db.update_user(1, email='john_doe@example.com')
# db.delete_user(1)
# db.close()