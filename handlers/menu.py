import logging
from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from validators import generate_profile_text, check_flight_ban
from db_manager import db  # <-- Импортируем db из db_manager

logger = logging.getLogger(__name__)
router = Router()

def get_main_keyboard(is_admin=False):
    keyboard = [
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="📚 Полезная информация")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="🛡 Административные функции")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(F.text == "👤 Мой профиль")
async def show_profile(message: types.Message):  # <-- БЕЗ db параметра!
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала пройдите регистрацию (/start)")
        return
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])
    await message.answer(profile_text, reply_markup=keyboard)

@router.message(F.text == "📚 Полезная информация")
async def show_info(message: types.Message):
    await message.answer("📚 Полезная информация\n\nВведите название аэродрома или города для поиска контактной информации.")

@router.message(F.text == "🛡 Административные функции")
async def admin_functions(message: types.Message):  # <-- БЕЗ db параметра!
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS and not db.check_admin_status(user_id):
        await message.answer("❌ У вас нет доступа")
        return
    await message.answer("🛡 Административные функции")
