#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 utils/admin_check.py
Декораторы для проверки прав администратора
"""

from functools import wraps
from aiogram.types import Message, CallbackQuery
from config import ADMIN_IDS, ADMIN_USERNAMES
from db_manager import db
import logging

logger = logging.getLogger(__name__)

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
        return True
    
    # 2. Проверка по username из config.py
    if username:
        username_clean = username.lstrip('@').lower()
        admin_usernames_clean = [u.lower().lstrip('@') for u in ADMIN_USERNAMES]
        if username_clean in admin_usernames_clean:
            return True
    
    # 3. Проверка через базу данных
    try:
        if db.check_admin_status(user_id, username):
            return True
    except Exception as e:
        logger.error(f"❌ Ошибка проверки админа в БД: {e}")
    
    return False


def admin_required(func):
    """
    Декоратор для проверки админских прав в callback query
    
    Использование:
        @router.callback_query(F.data == "admin_function")
        @admin_required
        async def admin_function(callback: CallbackQuery):
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


def admin_required_callback(func):
    """
    ✅ Декоратор для проверки админских прав в callback query (альтернативное имя)
    
    Использование:
        @router.callback_query(F.data == "admin_function")
        @admin_required_callback
        async def admin_function(callback: CallbackQuery):
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
        async def some_handler(message: Message):
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
