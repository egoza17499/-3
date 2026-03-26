#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ handlers/admin.py — Административные функции
✅ Управление пользователями
✅ Статистика
✅ Управление админами
✅ Управление базой данных
"""

import logging
from aiogram import Router, F, types
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, 
    InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from db_manager import (
    db, get_all_users, get_user, update_user, 
    delete_user, search_users, add_admin, remove_admin,
    get_all_admins, get_all_aerodromes_list, add_aerodrome,
    update_aerodrome, delete_aerodrome
)
from states import AdminState
from utils.admin_check import admin_required, admin_required_callback, admin_required_message

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Создать клавиатуру административных функций"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_list")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📚 Управление базой знаний", callback_data="admin_knowledge")],
        [InlineKeyboardButton(text="✈️ Заполнить базу аэродромов", callback_data="admin_aerodromes")],
        [InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_manage")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])


def get_user_management_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура управления пользователем"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"admin_edit_user_{user_id}")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"admin_delete_user_{user_id}")],
        [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")]
    ])


def get_edit_user_fields_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 ФИО", callback_data=f"admin_edit_field_{user_id}_fio")],
        [InlineKeyboardButton(text="🎖 Звание", callback_data=f"admin_edit_field_{user_id}_rank")],
        [InlineKeyboardButton(text="🏅 Квалификация", callback_data=f"admin_edit_field_{user_id}_qualification")],
        [InlineKeyboardButton(text="📅 Отпуск (начало)", callback_data=f"admin_edit_field_{user_id}_leave_start_date")],
        [InlineKeyboardButton(text="📅 Отпуск (конец)", callback_data=f"admin_edit_field_{user_id}_leave_end_date")],
        [InlineKeyboardButton(text="🏥 ВЛК", callback_data=f"admin_edit_field_{user_id}_vlk_date")],
        [InlineKeyboardButton(text="🔬 УМО", callback_data=f"admin_edit_field_{user_id}_umo_date")],
        [InlineKeyboardButton(text="✈️ КБП-4 МД-М", callback_data=f"admin_edit_field_{user_id}_exercise_4_md_m_date")],
        [InlineKeyboardButton(text="✈️ КБП-7 МД-М", callback_data=f"admin_edit_field_{user_id}_exercise_7_md_m_date")],
        [InlineKeyboardButton(text="✈️ КБП-4 МД-90А", callback_data=f"admin_edit_field_{user_id}_exercise_4_md_90a_date")],
        [InlineKeyboardButton(text="✈️ КБП-7 МД-90А", callback_data=f"admin_edit_field_{user_id}_exercise_7_md_90a_date")],
        [InlineKeyboardButton(text="🪂 Парашют", callback_data=f"admin_edit_field_{user_id}_parachute_jump_date")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_list")]
    ])


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
# СПИСОК ПОЛЬЗОВАТЕЛЕЙ
# ============================================================

@router.callback_query(F.data == "admin_list")
@admin_required_callback
async def admin_list(callback: CallbackQuery):
    """Показать список всех пользователей"""
    try:
        users = get_all_users()
        
        if not users:
            await callback.answer("📋 Пользователей пока нет", show_alert=True)
            return
        
        text = f"📋 <b>Список пользователей</b>\n\n"
        text += f"Всего: {len(users)}\n\n"
        
        keyboard_buttons = []
        
        for user in users[:20]:  # Показываем максимум 20
            # ✅ ИСПРАВЛЕНО: user — это dict, используем .get()
            user_id = user.get('user_id', 0)
            fio = user.get('fio', 'Не указано')
            username = user.get('username', 'N/A')
            rank = user.get('rank', 'Не указано')
            
            # Обрезаем ФИО если длинное
            fio_short = fio[:30] + '...' if len(fio) > 30 else fio
            
            text += f"👤 {fio_short}\n"
            text += f"   @{username}\n"
            text += f"   {rank}\n\n"
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"👤 {fio_short}",
                callback_data=f"admin_user_profile_{user_id}"
            )])
        
        keyboard_buttons.append([InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="admin_functions"
        )])
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_list: {e}")
        await callback.answer("❌ Ошибка при получении списка", show_alert=True)


@router.callback_query(F.data.startswith("admin_user_profile_"))
@admin_required_callback
async def admin_user_profile(callback: CallbackQuery):
    """Показать профиль пользователя (админ)"""
    try:
        user_id = int(callback.data.split("_")[-1])
        user = get_user(user_id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        from validators import generate_profile_text, check_flight_ban
        
        text = f"👤 <b>Профиль пользователя</b>\n\n"
        text += generate_profile_text(user)
        
        # Проверяем запреты
        bans = check_flight_ban(user)
        if bans:
            text += "\n\n🔴 <b>ПОЛЁТЫ ЗАПРЕЩЕНЫ:</b>\n" + "\n".join(bans)
        
        keyboard = get_user_management_keyboard(user_id)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_user_profile: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ============================================================
# СТАТИСТИКА
# ============================================================

@router.callback_query(F.data == "admin_stats")
@admin_required_callback
async def admin_stats(callback: CallbackQuery):
    """Показать статистику"""
    try:
        users = get_all_users()
        admins = get_all_admins()
        aerodromes = get_all_aerodromes_list()
        
        # Считаем зарегистрированных
        registered_count = len([u for u in users if u.get('is_registered')])
        
        # Считаем тех кто может летать
        from validators import check_flight_ban
        can_fly = len([u for u in users if not check_flight_ban(u)])
        cannot_fly = len([u for u in users if check_flight_ban(u)])
        
        text = "📊 <b>Статистика бота</b>\n\n"
        text += f"👥 <b>Пользователи:</b>\n"
        text += f"   Всего: {len(users)}\n"
        text += f"   Зарегистрировано: {registered_count}\n"
        text += f"   Не завершили регистрацию: {len(users) - registered_count}\n\n"
        
        text += f"🛡️ <b>Админы:</b> {len(admins)}\n\n"
        
        text += f"✈️ <b>Аэродромы:</b> {len(aerodromes)}\n\n"
        
        text += f"🪂 <b>Лётный статус:</b>\n"
        text += f"   ✅ Могут летать: {can_fly}\n"
        text += f"   🔴 Не могут летать: {cannot_fly}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_stats: {e}")
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)


# ============================================================
# УПРАВЛЕНИЕ АДМИНАМИ
# ============================================================

@router.callback_query(F.data == "admin_manage")
@admin_required_callback
async def admin_manage(callback: CallbackQuery):
    """Меню управления админами"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить админа", callback_data="admin_add_admin")],
        [InlineKeyboardButton(text="➖ Удалить админа", callback_data="admin_remove_admin")],
        [InlineKeyboardButton(text="📋 Список админов", callback_data="admin_list_admins")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions")]
    ])
    
    await callback.message.edit_text(
        "👥 <b>Управление админами</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_admin")
