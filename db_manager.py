# db_manager.py - Глобальный экземпляр базы данных
from database import Database
from config import DATABASE_URL

# Создаём и экспортируем глобальный экземпляр БД
db = Database(DATABASE_URL)
