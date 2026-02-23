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
router = Router()

# ============================================================
# СОСТОЯНИЯ
# ============================================================

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
            text = "📋 Список пользователей:\n\n"
            text += "Пользователей пока нет"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
            ])
            
            await callback.message.edit_text(text, reply_markup=keyboard)
            await callback.answer()
            return
        
        # Формируем текст с правильным экранированием HTML
        text = "📋 <b>Список пользователей</b>\n\n"
        text += "💡 <i>Введите фамилию или имя для поиска</i>\n\n"
        
        for i, user in enumerate(users, 1):
            # Безопасное получение данных
            user_id = user[0] if len(user) > 0 else 0
            username = user[1] if len(user) > 1 else "Не указан"
            fio = user[3] if len(user) > 3 else "Не указано"
            rank = user[4] if len(user) > 4 else "Не указано"
            
            # Экранируем специальные HTML символы
            fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            username_safe = str(username).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
            
            # Проверяем статус
            try:
                warnings, bans = check_date_warnings(user)
                
                if bans:
                    indicator = "⛔"
                elif warnings:
                    indicator = "⚠️"
                else:
                    indicator = "✅"
            except Exception as e:
                logger.error(f"Ошибка проверки статуса пользователя {user_id}: {e}")
                indicator = "❓"
            
            text += f"{i}. {indicator} <b>{fio_safe}</b>\n"
            text += f"   👤 @{username_safe}\n"
            text += f"   🎖 {rank_safe}\n\n"
            
            # Ограничиваем длину сообщения (Telegram лимит ~4096 символов)
            if len(text) > 3500:
                text += f"\n... и ещё {len(users) - i} пользователей\n"
                break
        
        text += "\n<i>Введите текст для поиска или нажмите Назад</i>"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
        ])
        
        # Используем parse_mode="HTML" вместо Markdown
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(AdminListState.waiting_for_search)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_list: {e}", exc_info=True)
        await callback.message.answer(
            "❌ Произошла ошибка при получении списка пользователей\n\n"
            f"<b>Ошибка:</b> {str(e)}",
            parse_mode="HTML"
        )
        await callback.answer()

@router.message(AdminListState.waiting_for_search)
@admin_required_message
async def admin_list_search_handler(message: types.Message):
    try:
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
                profile_text += "\n⚠️ <b>СКОРО ИСТЕКАЕТ:</b>\n" + "\n".join([f"• {w}" for w in warnings])
            
            if bans:
                profile_text += "\n\n⛔ <b>ЗАПРЕЩЕНО:</b>\n" + "\n".join([f"• {b}" for b in bans])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")]
            ])
            
            await message.answer(profile_text, reply_markup=keyboard, parse_mode="HTML")
        else:
            text = f"🔍 Найдено пользователей: {len(users)}\n\n"
            for i, user in enumerate(users, 1):
                fio = user[3] if len(user) > 3 else "Не указано"
                rank = user[4] if len(user) > 4 else "Не указано"
                username = user[1] if len(user) > 1 else "Не указан"
                
                # Экранируем HTML символы
                fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                username_safe = str(username).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
                
                try:
                    warnings, bans = check_date_warnings(user)
                    
                    if bans:
                        indicator = "⛔"
                    elif warnings:
                        indicator = "⚠️"
                    else:
                        indicator = "✅"
                except:
                    indicator = "❓"
                
                text += f"{i}. {indicator} <b>{fio_safe}</b>\n"
                text += f"   👤 @{username_safe}\n"
                text += f"   🎖 {rank_safe}\n\n"
            
            text += "\n<i>Введите другой запрос для поиска или нажмите Назад</i>"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")]
            ])
            
            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в поиске пользователей: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при поиске")

# ============================================================
# СТАТИСТИКА
# ============================================================

@router.callback_query(F.data == "admin_stats")
@admin_required
async def admin_stats(callback: types.CallbackQuery):
    try:
        users = db.get_all_users()
        total = len(users) if users else 0
        
        ready_users = db.get_users_ready_to_fly()
        cannot_fly_users = db.get_users_cannot_fly()
        
        can_fly = len(ready_users)
        cannot_fly = len(cannot_fly_users)
        
        text = "📊 <b>Статистика:</b>\n\n"
        text += f"👥 Всего пользователей: {total}\n"
        text += f"✅ Готовы к полётам: {can_fly}\n"
        text += f"🚫 Не могут летать: {cannot_fly}\n\n"
        text += "Нажмите на кнопку чтобы увидеть список:"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"✅ Готовы к полётам ({can_fly})", callback_data="admin_stats_ready")],
            [InlineKeyboardButton(text=f"🚫 Не могут летать ({cannot_fly})", callback_data="admin_stats_cannot")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в admin_stats: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)

