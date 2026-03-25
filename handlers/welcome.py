#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👋 Обработчик приветствий в группе
Отправляет приветственное сообщение новым участникам в нужной теме
"""

import logging
from aiogram import Router, F, types
from aiogram.filters import ChatMemberUpdatedFilter, MEMBER
from aiogram.types import Message, ChatMemberUpdated
from config import TOPIC_ID, GROUP_ID

logger = logging.getLogger(__name__)
router = Router()

# Кэш приветствованных пользователей (сбрасывается при перезапуске — это нормально)
welcomed_users: set[int] = set()

def _is_in_correct_topic(message: Message) -> bool:
    """Проверить что сообщение в нужной группе и теме"""
    # Проверка что это наша группа
    if message.chat.id != GROUP_ID:
        return False
    
    # Если TOPIC_ID задан — проверяем что сообщение в этой теме
    if TOPIC_ID and message.message_thread_id != TOPIC_ID:
        return False
    
    return True

@router.chat_member(ChatMemberUpdatedFilter(MEMBER))
async def on_new_member_join(event: ChatMemberUpdated):
    """Обработчик входа нового участника в группу"""
    
    # Проверяем что это наша группа
    if event.chat.id != GROUP_ID:
        return
    
    # Проверяем что это не бот
    if event.new_chat_member.user.is_bot:
        return
    
    user_id = event.new_chat_member.user.id
    full_name = event.new_chat_member.user.full_name
    
    # Если уже приветствовали — пропускаем
    if user_id in welcomed_users:
        return
    
    welcomed_users.add(user_id)
    
    bot_link = "https://t.me/help_81polk_bot"
    welcome_text = (
        f"Здравствуйте, {full_name}! 👋\n\n"
        f"Я — бот 81-го полка. Помогаю с информацией об аэродромах, "
        f"телефонах и блоках безопасности.\n\n"
        f"🔗 <b>Ссылка на бота:</b> {bot_link}\n\n"
        f"💡 <i>Для начала работы перейдите по ссылке и нажмите /start</i>"
    )
    
    try:
        # Отправляем приветствие в ту же тему если есть thread_id
        await event.bot.send_message(
            chat_id=event.chat.id,
            text=welcome_text,
            message_thread_id=event.message_thread_id if event.message_thread_id else None,
            parse_mode="HTML"
        )
        logger.info(f"✅ Приветствие отправлено пользователю {user_id} ({full_name})")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки приветствия пользователю {user_id}: {e}")

@router.message(
    F.chat.type.in_(['group', 'supergroup']),
    F.text,
    # Только первое сообщение пользователя в чате
    lambda msg: msg.from_user.id not in welcomed_users and _is_in_correct_topic(msg)
)
async def group_first_message_handler(message: Message):
    """Обработчик первого текстового сообщения пользователя в группе"""
    
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
        logger.info(f"✅ Приветствие отправлено пользователю {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки приветствия пользователю {user_id}: {e}")
