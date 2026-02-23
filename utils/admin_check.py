from aiogram import types
from aiogram.types import CallbackQuery, Message
from functools import wraps
from config import ADMIN_IDS, ADMIN_USERNAMES
from db_manager import db
import logging

logger = logging.getLogger(__name__)

async def is_admin(user_id: int, username: str = None) -> bool:
    """
    Проверка, является ли пользователь админом
    """
    # Проверка по ID из config.py
    if user_id in ADMIN_IDS:
        return True
    
    # Проверка по username из config.py
    if username:
        username_clean = username.lstrip('@').lower()
        if username_clean in [u.lower() for u in ADMIN_USERNAMES]:
            return True
    
    # Проверка через базу данных (таблица admins)
    try:
        admin_record = db.execute_query(
            "SELECT user_id FROM admins WHERE user_id = %s",
            (user_id,),
            fetch=True
        )
        if admin_record:
            return True
        
        # Проверка по username в базе
        if username:
            username_clean = username.lstrip('@')
            admin_by_username = db.execute_query(
                "SELECT user_id FROM admins WHERE username ILIKE %s",
                (username_clean,),
                fetch=True
            )
            if admin_by_username:
                return True
    except Exception as e:
        logger.error(f"Ошибка проверки админа в БД: {e}")
    
    return False

def admin_required(func):
    """
    Декоратор для проверки админских прав в callback query
    """
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        user_id = callback.from_user.id
        username = callback.from_user.username
        
        if not await is_admin(user_id, username):
            await callback.answer("❌ У вас нет прав для выполнения этого действия", show_alert=True)
            logger.warning(f"Пользователь {user_id} (@{username}) попытался получить доступ к админской функции")
            return
        
        return await func(callback, *args, **kwargs)
    return wrapper

def admin_required_message(func):
    """
    Декоратор для проверки админских прав в сообщениях
    """
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        username = message.from_user.username
        
        if not await is_admin(user_id, username):
            await message.answer("❌ У вас нет прав для выполнения этого действия")
            logger.warning(f"Пользователь {user_id} (@{username}) попытался получить доступ к админской функции")
            return
        
        return await func(message, *args, **kwargs)
    return wrapper
