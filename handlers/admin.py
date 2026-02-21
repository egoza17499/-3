import logging
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from validators import check_flight_ban
from db_manager import db

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
    is_admin = callback.from_user.id in ADMIN_IDS or db.check_admin_status(callback.from_user.id)
    from handlers.menu import get_main_keyboard
    await callback.message.edit_text("Главное меню", reply_markup=get_main_keyboard(is_admin))
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_list")
async def admin_list(callback: types.CallbackQuery):
    # Проверяем права админа
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    users = db.get_all_users()
    if not users:
        await callback.message.edit_text("📋 Список пользователей:\n\nПользователей пока нет")
        await callback.answer()
        return
    
    text = "📋 Список пользователей:\n\n"
    for user in users:
        fio = user[3] or "Не указано"
        rank = user[4] or "Не указано"
        username = user[1] or "Не указан"
        text += f"👤 {fio}\n"
        text += f"   Звание: {rank}\n"
        text += f"   Username: @{username}\n\n"
    
    # Добавляем кнопку назад
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    # Проверяем права админа
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    users = db.get_all_users()
    total = len(users) if users else 0
    can_fly = sum(1 for user in users if not check_flight_ban(user)) if users else 0
    
    text = "📊 Статистика:\n\n"
    text += f"👥 Всего пользователей: {total}\n"
    text += f"✅ Готовы к полётам: {can_fly}\n"
    text += f"🚫 Не могут летать: {total - can_fly}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_fill_airports")
async def admin_fill_airports(callback: types.CallbackQuery):
    # Проверяем права админа
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text("⏳ Заполняю базу аэродромов...")
    await callback.answer()
    
    # Здесь будет логика заполнения базы аэродромов
    # Пока просто заглушка
    await callback.message.edit_text("✅ База аэродромов заполнена!\n\n(Функция в разработке)")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "admin_manage")
async def admin_manage(callback: types.CallbackQuery):
    # Проверяем права админа
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    text = "👥 Управление администраторами\n\n"
    text += "Выберите действие:\n\n"
    text += "➕ Добавить админа\n"
    text += "➖ Удалить админа"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить админа", callback_data="admin_add_admin")],
        [InlineKeyboardButton(text="➖ Удалить админа", callback_data="admin_remove_admin")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_add_admin")
async def admin_add_admin_start(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может добавлять админов", show_alert=True)
        return
    
    await callback.message.edit_text("➕ Добавление админа\n\nВведите ID пользователя которого хотите сделать админом:")
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_remove_admin")
async def admin_remove_admin_start(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может удалять админов", show_alert=True)
        return
    
    # Показываем список текущих админов
    from config import ADMIN_IDS as all_admins
    text = "➖ Удаление админа\n\n"
    text += "Текущие админы (кроме главного):\n\n"
    
    for admin_id in all_admins:
        if admin_id != ADMIN_IDS[0]:  # Не показываем главного админа
            text += f"• ID: {admin_id}\n"
    
    text += "\nВведите ID админа которого хотите удалить:"
    
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_functions_back")
async def admin_functions_back(callback: types.CallbackQuery):
    # Проверяем права админа
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    text = "🛡 Административные функции\n\nВыберите действие:"
    
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()
