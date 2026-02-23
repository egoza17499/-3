import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from utils.admin_check import admin_required, admin_required_message, is_admin
from validators import check_flight_ban, check_date_warnings, generate_profile_text
from db_manager import db

logger = logging.getLogger(__name__)
router = Router()  # ✅ Создаём router!

# ============================================================
# СОСТОЯНИЯ
# ============================================================

class AddAdminState(StatesGroup):
    username = State()

class RemoveAdminState(StatesGroup):
    user_id = State()

class AdminListState(StatesGroup):
    waiting_for_search = State()

class AdminKnowledgeState(StatesGroup):
    aero_add_name = State()
    aero_add_city = State()
    aero_add_airport = State()
    aero_add_housing = State()
    aero_add_phone_name = State()
    aero_add_phone_number = State()
    aero_add_doc_name = State()
    aero_add_doc_file = State()
    safety_add_number = State()
    safety_add_text = State()
    aircraft_add_type = State()
    aircraft_add_name = State()
    aircraft_add_text = State()
    aircraft_add_file = State()

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def get_user_status_details(user):
    """
    Возвращает детальную информацию о статусе пользователя
    Returns: (indicator, status_text, details_list)
    """
    try:
        warnings, bans = check_date_warnings(user)
        
        if bans:
            return "🛑", "Запрещено", bans
        elif warnings:
            return "⚠️", "Внимание", warnings
        else:
            return "🟢", "OK", []
    except Exception as e:
        logger.error(f"Ошибка проверки статуса: {e}")
        return "⚪", "Ошибка", []

def create_user_list_keyboard(user_id, fio):
    """Создаёт клавиатуру с кнопкой для перехода к профилю"""
    fio_short = fio[:40] + "..." if len(fio) > 40 else fio
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"👤 {fio_short}", callback_data=f"admin_user_profile_{user_id}")],
        [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")]
    ])

# ============================================================
# КЛАВИАТУРЫ
# ============================================================

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_list")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📚 Управление базой знаний", callback_data="admin_knowledge")],
        [InlineKeyboardButton(text="✈️ Заполнить базу аэродромов", callback_data="admin_fill_airports")],
        [InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_manage")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])

# ============================================================
# АДМИН МЕНЮ
# ============================================================

@router.callback_query(F.data == "admin_back")
@admin_required
async def admin_back(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    from handlers.menu import get_main_keyboard
    await callback.message.edit_text("Главное меню", reply_markup=get_main_keyboard(True))
    await callback.answer()

@router.callback_query(F.data == "admin_functions_back")
@admin_required
async def admin_functions_back(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = "🛡 Административные функции\n\nВыберите действие:"
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()

# ============================================================
# СПИСОК ПОЛЬЗОВАТЕЛЕЙ
# ============================================================

@router.callback_query(F.data == "admin_list")
@admin_required
async def admin_list(callback: types.CallbackQuery, state: FSMContext):
    try:
        users = db.get_all_users()
        
        if not users:
            text = "📋 Список пользователей:\n\nПользователей пока нет"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
            ])
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            await callback.answer()
            return
        
        text = "📋 <b>Список пользователей</b>\n\n"
        text += "💡 <i>Введите фамилию для поиска или нажмите на имя</i>\n\n"
        
        green_count = 0
        yellow_count = 0
        red_count = 0
        
        for i, user in enumerate(users, 1):
            user_id = user[0] if len(user) > 0 else 0
            username = user[1] if len(user) > 1 else "Не указан"
            fio = user[3] if len(user) > 3 else "Не указано"
            rank = user[4] if len(user) > 4 else "Не указано"
            
            fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            username_safe = str(username).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
            
            indicator, status_label, details = get_user_status_details(user)
            
            if indicator == "🟢":
                green_count += 1
            elif indicator == "⚠️":
                yellow_count += 1
            elif indicator == "🛑":
                red_count += 1
            
            text += f"{i}. {indicator} <b>{fio_safe}</b>\n"
            text += f"   👤 @{username_safe} | 🎖 {rank_safe}\n"
            
            if details:
                for detail in details:
                    detail_safe = str(detail).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                    text += f"   <i>{detail_safe}</i>\n"
            
            text += "\n"
            
            if len(text) > 3500:
                text += f"... и ещё {len(users) - i} пользователей\n"
                break
        
        text += f"\n<b>Статус:</b> 🟢 {green_count} | ⚠️ {yellow_count} | 🛑 {red_count}\n"
        text += "\n<i>Введите текст для поиска или нажмите Назад</i>"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(AdminListState.waiting_for_search)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_list: {e}", exc_info=True)
        await callback.message.answer("❌ Ошибка при получении списка", parse_mode="HTML")
        await callback.answer()

@router.message(AdminListState.waiting_for_search, F.text)
@admin_required_message
async def admin_list_search_handler(message: types.Message):
    try:
        search_text = message.text.strip()
        if len(search_text) < 2:
            await message.answer("⚠️ Введите минимум 2 символа", parse_mode="HTML")
            return
        
        users = db.search_users(search_text)
        if not users:
            await message.answer(f"❌ Пользователи по запросу \"{search_text}\" не найдены", parse_mode="HTML")
            return
        
        if len(users) == 1:
            # Показываем профиль с кнопками
            user = users[0]
            user_id = user[0]
            fio = user[3] if len(user) > 3 else "Не указано"
            
            profile_text = generate_profile_text(user)
            indicator, status_label, details = get_user_status_details(user)
            
            profile_text = f"{indicator} <b>Статус: {status_label}</b>\n\n" + profile_text
            
            if details:
                profile_text += f"\n<b>Детали:</b>\n"
                for detail in details:
                    detail_safe = str(detail).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                    profile_text += f"• {detail_safe}\n"
            
            keyboard = create_user_list_keyboard(user_id, fio)
            await message.answer(profile_text, reply_markup=keyboard, parse_mode="HTML")
        else:
            # Показываем список с КНОПКАМИ-ФИО
            text = f"🔍 Найдено: {len(users)}\n\n"
            keyboard_buttons = []
            
            for i, user in enumerate(users, 1):
                user_id = user[0]
                fio = user[3] if len(user) > 3 else "Не указано"
                rank = user[4] if len(user) > 4 else "Не указано"
                username = user[1] if len(user) > 1 else "Не указан"
                
                fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                username_safe = str(username).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
                
                indicator, status_label, details = get_user_status_details(user)
                
                # ФИО как АКТИВНАЯ КНОПКА
                fio_short = fio[:40] + "..." if len(fio) > 40 else fio
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"{i}. {indicator} {fio_short}",
                        callback_data=f"admin_user_profile_{user_id}"
                    )
                ])
                
                # Дополнительная информация под кнопкой (не кликабельна)
                text += f"   👤 @{username_safe} | 🎖 {rank_safe}\n"
                
                if details:
                    for detail in details:
                        detail_safe = str(detail).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                        text += f"   <i>{detail_safe}</i>\n"
                
                text += "\n"
            
            # Кнопка "Назад"
            keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")])
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"Ошибка поиска: {e}", exc_info=True)
        await message.answer("❌ Ошибка при поиске", parse_mode="HTML")

