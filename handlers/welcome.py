#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👋 handlers/welcome.py
Обработчики приветствий: /start в ЛС и сообщения в группе
✅ Главное меню с 2 кнопками + админская
✅ Команда /menu
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from config import TOPIC_ID, GROUP_ID, ADMIN_IDS
from db_manager import get_user, add_user
from states import RegistrationState

logger = logging.getLogger(__name__)
router = Router()

# Кэш приветствованных пользователей в группе
welcomed_users: set[int] = set()

# ============================================================
# ГЛАВНОЕ МЕНЮ — КЛАВИАТУРА (2 кнопки + админская)
# ============================================================

def make_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Создать клавиатуру главного меню"""
    keyboard = [
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="📚 Полезная информация")]
    ]
    
    if is_admin:
        keyboard.append([KeyboardButton(text="🛡 Административные функции")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

# ============================================================
# КОМАНДА /start — ГЛАВНОЕ МЕНЮ
# ============================================================

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Сбрасываем все состояния
    await state.clear()
    
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "Пользователь"
    
    # Проверяем админ-статус
    from db_manager import db
    is_admin_user = user_id in ADMIN_IDS or db.check_admin_status(user_id, username)
    
    # Добавляем пользователя в БД если новый
    user = get_user(user_id)
    if not user:
        add_user(user_id, username)
        logger.info(f"✅ Новый пользователь {user_id} добавлен в БД")
    
    # Создаем клавиатуру
    keyboard = make_main_menu_keyboard(is_admin=is_admin_user)
    
    # Проверяем регистрацию
    if user and user.get('is_registered'):
        # Зарегистрирован — показываем меню
        await message.answer(
            f"👋 Привет, {first_name}!\n\n"
            "Я — бот 81-го полка ✈️\n\n"
            "Выберите действие:",
            reply_markup=keyboard
        )
        logger.info(f"✅ /start: пользователь {user_id} уже зарегистрирован")
    else:
        # Не зарегистрирован — предлагаем регистрацию
        await message.answer(
            f"👋 Привет, {first_name}!\n\n"
            "Я — бот 81-го полка ✈️\n\n"
            "<b>Для полного доступа пройди регистрацию:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        logger.info(f"✅ /start: новый пользователь {user_id} добавлен в БД")

# ============================================================
# КОМАНДА /menu — ПОКАЗАТЬ ГЛАВНОЕ МЕНЮ
# ============================================================

@router.message(F.text == "/menu")
async def cmd_menu(message: Message, state: FSMContext):
    """Команда для показа главного меню"""
    await state.clear()
    
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "Пользователь"
    
    # Проверяем админ-статус
    from db_manager import db
    is_admin_user = user_id in ADMIN_IDS or db.check_admin_status(user_id, username)
    
    # Проверяем регистрацию
    user = get_user(user_id)
    if not user or not user.get('is_registered'):
        await message.answer(
            "⚠️ Сначала завершите регистрацию!\n\n"
            "Нажмите /start или кнопку '📝 Регистрация'",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Показываем меню
    keyboard = make_main_menu_keyboard(is_admin=is_admin_user)
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
    
    # Если уже зарегистрирован — напоминаем
    if user and user.get('is_registered'):
        await message.answer(
            "✅ Ты уже зарегистрирован!\n\n"
            "Используй меню для навигации.",
            reply_markup=make_main_menu_keyboard()
        )
        return
    
    # Запускаем FSM регистрацию
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
# ПРИВЕТСТВИЕ В ГРУППЕ (в нужной теме)
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
    lambda msg: msg.from_user.id not in welcomed_users 
    and _is_in_correct_topic(msg)
    and not msg.from_user.is_bot
)
async def group_first_message_handler(message: Message):
    """Приветствие при первом сообщении пользователя в группе"""
    user_id = message.from_user.id
    welcomed_users.add(user_id)
    
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
    """Приветствие нового участника в группе"""
    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue
        
        user_id = new_member.id
        if user_id in welcomed_users:
            continue
        
        welcomed_users.add(user_id)
        
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
