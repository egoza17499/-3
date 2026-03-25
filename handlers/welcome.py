#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👋 handlers/welcome.py
Обработчики приветствий: /start в ЛС и сообщения в группе
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from config import TOPIC_ID, GROUP_ID
from db_manager import get_user, add_user, set_registration_complete
from states import RegistrationState

logger = logging.getLogger(__name__)
router = Router()

# Кэш приветствованных пользователей в группе (сбрасывается при перезапуске — это нормально)
welcomed_users: set[int] = set()


# ============================================================
# ГЛАВНОЕ МЕНЮ — КЛАВИАТУРА
# ============================================================

def make_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Создать клавиатуру главного меню"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Регистрация")],
            [KeyboardButton(text="👤 Мой профиль")],
            [KeyboardButton(text="🔍 Поиск аэродрома")],
            [KeyboardButton(text="📚 Полезная информация")],
            [KeyboardButton(text="🛡️ Блоки безопасности")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


# ============================================================
# ОБРАБОТЧИК /start В ЛИЧНЫХ СООБЩЕНИЯХ
# ============================================================

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработчик команды /start в личных сообщениях.
    - Если пользователь уже зарегистрирован — показывает главное меню
    - Если нет — добавляет в БД и предлагает зарегистрироваться
    """
    
    # Если это группа — пропускаем (там работает другой обработчик)
    if message.chat.type in ['group', 'supergroup']:
        return
    
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "Пользователь"
    
    # Сбрасываем состояние если было
    await state.clear()
    
    # Проверяем — не зарегистрирован ли уже
    user = get_user(user_id)
    
    if user and user.get('is_registered'):
        # Уже зарегистрирован — показываем главное меню
        await message.answer(
            f"👋 Привет, {first_name}!\n\n"
            "Я — бот 81-го полка. Помогаю с:\n"
            "• 🗺 Информацией об аэродромах и телефонах\n"
            "• 🏠 Данные о жилье по линии МО РФ\n"
            "• 📋 Блоками безопасности и документами\n"
            "• 📊 Отслеживанием сроков ВЛК, УМО, КБП",
            reply_markup=make_main_menu_keyboard(),
            parse_mode="HTML"
        )
        logger.info(f"✅ /start: пользователь {user_id} уже зарегистрирован")
        return
    
    # Новый пользователь — добавляем в БД
    add_user(user_id, username)
    
    # Показываем меню с предложением зарегистрироваться
    await message.answer(
        f"👋 Привет, {first_name}!\n\n"
        "Я — бот 81-го полка ✈️\n\n"
        "Помогаю лётчикам с:\n"
        "• 🗺 Информацией об аэродромах и телефонах\n"
        "• 🏠 Данные о жилье по линии МО РФ\n"
        "• 📋 Блоками безопасности и документами\n"
        "• 📊 Отслеживанием сроков ВЛК, УМО, КБП\n\n"
        "<b>Для полного доступа пройди регистрацию:</b>",
        reply_markup=make_main_menu_keyboard(),
        parse_mode="HTML"
    )
    
    logger.info(f"✅ /start: новый пользователь {user_id} добавлен в БД")


# ============================================================
# ОБРАБОТЧИК КНОПКИ "📝 Регистрация"
# ============================================================

@router.message(F.text == "📝 Регистрация")
async def start_registration_from_menu(message: Message, state: FSMContext):
    """Запуск регистрации по кнопке из главного меню"""
    
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
    # Проверка что это наша группа
    if message.chat.id != GROUP_ID:
        return False
    
    # Если TOPIC_ID задан — проверяем что сообщение в этой теме
    if TOPIC_ID and message.message_thread_id != TOPIC_ID:
        return False
    
    return True


@router.message(
    F.chat.type.in_(['group', 'supergroup']),
    F.text,
    # Только первое текстовое сообщение пользователя в чате
    lambda msg: msg.from_user.id not in welcomed_users 
    and _is_in_correct_topic(msg)
    and not msg.from_user.is_bot
)
async def group_first_message_handler(message: Message):
    """
    Обработчик первого текстового сообщения пользователя в группе.
    Отправляет приветствие с ссылкой на бота.
    """
    
    user_id = message.from_user.id
    
    # Если уже приветствовали — пропускаем
    if user_id in welcomed_users:
        return
    
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
        logger.error(f"❌ Ошибка отправки приветствия пользователю {user_id}: {e}")


# ============================================================
# ОБРАБОТЧИК ВХОДА НОВОГО УЧАСТНИКА В ГРУППУ
# ============================================================

@router.message(
    F.chat.type.in_(['group', 'supergroup']),
    F.new_chat_members,
    lambda msg: _is_in_correct_topic(msg)
)
async def on_new_member_join(message: Message):
    """Обработчик входа нового участника в группу"""
    
    for new_member in message.new_chat_members:
        # Пропускаем ботов
        if new_member.is_bot:
            continue
        
        user_id = new_member.id
        
        # Если уже приветствовали — пропускаем
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
            logger.error(f"❌ Ошибка отправки приветствия новому участнику {user_id}: {e}")
