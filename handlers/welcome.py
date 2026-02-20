import logging
from aiogram import Router, F, types
from config import TOPIC_ID
from database import Database

logger = logging.getLogger(__name__)
router = Router()
db = Database('bot_database.db')
welcomed_users = set()

@router.message(lambda msg: msg.chat.type in ['group', 'supergroup'])
async def group_welcome_handler(message: types.Message):
    if message.message_thread_id != TOPIC_ID:
        return
    if message.from_user.is_bot:
        return
    if message.new_chat_members or message.left_chat_member:
        return
    
    user_id = message.from_user.id
    if user_id in welcomed_users:
        return
    
    welcomed_users.add(user_id)
    bot_link = "https://t.me/help_81polk_bot"
    welcome_text = f"Здравствуйте, {message.from_user.full_name}! 👋\n\nБот доступен по ссылке: {bot_link}\n\nДля начала пользования перейдите по ссылке и нажмите /start"
    
    try:
        await message.answer(welcome_text, reply_to_message_id=message.message_id)
    except Exception as e:
        logger.error(f"Ошибка отправки приветствия: {e}")
