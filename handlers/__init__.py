# Пакет обработчиков
from . import registration
from . import menu
from . import profile
from . import admin
from . import search
from . import welcome

__all__ = ['registration', 'menu', 'profile', 'admin', 'search', 'welcome']

# Функция для инициализации роутеров с БД
def init_routers(db_instance):
    """Передаём экземпляр БД во все роутеры"""
    registration.db = db_instance
    menu.db = db_instance
    profile.db = db_instance
    admin.db = db_instance
    search.db = db_instance
    welcome.db = db_instance
