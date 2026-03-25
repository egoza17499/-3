import logging
from aiogram import Router, F, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from config import TOPIC_ID, GROUP_ID
from db_manager import get_user, add_user
from handlers.menu import show_main_menu

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# ОБРАБОТЧИК /start ДЛЯ ЛИЧНЫХ СООБЩЕНИЙ
# ============================================================

@router.message(F.text == "/start")
async def cmd_start_personal(message: Message, state: FSMContext):
    """Обработчик /start в личных сообщениях"""
    
    # Если это группа — пропускаем
    if message.chat.type in ['group', 'supergroup']:
        return
    
    user_id = message.from_user.id
    username = message.from_user.username or ""
    
    # Проверяем — не зарегистрирован ли уже
    user = get_user(user_id)
    
    if user and user.get('is_registered'):
        from handlers.menu import show_main_menu
        await show_main_menu(message)
        return
    
    add_user(user_id, username)
    
    keyboard = ReplyKeyboardMarkup(
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
    
    await message.answer(
        "👋 <b>Привет! Я бот 81-го полка</b> ✈️\n\n"
        "Помогаю лётчикам с:\n"
        "• 🗺 Информацией об аэродромах и телефонах\n"
        "• 🏠 Данные о жилье по линии МО РФ\n"
        "• 📋 Блоками безопасности и документами\n"
        "• 📊 Отслеживанием сроков ВЛК, УМО, КБП\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    logger.info(f"✅ /start обработан для пользователя {user_id}")

# ============================================================
# ПРИВЕТСТВИЕ В ГРУППЕ (в нужной теме)
# ============================================================

welcomed_users: set[int] = set()

def _is_in_correct_topic(message: Message) -> bool:
    if message.chat.id != GROUP_ID:
        return False
    if TOPIC_ID and message.message_thread_id != TOPIC_ID:
        return False
    return True

@router.message(
    F.chat.type.in_(['group', 'supergroup']),
    F.text,
    lambda msg: msg.from_user.id not in welcomed_users and _is_in_correct_topic(msg)
)
async def group_first_message_handler(message: Message):
    user_id = message.from_user.id
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
        logger.error(f"❌ Ошибка отправки приветствия: {e}")
