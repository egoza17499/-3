#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 handlers/search.py
Поиск ПОЛЬЗОВАТЕЛЕЙ — только для админов
⚠️ НЕ трогает поиск аэродромов и кнопки меню!
"""

import logging
import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db_manager import db, get_user
from utils.admin_check import is_admin

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# ФИЛЬТРЫ: что НЕ обрабатывать в этом хендлере
# ============================================================

# Кнопки главного меню — их обрабатывают другие хендлеры
MENU_BUTTONS = [
    "📝 Регистрация",
    "👤 Мой профиль", 
    "🔍 Поиск аэродрома",
    "📚 Полезная информация",
    "🛡️ Блоки безопасности",
    "/start", "/menu", "/cancel", "/profile"
]

# Команды для блоков безопасности
BLOCK_PATTERN = re.compile(r'^блок\s*№?\s*(\d+)$', re.IGNORECASE)

# Поиск аэродромов (короткие слова — скорее всего названия городов)
def is_aerodrome_search(text: str) -> bool:
    """Проверить что текст похож на поиск аэродрома, а не пользователя"""
    text_lower = text.lower().strip()
    
    # Короткие слова (1-10 символов) — скорее всего аэродромы
    if len(text_lower) <= 10:
        return True
    
    # Слова с дефисом или пробелом (названия городов)
    if '-' in text_lower or ' ' in text_lower:
        return True
    
    # Русские буквы только (аэродромы обычно на русском)
    if re.match(r'^[а-яё\s\-]+$', text_lower):
        return True
    
    return False

# ============================================================
# ОБРАБОТЧИК ПОИСКА ПОЛЬЗОВАТЕЛЕЙ (ТОЛЬКО АДМИНЫ)
# ============================================================

@router.message(
    F.text,
    F.chat.type == "private",  # Только в личных сообщениях!
    # ❌ ИСКЛЮЧАЕМ всё что НЕ поиск пользователя:
    ~F.text.lower().in_([b.lower() for b in MENU_BUTTONS]),  # Не кнопки меню
    ~F.text.regexp(BLOCK_PATTERN),  # Не "блок N"
    ~F.text.regexp(re.compile(r'^\/\w+', re.IGNORECASE)),  # Не /команды
)
async def search_users_handler(message: types.Message, state: FSMContext):
    """
    Поиск ПОЛЬЗОВАТЕЛЕЙ по ФИО или username.
    Работает ТОЛЬКО для админов в личных сообщениях.
    """
    
    search_text = message.text.strip()
    
    # 🔥 ФИЛЬТР: если похоже на поиск аэродрома — пропускаем!
    if is_aerodrome_search(search_text):
        logger.debug(f"⏭️ Пропускаем (похоже на аэродром): '{search_text}'")
        return  # Пусть обрабатывает handlers/aerodrome_search.py
    
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Проверка админ-статуса
    if not await is_admin(user_id, username):
        logger.info(f"⏭️ Пропускаем (не админ): '{search_text}'")
        return
    
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
        # ✅ user — это dict, не кортеж!
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
