#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 utils/registration_check.py
Декораторы для проверки регистрации пользователей
"""

from functools import wraps
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from db_manager import get_user
import logging

logger = logging.getLogger(__name__)

def registration_required(func):
    """
    Декоратор для проверки регистрации пользователя.
    Если пользователь не зарегистрирован — показывает сообщение о необходимости регистрации.
    """
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        user = get_user(user_id)
        
        # Проверяем регистрацию
        if not user or not user.get('is_registered'):
            await message.answer(
                "⚠️ <b>Сначала завершите регистрацию!</b>\n\n"
                "Нажмите /start или кнопку '📝 Регистрация' чтобы начать.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="HTML"
            )
            logger.info(f"⏭️ Пользователь {user_id} попытался получить доступ без регистрации")
            return
        
        # Пользователь зарегистрирован — выполняем функцию
        return await func(message, *args, **kwargs)
    
    return wrapper


def registration_required_callback(func):
    """
    Декоратор для проверки регистрации в callback query.
    """
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        user_id = callback.from_user.id
        user = get_user(user_id)
        
        if not user or not user.get('is_registered'):
            await callback.answer(
                "⚠️ Сначала завершите регистрацию! Используйте /start",
                show_alert=True
            )
            logger.info(f"⏭️ Пользователь {user_id} попытался получить доступ через callback без регистрации")
            return
        
        return await func(callback, *args, **kwargs)
    
    return wrapper
