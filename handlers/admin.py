#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ handlers/admin.py — Административные функции
✅ Управление пользователями с поиском
✅ Статистика с правильными функциями
✅ Управление админами
"""

import logging
from aiogram import Router, F, types
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, 
    InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from validators import check_flight_ban, check_date_warnings, generate_profile_text
# ✅ ИСПРАВЛЕНО: импортируем функции напрямую из db_manager
from db_manager import (
    db,
    get_all_users,
    get_users_ready_to_fly,
    get_users_cannot_fly,
    search_users,
    find_user_by_username,
    add_admin,
    remove_admin,
    get_all_admins
)
from utils.admin_check import admin_required, admin_required_callback, admin_required_message

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# СОСТОЯНИЯ
# ============================================================

class AddAdminState(StatesGroup):
    username = State()

class RemoveAdminState(StatesGroup):
    user_id = State()

class AdminListState(StatesGroup):
    waiting_for_search = State()

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Создать клавиатуру административных функций"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_list")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📚 Управление базой знаний", callback_data="admin_knowledge")],
        [InlineKeyboardButton(text="✈️ Заполнить базу аэродромов", callback_data="admin_fill_airports")],
        [InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_manage")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])


def get_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Создать клавиатуру главного меню"""
    keyboard = [
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="📚 Полезная информация")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="🛡 Административные функции")])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ============================================================
# ГЛАВНОЕ АДМИН МЕНЮ
# ============================================================

@router.callback_query(F.data == "admin_functions")
@admin_required_callback
async def admin_functions(callback: CallbackQuery):
    """Показать админское меню"""
    await callback.message.edit_text(
        "🛡️ <b>Административные функции</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# ============================================================
# СПИСОК ПОЛЬЗОВАТЕЛЕЙ С ПОИСКОМ
# ============================================================

@router.callback_query(F.data == "admin_list")
@admin_required_callback
async def admin_list(callback: CallbackQuery, state: FSMContext):
    """Показать список всех пользователей с поиском"""
    try:
        users = get_all_users()  # ✅ ИСПРАВЛЕНО: функция из db_manager
        
        if not users:
            text = "📋 <b>Список пользователей:</b>\n\n"
            text += "Пользователей пока нет"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions")]
            ])
            
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            await callback.answer()
            return
        
        text = "📋 <b>Список пользователей:</b>\n\n"
        text += "💡 <i>Введите фамилию или имя для поиска</i>\n\n"
        
        for i, user in enumerate(users[:20], 1):  # Показываем первые 20
            fio = user.get('fio') or "Не указано"
            rank = user.get('rank') or "Не указано"
            username = user.get('username') or "Не указан"
            
            warnings, bans = check_date_warnings(user)
            
            if bans:
                indicator = "⛔"
            elif warnings:
                indicator = "⚠️"
            else:
                indicator = "✅"
            
            text += f"{i}. {indicator} {fio}\n"
            text += f"   Звание: {rank}\n"
            text += f"   Username: @{username}\n\n"
        
        text += "\n<i>Введите текст для поиска или нажмите Назад</i>"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(AdminListState.waiting_for_search)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_list: {e}")
        await callback.answer("❌ Ошибка при получении списка", show_alert=True)


@router.message(AdminListState.waiting_for_search)
@admin_required_message
async def admin_list_search_handler(message: Message):
    """Обработчик поиска пользователей"""
    search_text = message.text.strip()
    
    if len(search_text) < 2:
        await message.answer("⚠️ Введите минимум 2 символа для поиска")
        return
    
    users = search_users(search_text)  # ✅ ИСПРАВЛЕНО: функция из db_manager
    
    if not users:
        await message.answer(
            f"❌ Пользователи по запросу \"{search_text}\" не найдены\n\n"
            f"Попробуйте другую фамилию или имя"
        )
        return
    
    if len(users) == 1:
        # Показываем подробный профиль
        user = users[0]
        profile_text = generate_profile_text(user)
        warnings, bans = check_date_warnings(user)
        
        if warnings:
            profile_text += "\n⚠️ <b>СКОРО ИСТЕКАЕТ:</b>\n" + "\n".join([f"• {w}" for w in warnings])
        
        if bans:
            profile_text += "\n\n⛔ <b>ЗАПРЕЩЕНО:</b>\n" + "\n".join([f"• {b}" for b in bans])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")]
        ])
        
        await message.answer(profile_text, reply_markup=keyboard, parse_mode="HTML")
    else:
        # Показываем список найденных
        text = f"🔍 <b>Найдено пользователей: {len(users)}</b>\n\n"
        
        for i, user in enumerate(users[:20], 1):
            fio = user.get('fio') or "Не указано"
            rank = user.get('rank') or "Не указано"
            username = user.get('username') or "Не указан"
            
            warnings, bans = check_date_warnings(user)
            
            if bans:
                indicator = "⛔"
            elif warnings:
                indicator = "⚠️"
            else:
                indicator = "✅"
            
            text += f"{i}. {indicator} {fio}\n"
            text += f"   Звание: {rank}\n"
            text += f"   Username: @{username}\n\n"
        
        text += "\n<i>Введите другой запрос для поиска или нажмите Назад</i>"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")]
        ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# ============================================================
