import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from db_manager import db

logger = logging.getLogger(__name__)
router = Router()

# Состояния для базы знаний
class KnowledgeState(StatesGroup):
    # Аэродромы
    aerodrome_search = State()
    aerodrome_add_name = State()
    aerodrome_add_city = State()
    aerodrome_add_airport = State()
    aerodrome_add_housing = State()
    aerodrome_add_phone_name = State()
    aerodrome_add_phone_number = State()
    
    # Блоки безопасности
    safety_block_search = State()
    safety_block_add_number = State()
    safety_block_add_text = State()
    
    # Знания по самолётам
    aircraft_select = State()

# ==================== ГЛАВНОЕ МЕНЮ ПОЛЕЗНОЙ ИНФОРМАЦИИ ====================

@router.message(lambda msg: msg.text == "📚 Полезная информация")
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

@router.callback_query(lambda c: c.data == "info_back")
async def info_back(callback: types.CallbackQuery):
    from handlers.menu import get_main_keyboard
    is_admin = callback.from_user.id in ADMIN_IDS or db.check_admin_status(callback.from_user.id, callback.from_user.username)
    await callback.message.edit_text("Главное меню", reply_markup=get_main_keyboard(is_admin))
    await callback.answer()

# ==================== БЛОКИ БЕЗОПАСНОСТИ ====================

@router.callback_query(lambda c: c.data == "info_safety")
async def info_safety(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🛡 Блоки по безопасности полетов\n\n"
        "Напишите номер блока, который вам необходим\n\n"
        "Пример: 1 или блок 1 или Блок №1"
    )
    await state.set_state(KnowledgeState.safety_block_search)
    await callback.answer()

@router.message(KnowledgeState.safety_block_search)
async def safety_block_search_handler(message: types.Message):
    # Извлекаем номер из сообщения
    text = message.text.strip().lower()
    
    # Пробуем найти номер в тексте
    import re
    numbers = re.findall(r'\d+', text)
    
    if not numbers:
        await message.answer("❌ Не удалось найти номер блока. Пожалуйста, введите число.")
        return
    
    block_number = int(numbers[0])
    
    # Ищем блок в базе
    block = db.get_safety_block_by_number(block_number)
    
    if not block:
        await message.answer(
            f"❌ Блок №{block_number} не найден в базе.\n\n"
            "Попробуйте другой номер или обратитесь к администратору."
        )
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к блокам", callback_data="info_safety_btn")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="info_back")]
    ])
    
    await message.answer(
        f"🛡 Блок безопасности №{block['block_number']}\n\n"
        f"{block['block_text']}",
        reply_markup=keyboard
    )

@router.callback_query(lambda c: c.data == "info_safety_btn")
async def info_safety_back(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🛡 Блоки по безопасности полетов\n\n"
        "Напишите номер блока, который вам необходим\n\n"
        "Пример: 1 или блок 1 или Блок №1"
    )
    await state.set_state(KnowledgeState.safety_block_search)
    await callback.answer()

# ==================== АЭРОДРОМЫ ====================

@router.callback_query(lambda c: c.data == "info_aerodrome")
async def info_aerodrome(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✈️ Поиск информации об аэродроме\n\n"
        "Пожалуйста, напишите аэродром или город, информация по которому вас интересует"
    )
    await state.set_state(KnowledgeState.aerodrome_search)
    await callback.answer()

