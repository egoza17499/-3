#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ handlers/admin.py — Административные функции
✅ Управление пользователями с поиском
✅ Статистика с правильными функциями
✅ Управление админами
✅ Управление базой знаний
"""

import logging
import re
from aiogram import Router, F, types
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, 
    InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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
    get_all_admins,
    get_aerodrome_by_search,
    add_aerodrome,
    add_aerodrome_phone,
    get_safety_block_by_number,
    add_safety_block,
    get_all_safety_blocks,
    add_aircraft_knowledge,
    get_aircraft_knowledge_by_type
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

class AdminKnowledgeState(StatesGroup):
    # Аэродромы
    aero_add_name = State()
    aero_add_city = State()
    aero_add_airport = State()
    aero_add_housing = State()
    aero_add_phone_name = State()
    aero_add_phone_number = State()
    aero_add_doc_name = State()
    aero_add_doc_file = State()
    
    # Блоки безопасности
    safety_add_number = State()
    safety_add_text = State()
    
    # Знания по самолётам
    aircraft_add_type = State()
    aircraft_add_name = State()
    aircraft_add_text = State()
    aircraft_add_file = State()

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
            # ✅ ИСПРАВЛЕНО: используем .get() для словарей
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
            # ✅ ИСПРАВЛЕНО: используем .get() для словарей
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
            # ✅ ИСПРАВЛЕНО: используем .get() для словарей
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
            # ✅ ИСПРАВЛЕНО: используем .get() для словарей
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
        # ✅ ИСПРАВЛЕНО: используем .get() для словарей
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
# УПРАВЛЕНИЕ БАЗОЙ ЗНАНИЙ
# ============================================================

@router.callback_query(F.data == "admin_knowledge")
@admin_required_callback
async def admin_knowledge(callback: CallbackQuery):
    """Меню управления базой знаний"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Аэродромы", callback_data="admin_knowledge_aerodromes")],
        [InlineKeyboardButton(text="🛡️ Блоки безопасности", callback_data="admin_knowledge_safety")],
        [InlineKeyboardButton(text="📖 Знания по самолётам", callback_data="admin_knowledge_aircraft")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions")]
    ])
    
    await callback.message.edit_text(
        "📚 <b>Управление базой знаний</b>\n\n"
        "Выберите раздел:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

# ============================================================
# АЭРОДРОМЫ (АДМИН)
# ============================================================

@router.callback_query(F.data == "admin_knowledge_aerodromes")
@admin_required_callback
async def admin_knowledge_aerodromes(callback: CallbackQuery):
    """Меню управления аэродромами"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить аэродром", callback_data="admin_aero_add")],
        [InlineKeyboardButton(text="📋 Список аэродромов", callback_data="admin_aero_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_knowledge")]
    ])
    
    await callback.message.edit_text(
        "✈️ <b>Управление аэродромами</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_aero_add")
@admin_required_callback
async def admin_aero_add_start(callback: CallbackQuery, state: FSMContext):
    """Начать добавление аэродрома"""
    await callback.message.edit_text(
        "➕ <b>Добавление аэродрома</b>\n\n"
        "Введите название города/аэродрома:\n\n"
        "Пример: Нижний Новгород",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_knowledge_aerodromes")]
        ]),
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aero_add_name)
    await callback.answer()


@router.message(AdminKnowledgeState.aero_add_name)
@admin_required_message
async def admin_aero_add_name(message: Message, state: FSMContext):
    """Обработка названия аэродрома"""
    await state.update_data(aero_name=message.text.strip())
    await message.answer(
        "Теперь введите название аэродрома (если отличается от города):\n\n"
        "Пример: Стригино\n\n"
        "Или напишите 'пропустить':",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_knowledge_aerodromes")]
        ])
    )
    await state.set_state(AdminKnowledgeState.aero_add_airport)


@router.message(AdminKnowledgeState.aero_add_airport)
@admin_required_message
async def admin_aero_add_airport(message: Message, state: FSMContext):
    """Обработка названия аэропорта"""
    airport = message.text.strip()
    if airport.lower() == 'пропустить':
        airport = None
    await state.update_data(aero_airport=airport)
    await message.answer(
        "Введите информацию о жилье:\n\n"
        "Пример: Предоставляется бесплатно / Не предоставляется / Требуется справка",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_knowledge_aerodromes")]
        ])
    )
    await state.set_state(AdminKnowledgeState.aero_add_housing)


@router.message(AdminKnowledgeState.aero_add_housing)
@admin_required_message
async def admin_aero_add_housing(message: Message, state: FSMContext):
    """Обработка информации о жилье"""
    data = await state.get_data()
    add_aerodrome(
        name=data['aero_name'],
        city=data['aero_name'],
        airport_name=data.get('aero_airport'),
        housing_info=message.text.strip(),
        created_by=message.from_user.id
    )
    await message.answer(
        "✅ Аэродром добавлен!\n\n"
        "Теперь добавьте телефоны (или напишите 'готово'):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_knowledge_aerodromes")]
        ])
    )
    await state.set_state(AdminKnowledgeState.aero_add_phone_name)


@router.message(AdminKnowledgeState.aero_add_phone_name)
@admin_required_message
async def admin_aero_add_phone_name(message: Message, state: FSMContext):
    """Обработка названия телефона"""
    if message.text.lower() == 'готово':
        await state.clear()
        await message.answer(
            "✅ Аэродром полностью добавлен!",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Назад")]], resize_keyboard=True)
        )
        return
    await state.update_data(phone_name=message.text.strip())
    await message.answer(
        "Введите номер телефона:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_knowledge_aerodromes")]
        ])
    )
    await state.set_state(AdminKnowledgeState.aero_add_phone_number)


@router.message(AdminKnowledgeState.aero_add_phone_number)
@admin_required_message
async def admin_aero_add_phone_number(message: Message, state: FSMContext):
    """Обработка номера телефона"""
    data = await state.get_data()
    aerodrome = get_aerodrome_by_search(data['aero_name'])
    if aerodrome:
        add_aerodrome_phone(aerodrome['id'], data['phone_name'], message.text.strip())
        await message.answer(
            "✅ Телефон добавлен!\n\n"
            "Добавьте ещё телефон или напишите 'готово':",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_knowledge_aerodromes")]
            ])
        )
        await state.set_state(AdminKnowledgeState.aero_add_phone_name)
    else:
        await message.answer("❌ Ошибка! Аэродром не найден.")
        await state.clear()


@router.callback_query(F.data == "admin_aero_list")
@admin_required_callback
async def admin_aero_list(callback: CallbackQuery):
    """Список аэродромов для админа"""
    try:
        aerodromes = db.get_all_aerodromes_list()
        
        if not aerodromes:
            await callback.answer("✈️ Аэродромов пока нет", show_alert=True)
            return
        
        text = "✈️ <b>Список аэродромов:</b>\n\n"
        keyboard_buttons = []
        
        for aero in aerodromes[:20]:
            name = aero.get('name', 'Неизвестно')
            city = aero.get('city', '')
            airport = aero.get('airport_name', '')
            
            display = f"{name}"
            if city and city != name:
                display += f" ({city})"
            if airport:
                display += f" - {airport}"
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"✈️ {display[:40]}",
                callback_data=f"admin_aero_edit_{aero['id']}"
            )])
        
        keyboard_buttons.append([InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="admin_knowledge_aerodromes"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            f"{text}\nВыберите аэродром для редактирования:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в admin_aero_list: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)

# ============================================================
# БЛОКИ БЕЗОПАСНОСТИ (АДМИН)
# ============================================================

@router.callback_query(F.data == "admin_knowledge_safety")
@admin_required_callback
async def admin_knowledge_safety(callback: CallbackQuery):
    """Меню управления блоками безопасности"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить блок", callback_data="admin_safety_add")],
        [InlineKeyboardButton(text="📋 Список блоков", callback_data="admin_safety_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_knowledge")]
    ])
    
    await callback.message.edit_text(
        "🛡️ <b>Управление блоками безопасности</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_safety_add")