# СТАТИСТИКА — ✅ ИСПРАВЛЕНО
# ============================================================

@router.callback_query(F.data == "admin_stats")
@admin_required_callback
async def admin_stats(callback: CallbackQuery):
    """Показать статистику"""
    try:
        users = get_all_users()  # ✅ ИСПРАВЛЕНО
        total = len(users) if users else 0
        
        # ✅ ИСПРАВЛЕНО: используем функции из db_manager, не методы db
        ready_users = get_users_ready_to_fly()
        cannot_fly_users = get_users_cannot_fly()
        
        can_fly = len(ready_users)
        cannot_fly = len(cannot_fly_users)
        
        text = "📊 <b>Статистика:</b>\n\n"
        text += f"👥 Всего пользователей: {total}\n"
        text += f"✅ Готовы к полётам: {can_fly}\n"
        text += f"🚫 Не могут летать: {cannot_fly}\n\n"
        text += "Нажмите на кнопку чтобы увидеть список:"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"✅ Готовы к полётам ({can_fly})", callback_data="admin_stats_ready")],
            [InlineKeyboardButton(text=f"🚫 Не могут летать ({cannot_fly})", callback_data="admin_stats_cannot")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_stats: {e}")
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)


@router.callback_query(F.data == "admin_stats_ready")
@admin_required_callback
async def admin_stats_show_ready(callback: CallbackQuery):
    """Показать пользователей готовых к полётам"""
    try:
        # ✅ ИСПРАВЛЕНО
        users = get_users_ready_to_fly()
        
        if not users:
            await callback.answer("Нет пользователей готовых к полётам", show_alert=True)
            return
        
        text = "✅ <b>Готовы к полётам:</b>\n\n"
        
        for i, user in enumerate(users[:20], 1):
            fio = user.get('fio') or "Не указано"
            rank = user.get('rank') or "Не указано"
            username = user.get('username') or "Не указан"
            
            text += f"{i}. {fio}\n"
            text += f"   Звание: {rank}\n"
            text += f"   Username: @{username}\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к статистике", callback_data="admin_stats")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_stats_show_ready: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data == "admin_stats_cannot")
@admin_required_callback
async def admin_stats_show_cannot(callback: CallbackQuery):
    """Показать пользователей кто не может летать"""
    try:
        # ✅ ИСПРАВЛЕНО
        users = get_users_cannot_fly()
        
        if not users:
            await callback.answer("Нет пользователей кто не может летать", show_alert=True)
            return
        
        text = "🚫 <b>Не могут летать:</b>\n\n"
        
        for i, user in enumerate(users[:20], 1):
            fio = user.get('fio') or "Не указано"
            rank = user.get('rank') or "Не указано"
            username = user.get('username') or "Не указан"
            
            bans = check_flight_ban(user)
            
            text += f"{i}. {fio}\n"
            text += f"   Звание: {rank}\n"
            text += f"   Username: @{username}\n"
            text += "   Причины:\n"
            for ban in bans:
                text += f"   • {ban}\n"
            text += "\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к статистике", callback_data="admin_stats")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_stats_show_cannot: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)

# ============================================================
# НАЗАД В ГЛАВНОЕ МЕНЮ
# ============================================================

