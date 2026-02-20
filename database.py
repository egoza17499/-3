def check_and_acquire_lock(self, instance_id):
    """
    Проверка и захват блокировки
    Возвращает True если удалось захватить, False если занято
    """
    try:
        # Создаём таблицу для блокировок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_lock (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                instance_id TEXT NOT NULL,
                acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Пытаемся захватить блокировку (INSERT OR REPLACE)
        self.cursor.execute('''
            INSERT OR REPLACE INTO bot_lock (id, instance_id, acquired_at, last_heartbeat)
            VALUES (1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (instance_id,))
        
        # Проверяем кто реально захватил
        self.cursor.execute('SELECT instance_id, acquired_at FROM bot_lock WHERE id = 1')
        row = self.cursor.fetchone()
        
        self.conn.commit()
        
        if row and row[0] == instance_id:
            logging.info(f"✅ Блокировка захвачена: {instance_id}")
            return True
        else:
            logging.warning(f"❌ Блокировка занята: {row[0] if row else 'неизвестно'}")
            return False
            
    except Exception as e:
        logging.error(f"Ошибка захвата блокировки: {e}")
        return False

def release_lock(self, instance_id):
    """Освобождение блокировки"""
    try:
        self.cursor.execute('''
            DELETE FROM bot_lock WHERE id = 1 AND instance_id = ?
        ''', (instance_id,))
        self.conn.commit()
        logging.info(f"🔓 Блокировка освобождена: {instance_id}")
    except Exception as e:
        logging.error(f"Ошибка освобождения блокировки: {e}")

def update_heartbeat(self, instance_id):
    """Обновление heartbeat активного экземпляра"""
    try:
        self.cursor.execute('''
            UPDATE bot_lock 
            SET last_heartbeat = CURRENT_TIMESTAMP 
            WHERE id = 1 AND instance_id = ?
        ''', (instance_id,))
        self.conn.commit()
    except Exception as e:
        logging.error(f"Ошибка heartbeat: {e}")

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
        logging.error(f"Ошибка проверки блокировки: {e}")
        return None
