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
# ⚠️ ИСКЛЮЧАЕМ команды "блок N" через фильтр в декораторе!
# ============================================================

@router.message(
    F.text, 
    ~F.text.regexp(re.compile(r'^(блок\s*№?\s*\d+)$', re.IGNORECASE))  # ✅ re.compile!
)
async def search_handler(message: types.Message):
    """Обработчик поиска пользователей — только в ЛС и только для админов"""
    
    # 🔥 ПЕРВАЯ ПРОВЕРКА — игнорируем группы!
    if message.chat.type != "private":
        logger.debug(f"⏭️ Игнорируем сообщение из {message.chat.type}")
        return
    
    search_text = message.text.strip()
    
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