@admin_required_callback
async def admin_add_admin(callback: CallbackQuery, state: FSMContext):
    """Добавить админа"""
    await state.set_state(AdminState.waiting_for_admin_id)
    await callback.message.edit_text(
        "➕ <b>Добавление админа</b>\n\n"
        "Отправьте <b>ID пользователя</b> которого хотите сделать админом:\n\n"
        "<i>Или перешлите сообщение от этого пользователя</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_manage")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_remove_admin")
@admin_required_callback
async def admin_remove_admin(callback: CallbackQuery, state: FSMContext):
    """Удалить админа"""
    await state.set_state(AdminState.waiting_for_admin_id)
    await callback.message.edit_text(
        "➖ <b>Удаление админа</b>\n\n"
        "Отправьте <b>ID админа</b> которого хотите удалить:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_manage")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_list_admins")
@admin_required_callback
async def admin_list_admins(callback: CallbackQuery):
    """Список админов"""
    try:
        admins = get_all_admins()
        
        if not admins:
            await callback.answer("👥 Админов пока нет", show_alert=True)
            return
        
        text = "👥 <b>Список админов</b>\n\n"
        for admin in admins:
            # ✅ ИСПРАВЛЕНО: admin — это dict
            admin_id = admin.get('user_id', 'N/A')
            username = admin.get('username', 'N/A')
            added_at = admin.get('added_at', 'N/A')
            
            text += f"🔹 ID: {admin_id}\n"
            text += f"   Username: @{username}\n"
            text += f"   Добавлен: {added_at}\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_manage")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_list_admins: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.message(AdminState.waiting_for_admin_id)
