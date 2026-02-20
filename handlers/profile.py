import logging
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)
router = Router()

def get_profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])

def get_edit_profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ФИО", callback_data="edit_fio")],
        [InlineKeyboardButton(text="Звание", callback_data="edit_rank")],
        [InlineKeyboardButton(text="Квалификация", callback_data="edit_qualification")],
        [InlineKeyboardButton(text="Даты отпуска", callback_data="edit_leave")],
        [InlineKeyboardButton(text="ВЛК", callback_data="edit_vlk")],
        [InlineKeyboardButton(text="УМО", callback_data="edit_umo")],
        [InlineKeyboardButton(text="КБП-4 МД-М", callback_data="edit_ex4_md_m")],
        [InlineKeyboardButton(text="КБП-7 МД-М", callback_data="edit_ex7_md_m")],
        [InlineKeyboardButton(text="КБП-4 МД-90А", callback_data="edit_ex4_md_90a")],
        [InlineKeyboardButton(text="КБП-7 МД-90А", callback_data="edit_ex7_md_90a")],
        [InlineKeyboardButton(text="Прыжки", callback_data="edit_parachute")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
    ])

@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    from main import db
    from handlers.menu import get_main_keyboard
    is_admin = callback.from_user.id in ADMIN_IDS or db.check_admin_status(callback.from_user.id)
    await callback.message.edit_text("Главное меню", reply_markup=get_main_keyboard(is_admin))
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_to_profile")
async def back_to_profile(callback: types.CallbackQuery):
    from main import db
    from validators import generate_profile_text, check_flight_ban
    user = db.get_user(callback.from_user.id)
    if not user:
        await callback.message.edit_text("❌ Сначала пройдите регистрацию (/start)")
        await callback.answer()
        return
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await callback.message.edit_text(profile_text, reply_markup=get_profile_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "edit_profile")
async def edit_profile(callback: types.CallbackQuery):
    await callback.message.edit_text("✏️ Редактирование профиля\n\nВыберите поле:", reply_markup=get_edit_profile_keyboard())
    await callback.answer()