@router.message(KnowledgeState.aerodrome_search)
async def aerodrome_search_handler(message: types.Message):
    search_text = message.text.strip()
    
    # Ищем аэродром
    aerodrome = db.get_aerodrome_by_search(search_text)
    
    if not aerodrome:
        await message.answer(
            f"❌ Информация по запросу \"{search_text}\" не найдена.\n\n"
            "Попробуйте другое название города или аэродрома."
        )
        return
    
    # Формируем ответ
    city = aerodrome['city'] or aerodrome['name']
    airport = aerodrome['airport_name'] or ""
    housing = aerodrome['housing_info'] or "Информация уточняется"
    
    text = f"🛫 {city}"
    if airport:
        text += f" (аэродром {airport})"
    text += "\n\n"
    
    # Информация о жилье
    text += f"🏠 Жилье: {housing}\n\n"
    
    # Телефоны
    phones = db.get_aerodrome_phones(aerodrome['id'])
    if phones:
        text += "📞 Полезные номера телефонов:\n"
        for phone in phones:
            text += f"• {phone['phone_name']}: {phone['phone_number']}\n"
        text += "\n"
    
    # Документы
    documents = db.get_aerodrome_documents(aerodrome['id'])
    
    keyboard_buttons = []
    
    if documents:
        keyboard_buttons.append([InlineKeyboardButton(text="📄 Полезные документы", callback_data=f"aero_docs_{aerodrome['id']}")])
    
    keyboard_buttons.append([InlineKeyboardButton(text="🔍 Повторный поиск", callback_data="info_aerodrome_btn")])
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 В главное меню", callback_data="info_back")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "info_aerodrome_btn")
async def info_aerodrome_back(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✈️ Поиск информации об аэродроме\n\n"
        "Пожалуйста, напишите аэродром или город, информация по которому вас интересует"
    )
    await state.set_state(KnowledgeState.aerodrome_search)
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("aero_docs_"))
async def aerodrome_documents_show(callback: types.CallbackQuery):
    aerodrome_id = int(c.data.split("_")[-1])
    
    documents = db.get_aerodrome_documents(aerodrome_id)
    
    if not documents:
        await callback.answer("📄 Документов нет", show_alert=True)
        return
    
    text = "📄 Полезные документы:\n\n"
    keyboard_buttons = []
    
    for i, doc in enumerate(documents, 1):
        text += f"{i}. {doc['doc_name']} ({doc['doc_type']})\n"
        if doc['file_id']:
            keyboard_buttons.append([InlineKeyboardButton(text=f"📥 Скачать: {doc['doc_name']}", callback_data=f"aero_file_{doc['id']}")])
    
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад к аэродрому", callback_data="info_aerodrome_btn")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

# ==================== ЗНАНИЯ ПО САМОЛЕТАМ ====================

@router.callback_query(lambda c: c.data == "info_aircraft")
async def info_aircraft(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Ил-76 МД", callback_data="aircraft_il76md")],
        [InlineKeyboardButton(text="✈️ Ил-76 МД-М", callback_data="aircraft_il76mdm")],
        [InlineKeyboardButton(text="✈️ Ил-76 МД-90А", callback_data="aircraft_il76md90a")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="info_back")]
    ])
    
    await callback.message.edit_text(
        "📖 Полезные знания по самолету\n\n"
        "Выберите тип самолета:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("aircraft_"))
async def aircraft_knowledge_show(callback: types.CallbackQuery):
    aircraft_map = {
        "aircraft_il76md": "Ил-76 МД",
        "aircraft_il76mdm": "Ил-76 МД-М",
        "aircraft_il76md90a": "Ил-76 МД-90А"
    }
    
    aircraft_type = aircraft_map.get(callback.data)
    
    if not aircraft_type:
        await callback.answer("❌ Самолет не найден", show_alert=True)
        return
    
    knowledge = db.get_aircraft_knowledge_by_type(aircraft_type)
    
    if not knowledge:
        text = f"✈️ {aircraft_type}\n\n"
        text += "📚 Информация по данному самолету пока не добавлена.\n\n"
        text += "Обратитесь к администратору для добавления материалов."
    else:
        text = f"✈️ {aircraft_type}\n\n"
        text += "📚 Доступные материалы:\n\n"
        
        for i, item in enumerate(knowledge, 1):
            text += f"{i}. {item['knowledge_name']}\n"
            if item['knowledge_text']:
                text += f"   {item['knowledge_text'][:200]}{'...' if len(item['knowledge_text']) > 200 else ''}\n"
            text += "\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к самолетам", callback_data="info_aircraft")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="info_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