@admin_required_message
async def process_admin_id(message: Message, state: FSMContext):
    """Обработка ID админа"""
    try:
        # Проверяем пересылку сообщения
        if message.forward_from:
            target_user_id = message.forward_from.id
        else:
            # Парсим ID из текста
            target_user_id = int(message.text.strip())
        
        callback_data = message.text.strip()
        
        if "add" in callback_data or "➕" in callback_data:
            # Добавляем админа
            add_admin(target_user_id, "", message.from_user.id)
            await message.answer(
                f"✅ Пользователь {target_user_id} добавлен в админы!",
                reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Назад")]], resize_keyboard=True)
            )
        elif "remove" in callback_data or "➖" in callback_data:
            # Удаляем админа
            remove_admin(target_user_id)
            await message.answer(
                f"✅ Пользователь {target_user_id} удалён из админов!",
                reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Назад")]], resize_keyboard=True)
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Неверный формат ID. Отправьте числовое ID пользователя.")
    except Exception as e:
        logger.error(f"Ошибка в process_admin_id: {e}")
        await message.answer("❌ Произошла ошибка")


# ============================================================
# РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ
# ============================================================

@router.callback_query(F.data.startswith("admin_edit_user_"))
@admin_required_callback
async def admin_edit_user(callback: CallbackQuery):
    """Выбор поля для редактирования"""
    try:
        user_id = int(callback.data.split("_")[-1])
        user = get_user(user_id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        fio = user.get('fio', 'Не указано')
        
        await callback.message.edit_text(
            f"✏️ <b>Редактирование пользователя</b>\n\n"
            f"👤 {fio}\n\n"
            "Выберите поле для редактирования:",
            reply_markup=get_edit_user_fields_keyboard(user_id),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_edit_user: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("admin_edit_field_"))
@admin_required_callback
async def admin_edit_field(callback: CallbackQuery, state: FSMContext):
    """Редактирование конкретного поля"""
    try:
        # Парсим callback_data: admin_edit_field_{user_id}_{field}
        parts = callback.data.split("_")
        user_id = int(parts[3])
        field = "_".join(parts[4:])  # На случай если поле содержит подчёркивания
        
        await state.update_data(edit_user_id=user_id, edit_field=field)
        await state.set_state(AdminState.waiting_for_field_value)
        
        field_names = {
            'fio': 'ФИО',
            'rank': 'Звание',
            'qualification': 'Квалификация',
            'leave_start_date': 'Отпуск (начало)',
            'leave_end_date': 'Отпуск (конец)',
            'vlk_date': 'ВЛК',
            'umo_date': 'УМО',
            'exercise_4_md_m_date': 'КБП-4 МД-М',
            'exercise_7_md_m_date': 'КБП-7 МД-М',
            'exercise_4_md_90a_date': 'КБП-4 МД-90А',
            'exercise_7_md_90a_date': 'КБП-7 МД-90А',
            'parachute_jump_date': 'Парашют'
        }
        
        field_name = field_names.get(field, field)
        
        await callback.message.edit_text(
            f"✏️ <b>Введите новое значение</b>\n\n"
            f"Поле: {field_name}\n\n"
            "Отправьте новое значение:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_user_profile_{user_id}")]
            ]),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_edit_field: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.message(AdminState.waiting_for_field_value)
@admin_required_message
async def process_field_value(message: Message, state: FSMContext):
    """Сохранение нового значения поля"""
    try:
        data = await state.get_data()
        user_id = data.get('edit_user_id')
        field = data.get('edit_field')
        new_value = message.text.strip()
        
        if not user_id or not field:
            await message.answer("❌ Ошибка: данные не найдены")
            return
        
        # Обновляем пользователя
        update_user(user_id, **{field: new_value})
        
        await message.answer(
            f"✅ Поле <b>{field}</b> обновлено!\n\n"
            f"Новое значение: {new_value}",
            parse_mode="HTML"
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка в process_field_value: {e}")
        await message.answer("❌ Произошла ошибка")


# ============================================================
# УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
# ============================================================

@router.callback_query(F.data.startswith("admin_delete_user_"))
@admin_required_callback
async def admin_delete_user(callback: CallbackQuery):
    """Удаление пользователя"""
    try:
        user_id = int(callback.data.split("_")[-1])
        user = get_user(user_id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        fio = user.get('fio', 'Неизвестно')
        
        # Показываем подтверждение
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"admin_confirm_delete_{user_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_user_profile_{user_id}")]
        ])
        
        await callback.message.edit_text(
            f"🗑️ <b>Удаление пользователя</b>\n\n"
            f"Вы действительно хотите удалить пользователя?\n\n"
            f"👤 {fio}\n"
            f"ID: {user_id}\n\n"
            "<b>⚠️ Это действие нельзя отменить!</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_delete_user: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("admin_confirm_delete_"))
@admin_required_callback
async def admin_confirm_delete(callback: CallbackQuery):
    """Подтверждение удаления пользователя"""
    try:
        user_id = int(callback.data.split("_")[-1])
        
        success = delete_user(user_id)
        
        if success:
            await callback.message.edit_text(
                f"✅ Пользователь {user_id} успешно удалён!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")]
                ])
            )
        else:
            await callback.message.edit_text("❌ Ошибка при удалении пользователя")
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_confirm_delete: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ============================================================
# НАЗАД В ГЛАВНОЕ МЕНЮ
# ============================================================

@router.callback_query(F.data == "admin_functions_back")
@admin_required_callback
async def admin_functions_back(callback: CallbackQuery):
    """Вернуться в админское меню"""
    await callback.message.edit_text(
        "🛡️ <b>Административные функции</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    """Вернуться в главное меню"""
    from handlers.menu import get_main_keyboard
    
    user_id = callback.from_user.id
    is_admin_user = user_id in ADMIN_IDS or db.check_admin_status(user_id, callback.from_user.username)
    
    await callback.message.edit_text(
        "📱 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard(is_admin=is_admin_user),
        parse_mode="HTML"
    )
    await callback.answer()