@admin_required_callback
async def admin_safety_add_start(callback: CallbackQuery, state: FSMContext):
    """Начать добавление блока безопасности"""
    await callback.message.edit_text(
        "➕ <b>Добавление блока безопасности</b>\n\n"
        "Введите номер блока:\n\n"
        "Пример: 1",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_knowledge_safety")]
        ]),
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.safety_add_number)
    await callback.answer()


@router.message(AdminKnowledgeState.safety_add_number)
@admin_required_message
async def admin_safety_add_number(message: Message, state: FSMContext):
    """Обработка номера блока"""
    try:
        block_number = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите корректный номер (число)")
        return
    
    # Проверяем что блок с таким номером ещё не существует
    existing = get_safety_block_by_number(block_number)
    if existing:
        await message.answer(f"❌ Блок №{block_number} уже существует!\n\nВведите другой номер:")
        return
    
    await state.update_data(safety_number=block_number)
    await message.answer(
        "Теперь отправьте текст блока:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_knowledge_safety")]
        ])
    )
    await state.set_state(AdminKnowledgeState.safety_add_text)


@router.message(AdminKnowledgeState.safety_add_text)
@admin_required_message
async def admin_safety_add_text(message: Message, state: FSMContext):
    """Обработка текста блока"""
    data = await state.get_data()
    add_safety_block(
        block_number=data['safety_number'],
        block_text=message.text,
        created_by=message.from_user.id
    )
    await message.answer(f"✅ Блок безопасности №{data['safety_number']} добавлен!")
    await state.clear()


