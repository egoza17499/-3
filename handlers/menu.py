import logging
from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from validators import generate_profile_text, check_flight_ban
from db_manager import db

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
async def show_profile(message: types.Message):
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
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛡 Блоки по безопасности полетов", callback_data="info_safety")],
        [InlineKeyboardButton(text="✈️ Поиск информации об аэродроме", callback_data="info_aerodrome")],
        [InlineKeyboardButton(text="📖 Полезные знания по самолету", callback_data="info_aircraft")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="info_back")]
    ])
    
    await message.answer(
        "📚 Полезная информация\n\n"
        "Выберите раздел:",
        reply_markup=keyboard
    )

@router.message(F.text == "🛡 Административные функции")
async def admin_functions(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS and not db.check_admin_status(user_id, message.from_user.username):
        await message.answer("❌ У вас нет доступа")
        return
    # Показываем админское меню с inline клавиатурой
    from handlers.admin import get_admin_keyboard
    await message.answer("🛡 Административные функции\n\nВыберите действие:", reply_markup=get_admin_keyboard())
