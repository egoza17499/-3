from aiogram import types
from aiogram.types import CallbackQuery, Message
from functools import wraps
from config import ADMIN_IDS, ADMIN_USERNAMES
from db_manager import db
import logging

logger = logging.getLogger(__name__)

# ============================================================
# ПРОВЕРКА ПРАВ АДМИНИСТРАТОРА
# ============================================================

async def is_admin(user_id: int, username: str = None) -> bool:
    """
    Проверка, является ли пользователь админом
    
    Args:
        user_id: Telegram ID пользователя
        username: Username пользователя (без @ или с @)
    
    Returns:
        bool: True если пользователь админ, False иначе
    """
    # 1. Проверка по ID из config.py
    if user_id in ADMIN_IDS:
        logger.debug(f"✅ Админ {user_id} найден в ADMIN_IDS")
        return True
    
    # 2. Проверка по username из config.py
    if username:
        username_clean = username.lstrip('@').lower()
        admin_usernames_clean = [u.lower().lstrip('@') for u in ADMIN_USERNAMES]
        if username_clean in admin_usernames_clean:
            logger.debug(f"✅ Админ @{username} найден в ADMIN_USERNAMES")
            return True
    
    # 3. Проверка через базу данных (таблица admins)
    try:
        # Проверка по user_id
        admin_record = db.execute_query(
            "SELECT user_id FROM admins WHERE user_id = %s",
            (user_id,),
            fetch=True
        )
        if admin_record:
            logger.debug(f"✅ Админ {user_id} найден в БД")
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
                logger.debug(f"✅ Админ @{username} найден в БД по username")
                return True
    except Exception as e:
        logger.error(f"❌ Ошибка проверки админа в БД: {e}")
    
    logger.debug(f"❌ Пользователь {user_id} (@{username}) не является админом")
    return False

# ============================================================
# ДЕКОРАТОРЫ ДЛЯ ПРОВЕРКИ ПРАВ
# ============================================================

def admin_required(func):
    """
    Декоратор для проверки админских прав в callback query
    
    Использование:
        @router.callback_query(F.data == "admin_function")
        @admin_required
        async def admin_function(callback: types.CallbackQuery):
            ...
    """
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        user_id = callback.from_user.id
        username = callback.from_user.username
        
        if not await is_admin(user_id, username):
            await callback.answer("❌ У вас нет прав для выполнения этого действия", show_alert=True)
            logger.warning(f"⚠️ Пользователь {user_id} (@{username}) попытался получить доступ к админской функции: {callback.data}")
            return
        
        logger.info(f"✅ Админ {user_id} (@{username}) получил доступ к функции: {callback.data}")
        return await func(callback, *args, **kwargs)
    return wrapper

def admin_required_message(func):
    """
    Декоратор для проверки админских прав в сообщениях
    
    Использование:
        @router.message(AdminState.some_state)
        @admin_required_message
        async def some_handler(message: types.Message):
            ...
    """
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        username = message.from_user.username
        
        if not await is_admin(user_id, username):
            await message.answer("❌ У вас нет прав для выполнения этого действия")
            logger.warning(f"⚠️ Пользователь {user_id} (@{username}) попытался получить доступ к админской функции")
            return
        
        logger.info(f"✅ Админ {user_id} (@{username}) получил доступ к функции")
        return await func(message, *args, **kwargs)
    return wrapper

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

async def check_admin_access(user_id: int, username: str = None, action: str = "") -> bool:
    """
    Проверка доступа с логированием
    
    Args:
        user_id: Telegram ID пользователя
        username: Username пользователя
        action: Описание действия для логирования
    
    Returns:
        bool: True если доступ разрешён
    """
    is_admin_user = await is_admin(user_id, username)
    
    if is_admin_user:
        logger.info(f"✅ Админ {user_id} (@{username}) выполнил действие: {action}")
    else:
        logger.warning(f"⚠️ Отказано в доступе пользователю {user_id} (@{username}) для действия: {action}")
    
    return is_admin_user

def get_admin_info(user_id: int, username: str = None) -> dict:
    """
    Получить информацию об админе
    
    Args:
        user_id: Telegram ID пользователя
        username: Username пользователя
    
    Returns:
        dict: Информация об админе
    """
    admin_type = "unknown"
    source = "unknown"
    
    if user_id in ADMIN_IDS:
        admin_type = "main_admin"
        source = "config.ADMIN_IDS"
    elif username:
        username_clean = username.lstrip('@').lower()
        admin_usernames_clean = [u.lower().lstrip('@') for u in ADMIN_USERNAMES]
        if username_clean in admin_usernames_clean:
            admin_type = "username_admin"
            source = "config.ADMIN_USERNAMES"
    
    # Проверка через БД
    try:
        admin_record = db.execute_query(
            "SELECT * FROM admins WHERE user_id = %s",
            (user_id,),
            fetch=True
        )
        if admin_record:
            admin_type = "database_admin"
            source = "database.admins"
    except Exception as e:
        logger.error(f"Ошибка получения информации об админе: {e}")
    
    return {
        "user_id": user_id,
        "username": username,
        "is_admin": admin_type != "unknown",
        "admin_type": admin_type,
        "source": source
    }