@router.callback_query(F.data == "admin_safety_list")
@admin_required_callback
async def admin_safety_list(callback: CallbackQuery):
    """Список блоков для админа"""
    try:
        blocks = get_all_safety_blocks()
        
        if not blocks:
            await callback.answer("🛡️ Блоков пока нет", show_alert=True)
            return
        
        text = "🛡️ <b>Список блоков безопасности:</b>\n\n"
        keyboard_buttons = []
        
        for block in blocks[:20]:
            num = block.get('block_number')
            text_preview = block.get('block_text', '')[:50] + '...' if len(block.get('block_text', '')) > 50 else block.get('block_text', '')
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"🔹 Блок №{num}",
                callback_data=f"admin_safety_edit_{num}"
            )])
        
        keyboard_buttons.append([InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="admin_knowledge_safety"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            f"{text}\nВыберите блок для редактирования:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в admin_safety_list: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)

# ============================================================
# ЗНАНИЯ ПО САМОЛЁТАМ (АДМИН)
# ============================================================

@router.callback_query(F.data == "admin_knowledge_aircraft")
@admin_required_callback
async def admin_knowledge_aircraft(callback: CallbackQuery):
    """Меню управления знаниями по самолётам"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить знание", callback_data="admin_aircraft_add")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_knowledge")]
    ])
    
    await callback.message.edit_text(
        "📖 <b>Управление знаниями по самолётам</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_aircraft_add")
@admin_required_callback
async def admin_aircraft_add_start(callback: CallbackQuery, state: FSMContext):
    """Выбор типа самолёта для добавления знания"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Ил-76 МД", callback_data="aircraft_type_il76md")],
        [InlineKeyboardButton(text="✈️ Ил-76 МД-М", callback_data="aircraft_type_il76mdm")],
        [InlineKeyboardButton(text="✈️ Ил-76 МД-90А", callback_data="aircraft_type_il76md90a")]
    ])
    
    await callback.message.edit_text(
        "➕ <b>Добавление знания по самолёту</b>\n\n"
        "Выберите тип самолёта:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aircraft_add_type)
    await callback.answer()


@router.callback_query(F.data.startswith("aircraft_type_"))
@admin_required_callback
async def admin_aircraft_type_select(callback: CallbackQuery, state: FSMContext):
    """Выбор типа самолёта"""
    aircraft_map = {
        "aircraft_type_il76md": "Ил-76 МД",
        "aircraft_type_il76mdm": "Ил-76 МД-М",
        "aircraft_type_il76md90a": "Ил-76 МД-90А"
    }
    aircraft_type = aircraft_map.get(callback.data)
    await state.update_data(aircraft_type=aircraft_type)
    
    await callback.message.edit_text(
        f"✈️ {aircraft_type}\n\n"
        "Введите название материала:\n\n"
        "Пример: Руководство по эксплуатации",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_knowledge_aircraft")]
        ]),
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aircraft_add_name)
    await callback.answer()


@router.message(AdminKnowledgeState.aircraft_add_name)
@admin_required_message
async def admin_aircraft_add_name(message: Message, state: FSMContext):
    """Обработка названия знания"""
    await state.update_data(knowledge_name=message.text.strip())
    await message.answer(
        "Теперь отправьте текст материала (или напишите 'пропустить' если только файл):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_knowledge_aircraft")]
        ])
    )
    await state.set_state(AdminKnowledgeState.aircraft_add_text)


@router.message(AdminKnowledgeState.aircraft_add_text)
@admin_required_message
async def admin_aircraft_add_text(message: Message, state: FSMContext):
    """Обработка текста знания"""
    text = message.text.strip()
    if text.lower() == 'пропустить':
        text = None
    await state.update_data(knowledge_text=text)
    
    data = await state.get_data()
    add_aircraft_knowledge(
        aircraft_type=data['aircraft_type'],
        knowledge_name=data['knowledge_name'],
        knowledge_text=data.get('knowledge_text')
    )
    
    await message.answer("✅ Знание добавлено!")
    await state.clear()

# ============================================================
# ОСТАЛЬНЫЕ ФУНКЦИИ (заглушки)
# ============================================================

@router.callback_query(F.data == "admin_fill_airports")
@admin_required_callback
async def admin_fill_airports(callback: CallbackQuery):
    """Заполнить базу аэродромов (заглушка)"""
    await callback.answer("⚠️ Функция в разработке", show_alert=True)


@router.callback_query(F.data == "admin_knowledge")
@admin_required_callback
async def admin_knowledge_stub(callback: CallbackQuery):
    """Управление базой знаний (заглушка)"""
    await callback.answer("⚠️ Функция в разработке", show_alert=True)
