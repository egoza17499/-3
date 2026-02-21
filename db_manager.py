# db_manager.py - глобальный экземпляр базы данных
from database import Database
from config import DB_NAME

# Создаём и экспортируем глобальный экземпляр БД
db = Database(DB_NAME)