@router.callback_query(F.data == "admin_stats_ready")
@admin_required
async def admin_stats_show_ready(callback: types.CallbackQuery):
    try:
        users = db.get_users_ready_to_fly()
        
        if not users:
            await callback.answer("Нет пользователей готовых к полётам", show_alert=True)
            return
        
        text = "✅ <b>Готовы к полётам:</b>\n\n"
        for i, user in enumerate(users, 1):
            fio = user[3] if len(user) > 3 else "Не указано"
            rank = user[4] if len(user) > 4 else "Не указано"
            username = user[1] if len(user) > 1 else "Не указан"
            
            # Экранируем HTML символы
            fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            username_safe = str(username).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
            
            text += f"{i}. {fio_safe}\n"
            text += f"   🎖 {rank_safe}\n"
            text += f"   👤 @{username_safe}\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к статистике", callback_data="admin_stats")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в admin_stats_show_ready: {e}", exc_info=True)
        await callback.answer("❌ Ошибка", show_alert=True)

@router.callback_query(F.data == "admin_stats_cannot")
@admin_required
async def admin_stats_show_cannot(callback: types.CallbackQuery):
    try:
        users = db.get_users_cannot_fly()
        
        if not users:
            await callback.answer("Нет пользователей кто не может летать", show_alert=True)
            return
        
        text = "🚫 <b>Не могут летать:</b>\n\n"
        for i, user in enumerate(users, 1):
            fio = user[3] if len(user) > 3 else "Не указано"
            rank = user[4] if len(user) > 4 else "Не указано"
            username = user[1] if len(user) > 1 else "Не указан"
            
            # Экранируем HTML символы
            fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            username_safe = str(username).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
            
            bans = check_flight_ban(user)
            
            text += f"{i}. {fio_safe}\n"
            text += f"   🎖 {rank_safe}\n"
            text += f"   👤 @{username_safe}\n"
            text += f"   Причины:\n"
            for ban in bans:
                ban_safe = str(ban).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                text += f"   • {ban_safe}\n"
            text += "\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к статистике", callback_data="admin_stats")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в admin_stats_show_cannot: {e}", exc_info=True)
        await callback.answer("❌ Ошибка", show_alert=True)

# ============================================================
# УПРАВЛЕНИЕ БАЗОЙ ЗНАНИЙ
# ============================================================

@router.callback_query(F.data == "admin_knowledge")
@admin_required
async def admin_knowledge(callback: types.CallbackQuery):
    text = "📚 <b>Управление базой знаний</b>\n\n"
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
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# ============================================================
# АЭРОДРОМЫ (АДМИН)
# ============================================================

@router.callback_query(F.data == "admin_knowledge_aerodromes")
@admin_required
async def admin_knowledge_aerodromes(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить аэродром", callback_data="admin_aero_add")],
        [InlineKeyboardButton(text="📋 Список аэродромов", callback_data="admin_aero_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_knowledge")]
    ])
    
    await callback.message.edit_text(
        "✈️ <b>Управление аэродромами</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_aero_add")
@admin_required
async def admin_aero_add_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "➕ <b>Добавление аэродрома</b>\n\n"
        "Введите название города/аэродрома:\n\n"
        "Пример: Нижний Новгород",
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aero_add_name)
    await callback.answer()

@router.message(AdminKnowledgeState.aero_add_name)
@admin_required_message
async def admin_aero_add_name(message: types.Message, state: FSMContext):
    await state.update_data(aero_name=message.text.strip())
    await message.answer(
        "Теперь введите название аэродрома (если отличается от города):\n\n"
        "Пример: Стригино\n\n"
        "Или напишите 'пропустить':",
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aero_add_airport)

@router.message(AdminKnowledgeState.aero_add_airport)
@admin_required_message
async def admin_aero_add_airport(message: types.Message, state: FSMContext):
    airport = message.text.strip()
    if airport.lower() == 'пропустить':
        airport = None
    await state.update_data(aero_airport=airport)
    await message.answer(
        "Введите информацию о жилье:\n\n"
        "Пример: Предоставляется бесплатно / Не предоставляется / Требуется справка",
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aero_add_housing)

