import logging
import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db_manager import db
from utils.admin_check import admin_required_message, is_admin

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# ОБРАБОТЧИК ПОИСКА ПОЛЬЗОВАТЕЛЕЙ (ТОЛЬКО ДЛЯ АДМИНОВ)
# ============================================================

@router.message(
    F.text.regexp(re.compile(r'^(блок\s*№?\s*\d+)$', re.IGNORECASE))
)
async def group_safety_block_from_disk(message: types.Message):
    """Показать блок безопасности из Yandex Disk — работает и в ЛС, и в группе!"""
    
    # Проверяем что это наша группа ИЛИ личное сообщение
    if message.chat.id != GROUP_ID and message.chat.type != "private":
        return
    
    try:
        from utils.yandex_disk_client import disk_client
    except ImportError:
        logger.error("❌ Модуль Yandex Disk не подключен!")
        return
    
    # 🔥 САМАЯ ПЕРВАЯ ПРОВЕРКА — игнорируем ВСЕ группы!
    if message.chat.type != "private":
        logger.debug(f"⏭️ Игнорируем сообщение из {message.chat.type}: '{message.text[:30]}'")
        return
    
    # 🔥 ОТЛАДКА — смотрим что приходит
    logger.debug(f"📩 Получено сообщение из чата типа: '{message.chat.type}' (ID: {message.chat.id})")
    logger.debug(f"💬 Текст: '{message.text[:50]}'")
    
    # 🔥 САМАЯ ПЕРВАЯ ПРОВЕРКА — игнорируем ВСЕ группы!
    if message.chat.type != "private":
        logger.info(f"⏭️ Игнорируем сообщение из {message.chat.type} (не private)!")
        return  # ← ВАЖНО! Возвращаем СРАЗУ
    
    # Дальше обрабатываем только личные сообщения
    search_text = message.text.strip()
    
    # ❌ Игнорируем команды для блоков безопасности
    if re.match(r'^(блок\s*№?\s*\d+)$', search_text, re.IGNORECASE):
        logger.info(f"⏭️ Пропускаем команду блока: '{search_text}'")
        return
    
    # Проверяем, админ ли это
    user_id = message.from_user.id
    username = message.from_user.username
    
    if not await is_admin(user_id, username):
        logger.info(f"⏭️ Пропускаем (не админ): '{search_text}'")
        return
    
    # Поиск пользователей (только для админов)
    logger.info(f"🔍 Поиск пользователя: '{search_text}'")
    users = db.search_users(search_text)
    
    if not users:
        await message.answer(f"❌ Пользователи по запросу \"{search_text}\" не найдены")
        return
    
    text = f"🔍 Найдено пользователей: {len(users)}\n\n"
    
    keyboard = []
    
    for user in users[:10]:
        user_id_db = user[0]
        username_db = user[1] or "N/A"
        fio = user[3] or "Не указано"
        rank = user[4] or "Не указано"
        
        text += f"👤 {fio}\n"
        text += f"   @{username_db}\n"
        text += f"   {rank}\n\n"
        
        keyboard.append([InlineKeyboardButton(
            text=f"👤 {fio}",
            callback_data=f"admin_user_profile_{user_id_db}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="admin_functions_back"
    )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(text, reply_markup=reply_markup)
