import logging
from aiogram import Router, F, types
from aiogram.types import Message
from config import GROUP_ID
from utils.admin_check import is_admin

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# ОБРАБОТКА СООБЩЕНИЙ В ГРУППЕ
# ============================================================

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def group_message_handler(message: types.Message):
    """Обработка сообщений в группе"""
    
    # Игнорируем сообщения от ботов
    if message.from_user.is_bot:
        return
    
    # Проверяем что это наша группа
    if message.chat.id != GROUP_ID:
        return
    
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text
    
    logger.info(f"💬 Сообщение в группе от {username} ({user_id}): {text[:50]}")
    
    # Пример: команда /профиль в группе
    if text and text.startswith('/профиль'):
        await handle_group_profile(message, user_id)
        return
    
    # Пример: команда /помощь в группе
    if text and text.startswith('/помощь'):
        await handle_group_help(message)
        return
    
    # Можно добавить другие команды для группы

async def handle_group_profile(message: types.Message, user_id: int):
    """Показать профиль пользователя в группе"""
    from db_manager import db
    
    user = db.get_user(user_id)
    
    if not user:
        await message.answer(
            "❌ Вы ещё не зарегистрированы в боте.\n"
            "Напишите боту в личные сообщения: /start"
        )
        return
    
    fio = user[3] or "Не указано"
    rank = user[4] or "Не указано"
    
    await message.answer(
        f"👤 <b>{fio}</b>\n"
        f"🎖 Звание: {rank}\n\n"
        f"Полный профиль доступен в ЛС бота.",
        parse_mode="HTML"
    )

async def handle_group_help(message: types.Message):
    """Справка по командам в группе"""
    help_text = (
        "🤖 <b>Команды для группы:</b>\n\n"
        "/профиль - Показать ваш профиль\n"
        "/помощь - Эта справка\n\n"
        "📩 <b>Личные команды</b> (в ЛС бота):\n"
        "/start - Главное меню\n"
        "Мой профиль - Анкета\n"
        "Полезная информация - База знаний"
    )
    
    await message.answer(help_text, parse_mode="HTML")

# ============================================================
# ОТВЕТЫ НА УПОМИНАНИЯ БОТА
# ============================================================

@router.message(F.mention)
async def bot_mention_handler(message: types.Message):
    """Ответ на упоминание бота"""
    
    if message.chat.id != GROUP_ID:
        return
    
    await message.answer(
        "👋 Я здесь! Напишите /помощь для списка команд.\n"
        "Или обратитесь ко мне в личные сообщения."
    )

# ============================================================
# ПРИВЕТСТВИЕ НОВЫХ УЧАСТНИКОВ
# ============================================================

@router.my_chat_member()
async def bot_chat_member_handler(message: types.ChatMemberUpdated):
    """Обработка изменения статуса бота в чате"""
    
    old_status = message.old_chat_member.status
    new_status = message.new_chat_member.status
    
    if new_status == 'member':
        logger.info(f"➕ Бот добавлен в чат {message.chat.title}")
    elif new_status == 'administrator':
        logger.info(f"⭐ Бот стал администратором в {message.chat.title}")
    elif new_status == 'left':
        logger.info(f"➖ Бот покинул чат {message.chat.title}")

# ============================================================
# ПРОВЕРКА ПРАВ АДМИНИСТРАТОРА
# ============================================================

async def is_bot_admin(chat_id: int) -> bool:
    """Проверить является ли бот администратором в чате"""
    from main import bot
    
    try:
        member = await bot.get_chat_member(chat_id, bot.id)
        return member.is_chat_admin()
    except:
        return False