@router.callback_query(F.data.startswith("admin_user_profile_"))
@admin_required
async def admin_user_profile(callback: types.CallbackQuery):
    try:
        user_id = int(callback.data.split("_")[-1])
        
        query = """
            SELECT user_id, username, registered_at, fio, rank, qualification,
                   leave_start_date, leave_end_date, vlk_date, umo_date,
                   exercise_4_md_m_date, exercise_7_md_m_date,
                   exercise_4_md_90a_date, exercise_7_md_90a_date,
                   parachute_jump_date, is_registered
            FROM users WHERE user_id = %s
        """
        user = db.execute_query(query, (user_id,), fetch=True)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        user = user[0]
        fio = user[3] if len(user) > 3 else "Не указано"
        
        profile_text = generate_profile_text(user)
        indicator, status_label, details = get_user_status_details(user)
        
        profile_text = f"{indicator} <b>Статус: {status_label}</b>\n\n" + profile_text
        
        if details:
            profile_text += f"\n<b>⚠️ Детали статуса:</b>\n"
            for detail in details:
                detail_safe = str(detail).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                profile_text += f"• {detail_safe}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")],
            [InlineKeyboardButton(text="🔙 Админ функции", callback_data="admin_functions_back")]
        ])
        
        await callback.message.answer(profile_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка просмотра профиля: {e}", exc_info=True)
        await callback.answer("❌ Ошибка", show_alert=True)

# ============================================================
# СТАТИСТИКА
# ============================================================

@router.callback_query(F.data == "admin_stats")
@admin_required
async def admin_stats(callback: types.CallbackQuery):
    try:
        users = db.get_all_users()
        total = len(users) if users else 0
        
        green_count = 0
        yellow_count = 0
        red_count = 0
        
        for user in users:
            indicator, _, _ = get_user_status_details(user)
            if indicator == "🟢":
                green_count += 1
            elif indicator == "⚠️":
                yellow_count += 1
            elif indicator == "🛑":
                red_count += 1
        
        text = f"📊 <b>Статистика:</b>\n\n"
        text += f"👥 Всего: {total}\n"
        text += f"🟢 Всё OK: {green_count}\n"
        text += f"⚠️ Внимание: {yellow_count}\n"
        text += f"🛑 Запрещено: {red_count}\n\n"
        text += "Нажмите чтобы увидеть список:"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🟢 Всё OK ({green_count})", callback_data="admin_stats_green")],
            [InlineKeyboardButton(text=f"⚠️ Внимание ({yellow_count})", callback_data="admin_stats_yellow")],
            [InlineKeyboardButton(text=f"🛑 Запрещено ({red_count})", callback_data="admin_stats_red")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_stats: {e}", exc_info=True)
        await callback.answer("❌ Ошибка", show_alert=True)

@router.callback_query(F.data == "admin_stats_green")
@admin_required
async def admin_stats_green(callback: types.CallbackQuery):
    users = db.get_all_users()
    green_users = [u for u in users if get_user_status_details(u)[0] == "🟢"]
    
    if not green_users:
        await callback.answer("Нет пользователей со статусом OK", show_alert=True)
        return
    
    text = "🟢 <b>Всё OK:</b>\n\n"
    for i, user in enumerate(green_users[:20], 1):
        fio = user[3] if len(user) > 3 else "Не указано"
        rank = user[4] if len(user) > 4 else "Не указано"
        fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
        rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
        text += f"{i}. {fio_safe} - {rank_safe}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_stats")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_stats_yellow")
@admin_required
async def admin_stats_yellow(callback: types.CallbackQuery):
    users = db.get_all_users()
    yellow_users = [u for u in users if get_user_status_details(u)[0] == "⚠️"]
    
    if not yellow_users:
        await callback.answer("Нет пользователей со статусом Внимание", show_alert=True)
        return
    
    text = "⚠️ <b>Внимание (истекает в 30 дней):</b>\n\n"
    for i, user in enumerate(yellow_users[:20], 1):
        fio = user[3] if len(user) > 3 else "Не указано"
        rank = user[4] if len(user) > 4 else "Не указано"
        fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
        rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
        text += f"{i}. {fio_safe} - {rank_safe}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_stats")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_stats_red")