@router.message(AdminKnowledgeState.aero_add_housing)
@admin_required_message
async def admin_aero_add_housing(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_aerodrome(
        name=data['aero_name'],
        city=data['aero_name'],
        airport_name=data.get('aero_airport'),
        housing_info=message.text.strip(),
        created_by=message.from_user.id
    )
    await message.answer(
        "✅ <b>Аэродром добавлен!</b>\n\n"
        "Теперь добавьте телефоны (или напишите 'готово'):",
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aero_add_phone_name)

@router.message(AdminKnowledgeState.aero_add_phone_name)
@admin_required_message
async def admin_aero_add_phone_name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'готово':
        await state.clear()
        await message.answer("✅ <b>Аэродром полностью добавлен!</b>", parse_mode="HTML")
        return
    
    await state.update_data(phone_name=message.text.strip())
    await message.answer("Введите номер телефона:", parse_mode="HTML")
    await state.set_state(AdminKnowledgeState.aero_add_phone_number)

@router.message(AdminKnowledgeState.aero_add_phone_number)
@admin_required_message
async def admin_aero_add_phone_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    aerodrome = db.get_aerodrome_by_search(data['aero_name'])
    
    if aerodrome:
        db.add_aerodrome_phone(aerodrome['id'], data['phone_name'], message.text.strip())
        await message.answer(
            "✅ <b>Телефон добавлен!</b>\n\n"
            "Добавьте ещё телефон или напишите 'готово':",
            parse_mode="HTML"
        )
        await state.set_state(AdminKnowledgeState.aero_add_phone_name)
    else:
        await message.answer("❌ <b>Ошибка!</b> Аэродром не найден.", parse_mode="HTML")
        await state.clear()

# ============================================================
# БЛОКИ БЕЗОПАСНОСТИ (АДМИН)
# ============================================================

@router.callback_query(F.data == "admin_knowledge_safety")
@admin_required
async def admin_knowledge_safety(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить блок", callback_data="admin_safety_add")],
        [InlineKeyboardButton(text="📋 Список блоков", callback_data="admin_safety_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_knowledge")]
    ])
    
    await callback.message.edit_text(
        "🛡 <b>Управление блоками безопасности</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_safety_add")
@admin_required
async def admin_safety_add_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "➕ <b>Добавление блока безопасности</b>\n\n"
        "Введите номер блока:\n\n"
        "Пример: 1",
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.safety_add_number)
    await callback.answer()

@router.message(AdminKnowledgeState.safety_add_number)
@admin_required_message
async def admin_safety_add_number(message: types.Message, state: FSMContext):
    try:
        block_number = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите корректный номер (число)", parse_mode="HTML")
        return
    
    existing = db.get_safety_block_by_number(block_number)
    if existing:
        await message.answer(
            f"❌ <b>Блок №{block_number}</b> уже существует!\n\n"
            "Введите другой номер:",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(safety_number=block_number)
    await message.answer("Теперь отправьте текст блока:", parse_mode="HTML")
    await state.set_state(AdminKnowledgeState.safety_add_text)

@router.message(AdminKnowledgeState.safety_add_text)
@admin_required_message
async def admin_safety_add_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_safety_block(
        block_number=data['safety_number'],
        block_text=message.text,
        created_by=message.from_user.id
    )
    await message.answer(
        f"✅ <b>Блок безопасности №{data['safety_number']}</b> добавлен!",
        parse_mode="HTML"
    )
    await state.clear()

# ============================================================
# ЗНАНИЯ ПО САМОЛЕТАМ (АДМИН)
# ============================================================

@router.callback_query(F.data == "admin_knowledge_aircraft")
@admin_required
async def admin_knowledge_aircraft(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить знание", callback_data="admin_aircraft_add")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_knowledge")]
    ])
    
    await callback.message.edit_text(
        "📖 <b>Управление знаниями по самолётам</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_aircraft_add")
