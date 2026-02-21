import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from validators import check_flight_ban, check_date_warnings, generate_profile_text
from db_manager import db

logger = logging.getLogger(__name__)
router = Router()

class AddAdminState(StatesGroup):
    username = State()

class RemoveAdminState(StatesGroup):
    user_id = State()

class UserSearchState(StatesGroup):
    search = State()

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
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    text = "📋 Список пользователей:\n\n"
    text += "Введите фамилию или имя для поиска:\n\n"
    text += "Или выберите действие:"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Поиск пользователя", callback_data="admin_search_user")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_search_user")
async def admin_search_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 Поиск пользователя\n\n"
        "Введите фамилию или имя (минимум 2 символа):\n\n"
        "Пример: Иванов или Петр"
    )
    await state.set_state(UserSearchState.search)
    await callback.answer()

@router.message(UserSearchState.search)
async def admin_search_user(message: types.Message, state: FSMContext):
    search_text = message.text.strip()
    
    if len(search_text) < 2:
        await message.answer("❌ Введите минимум 2 символа для поиска")
        return
    
    users = db.search_users(search_text)
    
    if not users:
        await message.answer(f"❌ Пользователи по запросу \"{search_text}\" не найдены")
        await state.clear()
        return
    
    if len(users) == 1:
        # Показываем полную информацию
        user = users[0]
        profile_text = generate_profile_text(user)
        warnings, bans = check_date_warnings(user)
        
        if warnings:
            profile_text += "\n⚠️ СКОРО ИСТЕКАЕТ:\n" + "\n".join([f"• {w}" for w in warnings])
        
        if bans:
            profile_text += "\n\n⛔ ЗАПРЕЩЕНО:\n" + "\n".join([f"• {b}" for b in bans])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к поиску", callback_data="admin_search_user_btn")]
        ])
        
        await message.answer(profile_text, reply_markup=keyboard)
    else:
        # Показываем список
        text = f"🔍 Найдено пользователей: {len(users)}\n\n"
        for i, user in enumerate(users, 1):
            fio = user[3] or "Не указано"
            rank = user[4] or "Не указано"
            username = user[1] or "Не указан"
            
            warnings, bans = check_date_warnings(user)
            
            if bans:
                indicator = "⛔"
            elif warnings:
                indicator = "⚠️"
            else:
                indicator = "✅"
            
            text += f"{i}. {indicator} {fio}\n"
            text += f"   Звание: {rank}\n"
            text += f"   Username: @{username}\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к поиску", callback_data="admin_search_user_btn")]
        ])
        
        await message.answer(text, reply_markup=keyboard)
    
    await state.clear()

@router.callback_query(lambda c: c.data == "admin_search_user_btn")
async def admin_search_back(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 Поиск пользователя\n\n"
        "Введите фамилию или имя (минимум 2 символа):\n\n"
        "Пример: Иванов или Петр"
    )
    await state.set_state(UserSearchState.search)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    users = db.get_all_users()
    total = len(users) if users else 0
    
    ready_users = db.get_users_ready_to_fly()
    cannot_fly_users = db.get_users_cannot_fly()
    
    can_fly = len(ready_users)
    cannot_fly = len(cannot_fly_users)
    
    text = "📊 Статистика:\n\n"
    text += f"👥 Всего пользователей: {total}\n"
    text += f"✅ Готовы к полётам: {can_fly}\n"
    text += f"🚫 Не могут летать: {cannot_fly}\n\n"
    text += "Нажмите на кнопку чтобы увидеть список:"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ Готовы к полётам ({can_fly})", callback_data="admin_stats_ready")],
        [InlineKeyboardButton(text=f"🚫 Не могут летать ({cannot_fly})", callback_data="admin_stats_cannot")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_stats_ready")
async def admin_stats_show_ready(callback: types.CallbackQuery):
    users = db.get_users_ready_to_fly()
    
    if not users:
        await callback.answer("Нет пользователей готовых к полётам", show_alert=True)
        return
    
    text = "✅ Готовы к полётам:\n\n"
    for i, user in enumerate(users, 1):
        fio = user[3] or "Не указано"
        rank = user[4] or "Не указано"
        username = user[1] or "Не указан"
        
        text += f"{i}. {fio}\n"
        text += f"   Звание: {rank}\n"
        text += f"   Username: @{username}\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к статистике", callback_data="admin_stats")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_stats_cannot")
async def admin_stats_show_cannot(callback: types.CallbackQuery):
    users = db.get_users_cannot_fly()
    
    if not users:
        await callback.answer("Нет пользователей кто не может летать", show_alert=True)
        return
    
    text = "🚫 Не могут летать:\n\n"
    for i, user in enumerate(users, 1):
        fio = user[3] or "Не указано"
        rank = user[4] or "Не указано"
        username = user[1] or "Не указан"
        
        bans = check_flight_ban(user)
        
        text += f"{i}. {fio}\n"
        text += f"   Звание: {rank}\n"
        text += f"   Username: @{username}\n"
        text += f"   Причины:\n"
        for ban in bans:
            text += f"   • {ban}\n"
        text += "\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к статистике", callback_data="admin_stats")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_fill_airports")
async def admin_fill_airports(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text("⏳ Заполняю базу аэродромов...")
    await callback.answer()
    
    await callback.message.edit_text("✅ База аэродромов заполнена!\n\n(Функция в разработке)")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "admin_manage")
async def admin_manage(callback: types.CallbackQuery):
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
    
    user = db.find_user_by_username(username)
    if not user:
        await message.answer(
            f"❌ Пользователь @{username} не найден в базе данных!\n\n"
            "Пользователь должен сначала зарегистрироваться в боте."
        )
        await state.clear()
        return
    
    db.add_admin(user['user_id'], username, message.from_user.id)
    
    await message.answer(f"✅ Пользователь @{username} (ID: {user['user_id']}) добавлен в админы!")
    await state.clear()

@router.callback_query(lambda c: c.data == "admin_remove_admin")
async def admin_remove_admin_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может удалять админов", show_alert=True)
        return
    
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
    
    if user_id in ADMIN_IDS:
        await message.answer("❌ Нельзя удалить главного админа из config!")
        await state.clear()
        return
    
    db.remove_admin(user_id)
    
    await message.answer(f"✅ Админ с ID {user_id} удалён!")
    await state.clear()

@router.callback_query(lambda c: c.data == "admin_functions_back")
async def admin_functions_back(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    text = "🛡 Административные функции\n\nВыберите действие:"
    
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()