@admin_required
async def admin_stats_red(callback: types.CallbackQuery):
    users = db.get_all_users()
    red_users = [u for u in users if get_user_status_details(u)[0] == "🛑"]
    
    if not red_users:
        await callback.answer("Нет пользователей со статусом Запрещено", show_alert=True)
        return
    
    text = "🛑 <b>Запрещено:</b>\n\n"
    for i, user in enumerate(red_users[:20], 1):
        fio = user[3] if len(user) > 3 else "Не указано"
        rank = user[4] if len(user) > 4 else "Не указано"
        fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
        rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
        bans = check_flight_ban(user)
        text += f"{i}. {fio_safe} - {rank_safe}\n"
        for ban in bans:
            ban_safe = str(ban).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            text += f"   • {ban_safe}\n"
        text += "\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_stats")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# ============================================================
# УПРАВЛЕНИЕ АДМИНАМИ
# ============================================================

@router.callback_query(F.data == "admin_manage")
@admin_required
async def admin_manage(callback: types.CallbackQuery):
    text = "👥 <b>Управление администраторами</b>\n\nВыберите действие:\n\n➕ Добавить админа\n➖ Удалить админа"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить админа", callback_data="admin_add_admin")],
        [InlineKeyboardButton(text="➖ Удалить админа", callback_data="admin_remove_admin")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_add_admin")
@admin_required
async def admin_add_admin_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может добавлять", show_alert=True)
        return
    await callback.message.edit_text(
        "➕ <b>Добавление админа</b>\n\nВведите username (без @ или с @):\n\nПример: username или @username",
        parse_mode="HTML"
    )
    await state.set_state(AddAdminState.username)
    await callback.answer()

@router.message(AddAdminState.username, F.text)
@admin_required_message
async def admin_add_admin_by_username(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Только главный админ", parse_mode="HTML")
        await state.clear()
        return
    username = message.text.strip().lstrip('@')
    user = db.find_user_by_username(username)
    if not user:
        await message.answer(f"❌ Пользователь @{username} не найден!", parse_mode="HTML")
        await state.clear()
        return
    db.add_admin(user['user_id'], username, message.from_user.id)
    await message.answer(f"✅ @{username} добавлен в админы!", parse_mode="HTML")
    await state.clear()

@router.callback_query(F.data == "admin_remove_admin")
@admin_required
async def admin_remove_admin_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может удалять", show_alert=True)
        return
    admins = db.get_all_admins()
    if not admins:
        await callback.message.edit_text("📋 <b>Нет админов в БД</b> (кроме config)", parse_mode="HTML")
        await callback.answer()
        return
    text = "➖ <b>Удаление админа</b>\n\nТекущие админы:\n\n"
    for admin in admins:
        username = admin.get('username') or "не указан"
        user_id = admin.get('user_id')
        text += f"• ID: <code>{user_id}</code> (@{username})\n"
    text += "\n<i>Введите ID для удаления:</i>"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_manage")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(RemoveAdminState.user_id)
    await callback.answer()

@router.message(RemoveAdminState.user_id, F.text)
@admin_required_message
async def admin_remove_admin_by_id(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Только главный админ", parse_mode="HTML")
        await state.clear()
        return
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите число (ID)", parse_mode="HTML")
        return
    if user_id in ADMIN_IDS:
        await message.answer("❌ Нельзя удалить главного админа из config!", parse_mode="HTML")
        await state.clear()
        return
    admins = db.get_all_admins()
    admin_exists = any(admin.get('user_id') == user_id for admin in admins)
    if not admin_exists:
        await message.answer(f"❌ Админ с ID {user_id} не найден!", parse_mode="HTML")
        await state.clear()
        return
    try:
        db.remove_admin(user_id)
        await message.answer(f"✅ Админ с ID {user_id} удалён!", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")
        await message.answer(f"❌ Ошибка: {str(e)}", parse_mode="HTML")
    finally:
        await state.clear()
