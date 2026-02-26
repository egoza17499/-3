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
# ОБРАБОТЧИК ПОИСКА
# ============================================================

@router.message(F.text)
async def search_handler(message: types.Message):
    """Обработчик поиска — с исключением для блоков безопасности"""
    
    search_text = message.text.strip()
    
    # ❌ ИГНОРИРУЕМ команды для блоков безопасности
    # Чтобы они обрабатывались в group.py
    if re.match(r'^(блок\s*№?\s*\d+)$', search_text, re.IGNORECASE):
        logger.info(f"⏭️ Пропускаем команду блока в search: '{search_text}'")
        return
    
    # Проверяем, админ ли это
    user_id = message.from_user.id
    username = message.from_user.username
    
    if not await is_admin(user_id, username):
        # Если не админ — игнорируем поиск по пользователям
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
    
    for user in users[:10]:  # Показываем первые 10 результатов
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
