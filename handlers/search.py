#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 handlers/search.py
Поиск ПОЛЬЗОВАТЕЛЕЙ — только для админов
✅ Показывает полный профиль (как "Мой профиль")
✅ Кнопки: Редактировать ФИО + Удалить пользователя
✅ Исправлен импорт Message
"""

import logging
import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import (  # ✅ Добавили Message сюда
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
)
from aiogram.fsm.state import State, StatesGroup
from validators import generate_profile_text, check_flight_ban
from db_manager import db, get_user, update_user, delete_user
from utils.admin_check import is_admin

logger = logging.getLogger(__name__)  # ✅ __name__ правильно
router = Router()

# ============================================================
# СОСТОЯНИЯ
# ============================================================

class AdminEditState(StatesGroup):
    waiting_for_fio = State()
    target_user_id = State()

# ============================================================
# ФИЛЬТРЫ: что НЕ обрабатывать в этом хендлере
# ============================================================

MENU_BUTTONS = [
    "📝 Регистрация",
    "👤 Мой профиль", 
    "🔍 Поиск аэродрома",
    "📚 Полезная информация",
    "🛡️ Блоки безопасности",
    "/start", "/menu", "/cancel", "/profile"
]

BLOCK_PATTERN = re.compile(r'^блок\s*№?\s*(\d+)$', re.IGNORECASE)

def should_skip_search(text: str) -> bool:
    """Проверить нужно ли пропустить этот текст"""
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
    """Эвристическая проверка: похоже ли на поиск аэродрома"""
    text_lower = text.strip().lower()
    
    # Очень короткие слова (1-3 символа)
    if len(text_lower) <= 3:
        return True
    
    # Слова с дефисом и только русские буквы
    if '-' in text_lower and re.match(r'^[а-яё\-]+$', text_lower):
        return True
    
    return False


# ============================================================
# ОБРАБОТЧИК ПОИСКА ПОЛЬЗОВАТЕЛЕЙ (ТОЛЬКО АДМИНЫ)
# ============================================================

@router.message(F.chat.type == "private")
async def search_users_handler(message: Message, state: FSMContext):  # ✅ Message теперь определён
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
    if is_likely_aerodrome_search(search_text):
        logger.debug(f"⏭️ Пропускаем (похоже на аэродром): '{search_text}'")
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
# ОБРАБОТЧИК CALLBACK: ПОЛНЫЙ ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
# ============================================================

@router.callback_query(F.data.startswith("admin_user_profile_"))
async def show_admin_user_profile(callback: CallbackQuery):
    """Показать подробный профиль пользователя для админа (как "Мой профиль")"""
    
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
    
    # ✅ ИСПОЛЬЗУЕМ generate_profile_text для полного профиля
    profile_text = generate_profile_text(target_user)
    
    # Проверяем запреты на полёты
    bans = check_flight_ban(target_user)
    if bans:
        profile_text += "\n\n🔴 <b>ПОЛЁТЫ ЗАПРЕЩЕНЫ:</b>\n" + "\n".join([f"• {b}" for b in bans])
    
    # ✅ ДОБАВЛЯЕМ КНОПКИ: Редактировать ФИО + Удалить пользователя
    keyboard = [
        [InlineKeyboardButton(
            text="✏️ Редактировать ФИО",
            callback_data=f"admin_edit_user_fio_{target_user_id}"
        )],
        [InlineKeyboardButton(
            text="🗑️ Удалить пользователя",
            callback_data=f"admin_delete_user_{target_user_id}"
        )],
        [InlineKeyboardButton(
            text="🔙 Назад к поиску",
            callback_data="admin_functions_back"
        )]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(profile_text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()


# ============================================================
# ОБРАБОТЧИК: РЕДАКТИРОВАНИЕ ФИО
# ============================================================

@router.callback_query(F.data.startswith("admin_edit_user_fio_"))
async def admin_edit_user_fio_start(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование ФИО пользователя"""
    
    user_id = callback.from_user.id
    if not await is_admin(user_id, callback.from_user.username):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    try:
        target_user_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка: неверный ID", show_alert=True)
        return
    
    target_user = get_user(target_user_id)
    if not target_user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    # Сохраняем ID пользователя в состоянии
    await state.update_data(edit_user_id=target_user_id)
    await state.set_state(AdminEditState.waiting_for_fio)
    
    await callback.message.edit_text(
        f"✏️ <b>Редактирование ФИО</b>\n\n"
        f"Пользователь: {target_user.get('fio') or 'Не указано'}\n\n"
        f"Введите новое ФИО:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_user_profile_{target_user_id}")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminEditState.waiting_for_fio)
async def admin_edit_user_fio_save(message: Message, state: FSMContext):  # ✅ Message теперь определён
    """Сохранить новое ФИО пользователя"""
    
    user_id = message.from_user.id
    if not await is_admin(user_id, message.from_user.username):
        return
    
    data = await state.get_data()
    target_user_id = data.get('edit_user_id')
    
    if not target_user_id:
        await message.answer("❌ Ошибка: не найден ID пользователя")
        await state.clear()
        return
    
    new_fio = message.text.strip()
    
    # Обновляем ФИО в БД
    update_user(target_user_id, fio=new_fio)
    
    await message.answer(
        f"✅ ФИО обновлено: <b>{new_fio}</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к профилю", callback_data=f"admin_user_profile_{target_user_id}")]
        ]),
        parse_mode="HTML"
    )
    await state.clear()


# ============================================================
# ОБРАБОТЧИК: УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ (ИСПРАВЛЕНО)
# ============================================================

@router.callback_query(F.data.startswith("admin_delete_user_"))
async def admin_delete_user_confirm(callback: CallbackQuery):
    """Показать подтверждение удаления пользователя"""
    
    user_id = callback.from_user.id
    if not await is_admin(user_id, callback.from_user.username):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    try:
        target_user_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка: неверный ID", show_alert=True)
        return
    
    target_user = get_user(target_user_id)
    if not target_user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    fio = target_user.get('fio') or "Неизвестно"
    
    # ✅ Показываем НОВОЕ сообщение с подтверждением
    keyboard = [
        [InlineKeyboardButton(
            text="✅ Да, удалить",
            callback_data=f"admin_delete_user_confirm_{target_user_id}"
        )],
        [InlineKeyboardButton(
            text="❌ Отмена",
            callback_data=f"admin_user_profile_{target_user_id}"
        )]
    ]
    
    await callback.message.answer(
        f"🗑️ <b>Удаление пользователя</b>\n\n"
        f"Вы действительно хотите удалить пользователя?\n\n"
        f"👤 {fio}\n"
        f"ID: {target_user_id}\n\n"
        f"<b>⚠️ Это действие нельзя отменить!</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_delete_user_confirm_"))
async def admin_delete_user_execute(callback: CallbackQuery):
    """Удаление пользователя (выполняется после подтверждения)"""
    
    user_id = callback.from_user.id
    if not await is_admin(user_id, callback.from_user.username):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    try:
        target_user_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка: неверный ID", show_alert=True)
        return
    
    # ✅ Удаляем пользователя
    success = delete_user(target_user_id)
    
    if success:
        # ✅ Удаляем сообщение с подтверждением
        try:
            await callback.message.delete()
        except:
            pass
        
        await callback.message.answer(
            f"✅ Пользователь {target_user_id} успешно удалён!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад к поиску", callback_data="admin_functions_back")]
            ])
        )
    else:
        await callback.answer("❌ Ошибка при удалении пользователя", show_alert=True)
    
    await callback.answer()
