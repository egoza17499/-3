#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 handlers/search.py
Поиск ПОЛЬЗОВАТЕЛЕЙ — только для админов
✅ Исправлены фильтры для aiogram 3.x
"""

import logging
import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from db_manager import db, get_user
from utils.admin_check import is_admin

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# ФИЛЬТРЫ: что НЕ обрабатывать в этом хендлере
# ============================================================

MENU_BUTTONS = [
    "📝 Регистрация", "👤 Мой профиль", "🔍 Поиск аэродрома",
    "📚 Полезная информация", "🛡️ Блоки безопасности",
    "/start", "/menu", "/cancel", "/profile"
]

BLOCK_PATTERN = re.compile(r'^блок\s*№?\s*(\d+)$', re.IGNORECASE)

def should_skip_search(text: str) -> bool:
    """
    Проверить нужно ли пропустить этот текст (не поиск пользователя).
    
    Returns:
        True если текст НЕ является поиском пользователя
    """
    text_lower = text.strip().lower()
    
    # Исключаем кнопки меню
    if text_lower in [b.lower() for b in MENU_BUTTONS]:
        return True
    
    # Исключаем команды
    if text_lower.startswith('/'):
        return True
    
    # Исключаем "блок N"
    if BLOCK_PATTERN.match(text_lower):
        return True
    
    return False


def is_likely_aerodrome_search(text: str) -> bool:
    """
    Эвристическая проверка: похоже ли на поиск аэродрома.
    ⚠️ Используется как ДОПОЛНИТЕЛЬНЫЙ фильтр, не основной!
    """
    text_lower = text.strip().lower()
    
    # Очень короткие слова (1-3 символа) — скорее всего не фамилия
    if len(text_lower) <= 3:
        return True
    
    # Слова с дефисом и только русские буквы — часто названия городов
    if '-' in text_lower and re.match(r'^[а-яё\-]+$', text_lower):
        return True
    
    return False


# ============================================================
# ОБРАБОТЧИК ПОИСКА ПОЛЬЗОВАТЕЛЕЙ (ТОЛЬКО АДМИНЫ)
# ============================================================

@router.message(F.chat.type == "private")
async def search_users_handler(message: types.Message, state: FSMContext):
    """
    Поиск ПОЛЬЗОВАТЕЛЕЙ по ФИО или username.
    Работает ТОЛЬКО для админов в личных сообщениях.
    """
    
    search_text = message.text.strip()
    
    # 🔥 ФИЛЬТР 1: исключаем кнопки меню, команды, блоки
    if should_skip_search(search_text):
        return
    
    user_id = message.from_user.id
    username = message.from_user.username
    
    # 🔥 ФИЛЬТР 2: только админы
    if not await is_admin(user_id, username):
        return
    
    # 🔥 ФИЛЬТР 3: эвристика для аэродромов (опционально)
    # Если хотите чтобы поиск аэродромов работал отдельно — раскомментируйте:
    # if is_likely_aerodrome_search(search_text):
    #     logger.debug(f"⏭️ Пропускаем (похоже на аэродром): '{search_text}'")
    #     return
    
    # Поиск пользователей в БД
    logger.info(f"🔍 Поиск пользователя админом: '{search_text}'")
    users = db.search_users(search_text)
    
    if not users:
        await message.answer(
            f"❌ Пользователи по запросу <b>\"{search_text}\"</b> не найдены",
            parse_mode="HTML"
        )
        return
    
    # Формируем результат
    text = f"🔍 Найдено пользователей: <b>{len(users)}</b>\n\n"
    
    keyboard = []
    
    for user in users[:10]:  # Показываем максимум 10 результатов
        # ✅ user — это dict, используем .get()
        user_id_db = user.get('user_id')
        username_db = user.get('username') or "N/A"
        fio = user.get('fio') or "Не указано"
        rank = user.get('rank') or "Не указано"
        
        text += f"👤 <b>{fio}</b>\n"
        text += f"   @{username_db}\n"
        text += f"   {rank}\n\n"
        
        keyboard.append([InlineKeyboardButton(
            text=f"👤 {fio}",
            callback_data=f"admin_user_profile_{user_id_db}"
        )])
    
    # Кнопка "Назад"
    keyboard.append([InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="admin_functions_back"
    )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    logger.info(f"✅ Найдено {len(users)} пользователей по запросу '{search_text}'")


# ============================================================
# ОБРАБОТЧИК CALLBACK: профиль пользователя (для админов)
# ============================================================

@router.callback_query(F.data.startswith("admin_user_profile_"))
async def show_admin_user_profile(callback: CallbackQuery):
    """Показать подробный профиль пользователя для админа"""
    
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    if not await is_admin(user_id, username):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    # Извлекаем ID пользователя из callback_data
    try:
        target_user_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка: неверный ID", show_alert=True)
        return
    
    # Получаем данные пользователя
    target_user = get_user(target_user_id)
    
    if not target_user:
        await callback.message.edit_text("❌ Пользователь не найден")
        return
    
    # Формируем текст профиля
    text = f"👤 <b>Профиль пользователя</b>\n\n"
    text += f"🆔 ID: <code>{target_user.get('user_id')}</code>\n"
    text += f"👤 ФИО: {target_user.get('fio') or 'Не указано'}\n"
    text += f"🔹 Username: @{target_user.get('username') or 'N/A'}\n"
    text += f"🎖 Звание: {target_user.get('rank') or 'Не указано'}\n"
    text += f"🏅 Квалификация: {target_user.get('qualification') or 'Не указано'}\n"
    
    is_registered = target_user.get('is_registered', False)
    text += f"\n📋 Статус: {'✅ Зарегистрирован' if is_registered else '⏳ Не завершил регистрацию'}\n"
    
    # Кнопки действий для админа
    keyboard = [
        [InlineKeyboardButton(
            text="✏️ Редактировать",
            callback_data=f"admin_edit_user_{target_user_id}"
        )],
        [InlineKeyboardButton(
            text="🔙 Назад к поиску",
            callback_data="admin_functions_back"
        )]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()