@admin_required
async def admin_aircraft_add_start(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Ил-76 МД", callback_data="aircraft_type_il76md")],
        [InlineKeyboardButton(text="✈️ Ил-76 МД-М", callback_data="aircraft_type_il76mdm")],
        [InlineKeyboardButton(text="✈️ Ил-76 МД-90А", callback_data="aircraft_type_il76md90a")]
    ])
    
    await callback.message.edit_text(
        "➕ <b>Добавление знания по самолёту</b>\n\n"
        "Выберите тип самолёта:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aircraft_add_type)
    await callback.answer()

@router.callback_query(F.data.startswith("aircraft_type_"))
@admin_required
async def admin_aircraft_type_select(callback: types.CallbackQuery, state: FSMContext):
    aircraft_map = {
        "aircraft_type_il76md": "Ил-76 МД",
        "aircraft_type_il76mdm": "Ил-76 МД-М",
        "aircraft_type_il76md90a": "Ил-76 МД-90А"
    }
    
    aircraft_type = aircraft_map.get(callback.data)
    await state.update_data(aircraft_type=aircraft_type)
    
    await callback.message.edit_text(
        f"✈️ <b>{aircraft_type}</b>\n\n"
        "Введите название материала:\n\n"
        "Пример: Руководство по эксплуатации",
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aircraft_add_name)
    await callback.answer()

@router.message(AdminKnowledgeState.aircraft_add_name)
@admin_required_message
async def admin_aircraft_add_name(message: types.Message, state: FSMContext):
    await state.update_data(knowledge_name=message.text.strip())
    await message.answer(
        "Теперь отправьте текст материала (или напишите 'пропустить' если только файл):",
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aircraft_add_text)

@router.message(AdminKnowledgeState.aircraft_add_text)
@admin_required_message
async def admin_aircraft_add_text(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() == 'пропустить':
        text = None
    await state.update_data(knowledge_text=text)
    await message.answer("✅ <b>Знание добавлено!</b>", parse_mode="HTML")
    
    data = await state.get_data()
    db.add_aircraft_knowledge(
        aircraft_type=data['aircraft_type'],
        knowledge_name=data['knowledge_name'],
        knowledge_text=data.get('knowledge_text')
    )
    
    await state.clear()

# ============================================================
# УПРАВЛЕНИЕ АДМИНАМИ
# ============================================================

@router.callback_query(F.data == "admin_manage")
@admin_required
async def admin_manage(callback: types.CallbackQuery):
    text = "👥 <b>Управление администраторами</b>\n\n"
    text += "Выберите действие:\n\n"
    text += "➕ Добавить админа по username\n"
    text += "➖ Удалить админа"
    
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
    
    # Проверяем что это главный админ из config
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может добавлять админов", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ <b>Добавление админа</b>\n\n"
        "Введите username пользователя (без @ или с @):\n\n"
        "Пример: @username или username",
        parse_mode="HTML"
    )
    await state.set_state(AddAdminState.username)
    await callback.answer()

@router.message(AddAdminState.username)
@admin_required_message
async def admin_add_admin_by_username(message: types.Message, state: FSMContext):
    # Проверяем что это главный админ
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Только главный админ может добавлять админов", parse_mode="HTML")
        await state.clear()
        return
    
    username = message.text.strip().lstrip('@')
    
    user = db.find_user_by_username(username)
    if not user:
        await message.answer(
            f"❌ <b>Пользователь @{username}</b> не найден в базе данных!\n\n"
            "Пользователь должен сначала зарегистрироваться в боте.",
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    db.add_admin(user['user_id'], username, message.from_user.id)
    
    await message.answer(
        f"✅ <b>Пользователь @{username}</b> (ID: {user['user_id']}) добавлен в админы!",
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data == "admin_remove_admin")
@admin_required
async def admin_remove_admin_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    # Проверяем что это главный админ
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Только главный админ может удалять админов", show_alert=True)
        return
    
    admins = db.get_all_admins()
    
    if not admins:
        await callback.message.edit_text(
            "📋 <b>В базе нет дополнительных админов</b> (кроме тех что в config)",
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    text = "➖ <b>Удаление админа</b>\n\n"
    text += "Текущие админы из базы данных:\n\n"
    
    for admin in admins:
        username = admin['username'] or "не указан"
        text += f"• ID: {admin['user_id']} (@{username})\n"
    
    text += "\nВведите ID админа которого хотите удалить:"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(RemoveAdminState.user_id)
    await callback.answer()

@router.message(RemoveAdminState.user_id)
@admin_required_message
async def admin_remove_admin_by_id(message: types.Message, state: FSMContext):
    # Проверяем что это главный админ
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Только главный админ может удалять админов", parse_mode="HTML")
        await state.clear()
        return
    
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите корректный ID (число)", parse_mode="HTML")
        return
    
    if user_id in ADMIN_IDS:
        await message.answer("❌ <b>Нельзя удалить главного админа</b> из config!", parse_mode="HTML")
        await state.clear()
        return
    
    db.remove_admin(user_id)
    
    await message.answer(
        f"✅ <b>Админ с ID {user_id}</b> удалён!",
        parse_mode="HTML"
    )
    await state.clear()

# ============================================================
# ЗАПОЛНЕНИЕ БАЗЫ АЭРОДРОМОВ
# ============================================================

@router.callback_query(F.data == "admin_fill_airports")
@admin_required
async def admin_fill_airports(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ <b>Заполняю базу аэродромов...</b>", parse_mode="HTML")
    await callback.answer()
    
    # Здесь можно вызвать скрипт заполнения
    # from scripts.fill_aerodromes import fill_aerodromes
    # await fill_aerodromes()
    
    await callback.message.edit_text(
        "✅ <b>База аэродромов заполнена!</b>\n\n"
        "(Функция в разработке)",
        parse_mode="HTML"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
    ])
    
    await callback.message.edit_reply_markup(reply_markup=keyboard)
