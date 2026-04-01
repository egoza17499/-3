#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👋 handlers/welcome.py
Обработчики приветствий: /start в ЛС и сообщения в группе
✅ Только 1 приветствие на пользователя
✅ Лимит 5 сообщений в сутки в группе
✅ Работает только в своей теме
"""

import logging
import time
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from config import TOPIC_ID, GROUP_ID, ADMIN_IDS
from db_manager import get_user, add_user, db
from states import RegistrationState

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# КЭШИРОВАНИЕ ПРИВЕТСТВИЙ (с лимитом 5 сообщений в сутки)
# ============================================================

# Хранилище: {user_id: {'count': int, 'date': str, 'welcomed': bool}}
user_message_stats = {}

def get_user_daily_stats(user_id: int) -> dict:
    """Получить статистику сообщений пользователя за сегодня"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if user_id not in user_message_stats:
        user_message_stats[user_id] = {
            'count': 0,
            'date': today,
            'welcomed': False
        }
    
    # Если новый день — сбрасываем счётчик
    if user_message_stats[user_id]['date'] != today:
        user_message_stats[user_id] = {
            'count': 0,
            'date': today,
            'welcomed': user_message_stats[user_id].get('welcomed', False)
        }
    
    return user_message_stats[user_id]

def can_send_message(user_id: int) -> bool:
    """Проверить можно ли отправить сообщение пользователю (лимит 5 в сутки)"""
    stats = get_user_daily_stats(user_id)
    return stats['count'] < 5

def increment_message_count(user_id: int):
    """Увеличить счётчик сообщений пользователя"""
    stats = get_user_daily_stats(user_id)
    stats['count'] += 1

def was_user_welcomed(user_id: int) -> bool:
    """Проверить был ли пользователь уже приветствован"""
    stats = get_user_daily_stats(user_id)
    return stats.get('welcomed', False)

def mark_user_welcomed(user_id: int):
    """Отметить пользователя как приветствованного"""
    stats = get_user_daily_stats(user_id)
    stats['welcomed'] = True

# ============================================================
# ГЛАВНОЕ МЕНЮ — КЛАВИАТУРА
# ============================================================

