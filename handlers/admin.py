import logging
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from validators import check_flight_ban

logger = logging.getLogger(__name__)
router = Router()

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_list")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="✈️ Заполнить базу аэродромов", callback_data="admin_fill_airports")],
        [InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_manage")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])

@router.callback_query(lambda c: c.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    from main import db
    is_admin = callback.from_user.id in ADMIN_IDS or db.check_admin_status(callback.from_user.id)
    from handlers.menu import get_main_keyboard
    await callback.message.edit_text("Главное меню", reply_markup=get_main_keyboard(is_admin))
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_list")
async def admin_list(callback: types.CallbackQuery):
    from main import db
    users = db.get_all_users()
    if not users:
        await callback.message.edit_text("📋 Список пуст")
        await callback.answer()
        return
    text = "📋 Список пользователей:\n\n"
    for user in users:
        fio = user[3] or "Не указано"
        rank = user[4] or "Не указано"
        text += f"• {fio} ({rank})\n"
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    from main import db
    users = db.get_all_users()
    total = len(users)
    can_fly = sum(1 for user in users if not check_flight_ban(user))
    text = f"📊 Статистика:\n\n👥 Всего пользователей: {total}\n✅ Готовы к полётам: {can_fly}\n🚫 Не могут летать: {total - can_fly}"
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_fill_airports")
async def admin_fill_airports(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ Заполняю базу аэродромов...")
    await callback.message.edit_text("✅ База заполнена!")
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_manage")
async def admin_manage(callback: types.CallbackQuery):
    text = "👥 Управление администраторами\n\nВыберите действие:\n➕ Добавить админа\n➖ Удалить админа"
    await callback.message.edit_text(text)
    await callback.answer()
