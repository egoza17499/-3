#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 handlers/menu.py — Главное меню бота
✅ Постоянная клавиатура внизу экрана
✅ Проверка регистрации
✅ Исправлен импорт Message
"""

import logging
from aiogram import Router, F, types  # ✅ Убрали Message отсюда
from aiogram.types import (  # ✅ Добавили Message сюда
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton,
    Message  # ✅ Message импортируем из правильного места
)
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from validators import generate_profile_text, check_flight_ban
from db_manager import db, get_user
from utils.registration_check import registration_required

logger = logging.getLogger(__name__)  # ✅ __name__ правильно
router = Router()

def get_main_keyboard(is_admin=False):
    """Создать главную клавиатуру"""
    keyboard = [
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="📚 Полезная информация")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="🛡 Административные функции")])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(F.text == "👤 Мой профиль")
@registration_required  # ✅ ПРОВЕРКА РЕГИСТРАЦИИ
async def show_profile(message: Message):  # ✅ Message теперь определён
    """Показать профиль пользователя"""
    user = db.get_user(message.from_user.id)
    
    if not user:
        await message.answer("❌ Ошибка: пользователь не найден")
        return
    
    profile_text = generate_profile_text(user)
    
    # Проверяем запреты на полёты
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\n🔴 <b>ПОЛЁТЫ ЗАПРЕЩЕНЫ:</b>\n" + "\n".join(bans)
    
    # Inline-кнопки для профиля
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile")],
    ])
    
    await message.answer(profile_text, reply_markup=keyboard, parse_mode="HTML")

@router.message(F.text == "📚 Полезная информация")
@registration_required  # ✅ ПРОВЕРКА РЕГИСТРАЦИИ
async def show_info(message: Message):  # ✅ Message теперь определён
    """Показать меню полезной информации"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛡️ Блоки по безопасности полетов", callback_data="info_safety")],
        [InlineKeyboardButton(text="✈️ Поиск информации об аэродроме", callback_data="info_aerodrome")],
        [InlineKeyboardButton(text="📖 Полезные знания по самолету", callback_data="info_aircraft")],
    ])
    
    await message.answer(
        "📚 <b>Полезная информация</b>\n\n"
        "Выберите раздел:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.message(F.text == "🛡 Административные функции")
@registration_required  # ✅ ПРОВЕРКА РЕГИСТРАЦИИ
async def admin_functions(message: Message):  # ✅ Message теперь определён
    """Админское меню"""
    user_id = message.from_user.id
    
    if user_id not in ADMIN_IDS and not db.check_admin_status(user_id, message.from_user.username):
        await message.answer("❌ У вас нет доступа")
        return
    
    # Показываем админское меню
    from handlers.admin import get_admin_keyboard
    await message.answer(
        "🛡 <b>Административные функции</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )
