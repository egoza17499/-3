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

class AdminListState(StatesGroup):
    waiting_for_search = State()

# Состояния для базы знаний
class AdminKnowledgeState(StatesGroup):
    # Аэродромы
    aero_add_name = State()
    aero_add_city = State()
    aero_add_airport = State()
    aero_add_housing = State()
    aero_add_phone_name = State()
    aero_add_phone_number = State()
    aero_add_doc_name = State()
    aero_add_doc_file = State()
    
    # Блоки безопасности
    safety_add_number = State()
    safety_add_text = State()
    
    # Знания по самолётам
    aircraft_add_type = State()
    aircraft_add_name = State()
    aircraft_add_text = State()
    aircraft_add_file = State()

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_list")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📚 Управление базой знаний", callback_data="admin_knowledge")],
        [InlineKeyboardButton(text="✈️ Заполнить базу аэродромов", callback_data="admin_fill_airports")],
        [InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_manage")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])

@router.callback_query(lambda c: c.data == "admin_back")
async def admin_back(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    is_admin = callback.from_user.id in ADMIN_IDS or db.check_admin_status(callback.from_user.id, callback.from_user.username)
    from handlers.menu import get_main_keyboard
    await callback.message.edit_text("Главное меню", reply_markup=get_main_keyboard(is_admin))
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_list")
async def admin_list(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    users = db.get_all_users()
    
    if not users:
        text = "📋 Список пользователей:\n\n"
        text += "Пользователей пока нет"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        return
    
    text = "📋 Список пользователей:\n\n"
    text += "💡 *Введите фамилию или имя для поиска*\n\n"
    
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
    
    text += "\n*Введите текст для поиска или нажмите Назад*"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(AdminListState.waiting_for_search)
    await callback.answer()

@router.message(AdminListState.waiting_for_search)
async def admin_list_search_handler(message: types.Message):
    search_text = message.text.strip()
    
    if len(search_text) < 2:
        await message.answer("⚠️ Введите минимум 2 символа для поиска")
        return
    
    users = db.search_users(search_text)
    
    if not users:
        await message.answer(
            f"❌ Пользователи по запросу \"{search_text}\" не найдены\n\n"
            f"Попробуйте другую фамилию или имя"
        )
        return
    
    if len(users) == 1:
        user = users[0]
        profile_text = generate_profile_text(user)
        warnings, bans = check_date_warnings(user)
        
        if warnings:
            profile_text += "\n⚠️ *СКОРО ИСТЕКАЕТ:*\n" + "\n".join([f"• {w}" for w in warnings])
        
        if bans:
            profile_text += "\n\n⛔ *ЗАПРЕЩЕНО:*\n" + "\n".join([f"• {b}" for b in bans])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")]
        ])
        
        await message.answer(profile_text, reply_markup=keyboard, parse_mode="Markdown")
    else:
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
        
        text += "\n*Введите другой запрос для поиска или нажмите Назад*"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")]
        ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(lambda c: c.data == "admin_functions_back")
async def admin_functions_back(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    text = "🛡 Административные функции\n\nВыберите действие:"
    
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
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

# ==================== УПРАВЛЕНИЕ БАЗОЙ ЗНАНИЙ ====================

@router.callback_query(lambda c: c.data == "admin_knowledge")
async def admin_knowledge(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS and not db.check_admin_status(callback.from_user.id, callback.from_user.username):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    text = "📚 Управление базой знаний\n\n"
    text += "Выберите раздел:\n\n"
    text += "✈️ Аэродромы\n"
    text += "🛡 Блоки безопасности\n"
    text += "📖 Знания по самолётам"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Аэродромы", callback_data="admin_knowledge_aerodromes")],
        [InlineKeyboardButton(text="🛡 Блоки безопасности", callback_data="admin_knowledge_safety")],
        [InlineKeyboardButton(text="📖 Знания по самолётам", callback_data="admin_knowledge_aircraft")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

# ==================== АЭРОДРОМЫ (АДМИН) ====================

@router.callback_query(lambda c: c.data == "admin_knowledge_aerodromes")
async def admin_knowledge_aerodromes(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить аэродром", callback_data="admin_aero_add")],
        [InlineKeyboardButton(text="📋 Список аэродромов", callback_data="admin_aero_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_knowledge")]
    ])
    
    await callback.message.edit_text(
        "✈️ Управление аэродромами\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_aero_add")
async def admin_aero_add_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "➕ Добавление аэродрома\n\n"
        "Введите название города/аэродрома:\n\n"
        "Пример: Нижний Новгород"
    )
    await state.set_state(AdminKnowledgeState.aero_add_name)
    await callback.answer()

@router.message(AdminKnowledgeState.aero_add_name)
async def admin_aero_add_name(message: types.Message, state: FSMContext):
    await state.update_data(aero_name=message.text.strip())
    await message.answer("Теперь введите название аэродрома (если отличается от города):\n\nПример: Стригино\n\nИли напишите 'пропустить':")
    await state.set_state(AdminKnowledgeState.aero_add_airport)

@router.message(AdminKnowledgeState.aero_add_airport)
async def admin_aero_add_airport(message: types.Message, state: FSMContext):
    airport = message.text.strip()
    if airport.lower() == 'пропустить':
        airport = None
    await state.update_data(aero_airport=airport)
    await message.answer("Введите информацию о жилье:\n\nПример: Предоставляется бесплатно / Не предоставляется / Требуется справка")
    await state.set_state(AdminKnowledgeState.aero_add_housing)

@router.message(AdminKnowledgeState.aero_add_housing)
async def admin_aero_add_housing(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_aerodrome(
        name=data['aero_name'],
        city=data['aero_name'],
        airport_name=data.get('aero_airport'),
        housing_info=message.text.strip(),
        created_by=message.from_user.id
    )
    await message.answer("✅ Аэродром добавлен!\n\nТеперь добавьте телефоны (или напишите 'готово'):")
    await state.set_state(AdminKnowledgeState.aero_add_phone_name)

@router.message(AdminKnowledgeState.aero_add_phone_name)
async def admin_aero_add_phone_name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'готово':
        await state.clear()
        await message.answer("✅ Аэродром полностью добавлен!")
        return
    
    await state.update_data(phone_name=message.text.strip())
    await message.answer("Введите номер телефона:")
    await state.set_state(AdminKnowledgeState.aero_add_phone_number)

@router.message(AdminKnowledgeState.aero_add_phone_number)
async def admin_aero_add_phone_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    aerodrome = db.get_aerodrome_by_search(data['aero_name'])
    
    if aerodrome:
        db.add_aerodrome_phone(aerodrome['id'], data['phone_name'], message.text.strip())
        await message.answer("✅ Телефон добавлен!\n\nДобавьте ещё телефон или напишите 'готово':")
        await state.set_state(AdminKnowledgeState.aero_add_phone_name)
    else:
        await message.answer("❌ Ошибка! Аэродром не найден.")
        await state.clear()

# ==================== БЛОКИ БЕЗОПАСНОСТИ (АДМИН) ====================

@router.callback_query(lambda c: c.data == "admin_knowledge_safety")
async def admin_knowledge_safety(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить блок", callback_data="admin_safety_add")],
        [InlineKeyboardButton(text="📋 Список блоков", callback_data="admin_safety_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_knowledge")]
    ])
    
    await callback.message.edit_text(
        "🛡 Управление блоками безопасности\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_safety_add")
async def admin_safety_add_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "➕ Добавление блока безопасности\n\n"
        "Введите номер блока:\n\n"
        "Пример: 1"
    )
    await state.set_state(AdminKnowledgeState.safety_add_number)
    await callback.answer()

@router.message(AdminKnowledgeState.safety_add_number)
async def admin_safety_add_number(message: types.Message, state: FSMContext):
    try:
        block_number = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите корректный номер (число)")
        return
    
    # Проверяем что блок с таким номером ещё не существует
    existing = db.get_safety_block_by_number(block_number)
    if existing:
        await message.answer(f"❌ Блок №{block_number} уже существует!\n\nВведите другой номер:")
        return
    
    await state.update_data(safety_number=block_number)
    await message.answer("Теперь отправьте текст блока:")
    await state.set_state(AdminKnowledgeState.safety_add_text)

@router.message(AdminKnowledgeState.safety_add_text)
async def admin_safety_add_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_safety_block(
        block_number=data['safety_number'],
        block_text=message.text,
        created_by=message.from_user.id
    )
    await message.answer(f"✅ Блок безопасности №{data['safety_number']} добавлен!")
    await state.clear()

# ==================== ЗНАНИЯ ПО САМОЛЕТАМ (АДМИН) ====================

@router.callback_query(lambda c: c.data == "admin_knowledge_aircraft")
async def admin_knowledge_aircraft(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить знание", callback_data="admin_aircraft_add")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_knowledge")]
    ])
    
    await callback.message.edit_text(
        "📖 Управление знаниями по самолётам\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_aircraft_add")
async def admin_aircraft_add_start(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Ил-76 МД", callback_data="aircraft_type_il76md")],
        [InlineKeyboardButton(text="✈️ Ил-76 МД-М", callback_data="aircraft_type_il76mdm")],
        [InlineKeyboardButton(text="✈️ Ил-76 МД-90А", callback_data="aircraft_type_il76md90a")]
    ])
    
    await callback.message.edit_text(
        "➕ Добавление знания по самолёту\n\n"
        "Выберите тип самолёта:",
        reply_markup=keyboard
    )
    await state.set_state(AdminKnowledgeState.aircraft_add_type)
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("aircraft_type_"))
async def admin_aircraft_type_select(callback: types.CallbackQuery, state: FSMContext):
    aircraft_map = {
        "aircraft_type_il76md": "Ил-76 МД",
        "aircraft_type_il76mdm": "Ил-76 МД-М",
        "aircraft_type_il76md90a": "Ил-76 МД-90А"
    }
    
    aircraft_type = aircraft_map.get(callback.data)
    await state.update_data(aircraft_type=aircraft_type)
    
    await callback.message.edit_text(
        f"✈️ {aircraft_type}\n\n"
        "Введите название материала:\n\n"
        "Пример: Руководство по эксплуатации"
    )
    await state.set_state(AdminKnowledgeState.aircraft_add_name)
    await callback.answer()

@router.message(AdminKnowledgeState.aircraft_add_name)
async def admin_aircraft_add_name(message: types.Message, state: FSMContext):
    await state.update_data(knowledge_name=message.text.strip())
    await message.answer("Теперь отправьте текст материала (или напишите 'пропустить' если только файл):")
    await state.set_state(AdminKnowledgeState.aircraft_add_text)

@router.message(AdminKnowledgeState.aircraft_add_text)
async def admin_aircraft_add_text(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() == 'пропустить':
        text = None
    await state.update_data(knowledge_text=text)
    await message.answer("✅ Знание добавлено!")
    
    data = await state.get_data()
    db.add_aircraft_knowledge(
        aircraft_type=data['aircraft_type'],
        knowledge_name=data['knowledge_name'],
        knowledge_text=data.get('knowledge_text')
    )
    
    await state.clear()

# ==================== ОСТАЛЬНЫЕ ФУНКЦИИ ====================

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
    await state.clear()
    
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
    await state.clear()
    
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