@router.callback_query(F.data == "admin_functions_back")
@admin_required_callback
async def admin_functions_back(callback: CallbackQuery, state: FSMContext):
    """Вернуться в админское меню"""
    await state.clear()
    
    await callback.message.edit_text(
        "🛡️ <b>Административные функции</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню"""
    await state.clear()
    
    user_id = callback.from_user.id
    is_admin_user = user_id in ADMIN_IDS or db.check_admin_status(user_id, callback.from_user.username)
    
    keyboard = get_main_menu_keyboard(is_admin=is_admin_user)
    
    await callback.message.edit_text(
        "📱 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

# ============================================================
# УПРАВЛЕНИЕ АДМИНАМИ
# ============================================================

@router.callback_query(F.data == "admin_manage")
@admin_required_callback
async def admin_manage(callback: CallbackQuery):
    """Меню управления админами"""
    text = "👥 <b>Управление администраторами</b>\n\n"
    text += "Выберите действие:\n\n"
    text += "➕ Добавить админа по username\n"
    text += "➖ Удалить админа"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить админа", callback_data="admin_add_admin")],
        [InlineKeyboardButton(text="➖ Удалить админа", callback_data="admin_remove_admin")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin_add_admin")
@admin_required_callback
async def admin_add_admin_start(callback: CallbackQuery, state: FSMContext):
    """Добавить админа"""
    await state.clear()
    
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может добавлять админов", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ <b>Добавление админа</b>\n\n"
        "Введите username пользователя (без @ или с @):\n\n"
        "Пример: @username или username",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_manage")]
        ]),
        parse_mode="HTML"
    )
    await state.set_state(AddAdminState.username)
    await callback.answer()


@router.message(AddAdminState.username)
@admin_required_message
async def admin_add_admin_by_username(message: Message, state: FSMContext):
    """Добавить админа по username"""
    try:
        username = message.text.strip().lstrip('@')
        # ✅ ИСПРАВЛЕНО: используем функцию из db_manager
        user = find_user_by_username(username)
        
        if not user:
            await message.answer(
                f"❌ Пользователь @{username} не найден в базе данных!\n\n"
                "Пользователь должен сначала зарегистрироваться в боте."
            )
            await state.clear()
            return
        
        # ✅ ИСПРАВЛЕНО: используем функцию из db_manager
        add_admin(user['user_id'], username, message.from_user.id)
        
        await message.answer(
            f"✅ Пользователь @{username} (ID: {user['user_id']}) добавлен в админы!",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Назад")]], resize_keyboard=True)
        )
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_add_admin_by_username: {e}")
        await message.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "admin_remove_admin")
@admin_required_callback
async def admin_remove_admin_start(callback: CallbackQuery, state: FSMContext):
    """Удалить админа"""
    await state.clear()
    
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может удалять админов", show_alert=True)
        return
    
    # ✅ ИСПРАВЛЕНО: используем функцию из db_manager
    admins = get_all_admins()
    
    if not admins:
        await callback.message.edit_text("📋 В базе нет дополнительных админов (кроме тех что в config)")
        await callback.answer()
        return
    
    text = "➖ <b>Удаление админа</b>\n\n"
    text += "Текущие админы из базы данных:\n\n"
    
    for admin in admins:
        username = admin.get('username') or "не указан"
        text += f"• ID: {admin.get('user_id')} (@{username})\n"
    
    text += "\nВведите ID админа которого хотите удалить:"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(RemoveAdminState.user_id)
    await callback.answer()


@router.message(RemoveAdminState.user_id)
@admin_required_message
async def admin_remove_admin_by_id(message: Message, state: FSMContext):
    """Удалить админа по ID"""
    try:
        user_id = int(message.text.strip())
        
        if user_id in ADMIN_IDS:
            await message.answer("❌ Нельзя удалить главного админа из config!")
            await state.clear()
            return
        
        # ✅ ИСПРАВЛЕНО: используем функцию из db_manager
        remove_admin(user_id)
        
        await message.answer(
            f"✅ Админ с ID {user_id} удалён!",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Назад")]], resize_keyboard=True)
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Введите корректный ID (число)")
    except Exception as e:
        logger.error(f"Ошибка в admin_remove_admin_by_id: {e}")
        await message.answer("❌ Произошла ошибка")

# ============================================================
# ОСТАЛЬНЫЕ ФУНКЦИИ (заглушки)
# ============================================================

@router.callback_query(F.data == "admin_knowledge")
@admin_required_callback
async def admin_knowledge(callback: CallbackQuery):
    """Управление базой знаний (заглушка)"""
    await callback.answer("⚠️ Функция в разработке", show_alert=True)


@router.callback_query(F.data == "admin_fill_airports")
@admin_required_callback
async def admin_fill_airports(callback: CallbackQuery):
    """Заполнить базу аэродромов (заглушка)"""
    await callback.answer("⚠️ Функция в разработке", show_alert=True)
