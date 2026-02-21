import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from validators import check_flight_ban
from db_manager import db

logger = logging.getLogger(__name__)
router = Router()

class AddAdminState(StatesGroup):
    username = State()

class RemoveAdminState(StatesGroup):
    user_id = State()

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
    is_admin = callback.from_user.id in ADMIN_IDS or db.check_admin_status(callback.from_user.id, callback.from_user.username)
    from handlers.menu import get_main_keyboard
    await callback.message.edit_text("Главное меню", reply_markup=get_main_keyboard(is_admin))
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_list")
async def admin_list(callback: types.CallbackQuery):
    # Проверяем права админа
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
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
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
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
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
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
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    text = "👥 Управление администраторами\n\n"
    text += "Выберите действие:\n\n"
    text += "➕ Добавить админа по username\n"
    text += "➖ Удалить админа"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить админа", callback_data="admin_add_admin")],
        [InlineKeyboardButton(text="➖ Удалить админа", callback_data="admin_remove_admin")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_add_admin")
async def admin_add_admin_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может добавлять админов", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ Добавление админа\n\n"
        "Введите username пользователя (без @ или с @):\n\n"
        "Пример: @username или username"
    )
    await state.set_state(AddAdminState.username)
    await callback.answer()

@router.message(AddAdminState.username)
async def admin_add_admin_by_username(message: types.Message, state: FSMContext):
    username = message.text.strip().lstrip('@')
    
    # Ищем пользователя в базе
    user = db.find_user_by_username(username)
    if not user:
        await message.answer(
            f"❌ Пользователь @{username} не найден в базе данных!\n\n"
            "Пользователь должен сначала зарегистрироваться в боте."
        )
        await state.clear()
        return
    
    # Добавляем как админа
    db.add_admin(user['user_id'], username, message.from_user.id)
    
    await message.answer(f"✅ Пользователь @{username} (ID: {user['user_id']}) добавлен в админы!")
    await state.clear()

@router.callback_query(lambda c: c.data == "admin_remove_admin")
async def admin_remove_admin_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может удалять админов", show_alert=True)
        return
    
    # Получаем всех админов из БД
    admins = db.get_all_admins()
    
    if not admins:
        await callback.message.edit_text("📋 В базе нет дополнительных админов (кроме тех что в config)")
        await callback.answer()
        return
    
    text = "➖ Удаление админа\n\n"
    text += "Текущие админы из базы данных:\n\n"
    
    for admin in admins:
        username = admin['username'] or "не указан"
        text += f"• ID: {admin['user_id']} (@{username})\n"
    
    text += "\nВведите ID админа которого хотите удалить:"
    
    await callback.message.edit_text(text)
    await state.set_state(RemoveAdminState.user_id)
    await callback.answer()

@router.message(RemoveAdminState.user_id)
async def admin_remove_admin_by_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите корректный ID (число)")
        return
    
    # Проверяем что это не главный админ
    if user_id in ADMIN_IDS:
        await message.answer("❌ Нельзя удалить главного админа из config!")
        await state.clear()
        return
    
    # Удаляем админа
    db.remove_admin(user_id)
    
    await message.answer(f"✅ Админ с ID {user_id} удалён!")
    await state.clear()

@router.callback_query(lambda c: c.data == "admin_functions_back")
async def admin_functions_back(callback: types.CallbackQuery):
    # Проверяем права админа
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    text = "🛡 Административные функции\n\nВыберите действие:"
    
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()