def make_main_menu_keyboard(is_admin: bool = False, show_registration: bool = False) -> ReplyKeyboardMarkup:
    """Создать клавиатуру главного меню"""
    keyboard = []
    
    # Кнопка регистрации — только для незарегистрированных
    if show_registration:
        keyboard.append([KeyboardButton(text="📝 Регистрация")])
    
    keyboard.append([KeyboardButton(text="👤 Мой профиль")])
    keyboard.append([KeyboardButton(text="📚 Полезная информация")])
    
    if is_admin:
        keyboard.append([KeyboardButton(text="🛡 Административные функции")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

# ============================================================
# КОМАНДА /start В ЛИЧНЫХ СООБЩЕНИЯХ
# ============================================================

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    if message.chat.type in ['group', 'supergroup']:
        return
    
    await state.clear()
    
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "Пользователь"
    
    is_admin_user = user_id in ADMIN_IDS or db.check_admin_status(user_id, username)
    
    user = get_user(user_id)
    if not user:
        add_user(user_id, username)
        logger.info(f"✅ Новый пользователь {user_id} добавлен в БД")
        user = get_user(user_id)
    
    is_registered = user and user.get('is_registered')
    show_registration = not is_registered
    
    keyboard = make_main_menu_keyboard(
        is_admin=is_admin_user,
        show_registration=show_registration
    )
    
    if is_registered:
        await message.answer(
            f"👋 Привет, {first_name}!\n\n"
            "Я — бот 81-го полка ✈️\n\n"
            "Выберите действие:",
            reply_markup=keyboard
        )
        logger.info(f"✅ /start: пользователь {user_id} уже зарегистрирован")
    else:
        await message.answer(
            f"👋 Привет, {first_name}!\n\n"
            "Я — бот 81-го полка ✈️\n\n"
            "<b>Для полного доступа пройди регистрацию:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        logger.info(f"✅ /start: незарегистрированный пользователь {user_id}")

# ============================================================
# КОМАНДА /menu
# ============================================================

@router.message(F.text == "/menu")
async def cmd_menu(message: Message, state: FSMContext):
    """Команда для показа главного меню"""
    await state.clear()
    
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "Пользователь"
    
    is_admin_user = user_id in ADMIN_IDS or db.check_admin_status(user_id, username)
    
    user = get_user(user_id)
    if not user or not user.get('is_registered'):
        keyboard = make_main_menu_keyboard(is_admin=False, show_registration=True)
        await message.answer(
            f"👋 Привет, {first_name}!\n\n"
            "<b>Для полного доступа пройди регистрацию:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return
    
    keyboard = make_main_menu_keyboard(is_admin=is_admin_user, show_registration=False)
    await message.answer(
        f"👋 Привет, {first_name}!\n\n"
        "Главное меню:",
        reply_markup=keyboard
    )

# ============================================================
# ОБРАБОТЧИК КНОПКИ "📝 Регистрация"
# ============================================================

@router.message(F.text == "📝 Регистрация")
async def start_registration_from_menu(message: Message, state: FSMContext):
    """Запуск регистрации из главного меню"""
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if user and user.get('is_registered'):
        is_admin_user = user_id in ADMIN_IDS or db.check_admin_status(user_id, message.from_user.username)
        keyboard = make_main_menu_keyboard(is_admin=is_admin_user, show_registration=False)
        await message.answer(
            "✅ Ты уже зарегистрирован!\n\n"
            "Используй меню для навигации.",
            reply_markup=keyboard
        )
        return
    
    await state.set_state(RegistrationState.fio)
    await message.answer(
        "📝 <b>Начинаем регистрацию!</b>\n\n"
        "Шаг 1 из 12\n\n"
        "Введи своё <b>ФИО</b> полностью:\n"
        "<i>Например: Иванов Иван Иванович</i>",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    logger.info(f"✅ Регистрация начата пользователем {user_id}")

# ============================================================
# ПРИВЕТСТВИЕ В ГРУППЕ (с лимитами)
# ============================================================

def _is_in_correct_topic(message: Message) -> bool:
    """Проверить что сообщение в нужной группе и теме"""
    if message.chat.id != GROUP_ID:
        return False
    if TOPIC_ID and message.message_thread_id != TOPIC_ID:
        return False
    return True

@router.message(
    F.chat.type.in_(['group', 'supergroup']),
    F.text,
    lambda msg: not msg.from_user.is_bot
)
async def group_first_message_handler(message: Message):
    """
    Обработчик первого сообщения пользователя в группе.
    ✅ Только 1 приветствие на пользователя
    ✅ Лимит 5 сообщений в сутки
    ✅ Только в своей теме
    """
    # Проверяем тему
    if not _is_in_correct_topic(message):
        return
    
    user_id = message.from_user.id
    
    # Проверяем лимит сообщений в сутки
    if not can_send_message(user_id):
        logger.info(f"⏭️ Превышен лимит сообщений для пользователя {user_id}")
        return
    
    # Проверяем было ли уже приветствие
    if was_user_welcomed(user_id):
        return
    
    # Отмечаем что приветствовали
    mark_user_welcomed(user_id)
    increment_message_count(user_id)
    
    bot_link = "https://t.me/help_81polk_bot"
    welcome_text = (
        f"Здравствуйте, {message.from_user.full_name}! 👋\n\n"
        f"Я — бот 81-го полка. Помогаю с информацией об аэродромах, "
        f"телефонах и блоках безопасности.\n\n"
        f"🔗 <b>Ссылка на бота:</b> {bot_link}\n\n"
        f"💡 <i>Для начала работы перейдите по ссылке и нажмите /start</i>"
    )
    
    try:
        await message.answer(
            text=welcome_text,
            reply_to_message_id=message.message_id,
            parse_mode="HTML"
        )
        logger.info(f"✅ Приветствие отправлено пользователю {user_id} в группе")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки приветствия: {e}")

@router.message(
    F.chat.type.in_(['group', 'supergroup']),
    F.new_chat_members,
    lambda msg: _is_in_correct_topic(msg)
)
async def on_new_member_join(message: Message):
    """Приветствие нового участника в группе (с лимитами)"""
    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue
        
        user_id = new_member.id
        
        # Проверяем лимит
        if not can_send_message(user_id):
            logger.info(f"⏭️ Превышен лимит сообщений для нового участника {user_id}")
            return
        
        # Проверяем было ли приветствие
        if was_user_welcomed(user_id):
            return
        
        # Отмечаем что приветствовали
        mark_user_welcomed(user_id)
        increment_message_count(user_id)
        
        bot_link = "https://t.me/help_81polk_bot"
        welcome_text = (
            f"Здравствуйте, {new_member.full_name}! 👋\n\n"
            f"Я — бот 81-го полка. Помогаю с информацией об аэродромах, "
            f"телефонах и блоках безопасности.\n\n"
            f"🔗 <b>Ссылка на бота:</b> {bot_link}\n\n"
            f"💡 <i>Для начала работы перейдите по ссылке и нажмите /start</i>"
        )
        
        try:
            await message.answer(
                text=welcome_text,
                reply_to_message_id=message.message_id,
                parse_mode="HTML"
            )
            logger.info(f"✅ Приветствие отправлено новому участнику {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки приветствия: {e}")
