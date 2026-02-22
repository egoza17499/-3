import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db_manager import (
    get_aerodromes_by_city,
    get_aerodrome_by_id,
    get_aerodrome_phones,
    get_aerodrome_documents
)
from states import KnowledgeState

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# ИНФОРМАЦИЯ
# ============================================================

@router.callback_query(F.data == "info")
async def info_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📚 Полезная информация\n\n"
        "Выберите раздел:"
    )
    await callback.answer()

# ============================================================
# АЭРОДРОМЫ
# ============================================================

@router.callback_query(F.data == "info_aerodrome")
async def info_aerodrome(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✈️ Поиск информации об аэродроме\n\n"
        "Пожалуйста, напишите название аэродрома или города,\n"
        "информация о котором вас интересует"
    )
    await state.set_state(KnowledgeState.aerodrome_search)
    await callback.answer()

@router.message(KnowledgeState.aerodrome_search)
async def aerodrome_search_handler(message: types.Message):
    logger.info(f"🔍 ДОШЛО ДО ОБРАБОТЧИКА! Текст: {message.text}")
    
    search_text = message.text.strip()
    logger.info(f"✈️ Поиск аэродрома: '{search_text}'")
    
    # Ищем ВСЕ аэродромы в городе
    aerodromes = get_aerodromes_by_city(search_text)
    
    if not aerodromes:
        logger.warning(f"❌ Не найдено по запросу: {search_text}")
        await message.answer(
            f"❌ Информация по запросу \"{search_text}\" не найдена.\n\n"
            "Попробуйте другое название города или аэродрома."
        )
        return
    
    logger.info(f"✅ Найдено аэродромов: {len(aerodromes)}")
    
    # Если найден только один аэродром - показываем его сразу
    if len(aerodromes) == 1:
        await show_aerodrome_details(message, aerodromes[0])
        return
    
    # Если несколько аэродромов - показываем список с выбором
    await show_aerodrome_selection(message, aerodromes, search_text)

async def show_aerodrome_selection(message: types.Message, aerodromes: list, search_text: str):
    """Показать список аэродромов для выбора"""
    city_name = aerodromes[0]['city'] or search_text
    
    text = f"🏙️ <b>В городе {city_name} найдено аэродромов: {len(aerodromes)}</b>\n\n"
    text += "Выберите нужный аэродром:\n\n"
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for aero in aerodromes:
        display_name = aero['airport_name'] if aero['airport_name'] else aero['name']
        text += f"• {display_name}\n"
        
        keyboard.add(InlineKeyboardButton(
            f"🛫 {display_name}",
            callback_data=f"aerodrome_select_{aero['id']}"
        ))
    
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="info_aerodrome_btn"))
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_aerodrome_details(message: types.Message, aerodrome: dict):
    """Показать подробную информацию об аэродроме"""
    logger.info(f"✅ Показываем детали: {aerodrome['name']} ({aerodrome['city']})")
    
    # Формируем ответ
    city = aerodrome['city'] or aerodrome['name']
    airport = aerodrome['airport_name'] or ""
    housing = aerodrome['housing_info'] or "Информация уточняется"
    
    text = f"🏙 {city}"
    if airport:
        text += f"\n✈️ Аэродром: {airport}"
    text += f"\n🏠 Жилье: {housing}\n\n"
    
    # Телефоны
    phones = get_aerodrome_phones(aerodrome['id'])
    if phones:
        text += "📞 Полезные номера телефонов:\n"
        for phone in phones:
            text += f"• {phone['phone_name']}: {phone['phone_number']}\n"
        text += "\n"
    
    # Документы
    documents = get_aerodrome_documents(aerodrome['id'])
    
    keyboard = []
    
    if documents:
        keyboard.append([InlineKeyboardButton(
            text="📄 Полезные документы",
            callback_data=f"aero_docs_{aerodrome['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        text="🔍 Повторный поиск",
        callback_data="info_aerodrome_btn"
    )])
    
    keyboard.append([InlineKeyboardButton(
        text="🏠 В главное меню",
        callback_data="info_back"
    )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(text, reply_markup=reply_markup)

# Обработчик выбора аэродрома из списка
@router.callback_query(F.data.startswith("aerodrome_select_"))
async def aerodrome_selected(callback: types.CallbackQuery):
    """Обработчик выбора аэродрома из списка"""
    try:
        aerodrome_id = int(callback.data.split("_")[-1])
        aerodrome = get_aerodrome_by_id(aerodrome_id)
        
        if not aerodrome:
            await callback.answer("❌ Аэродром не найден", show_alert=True)
            return
        
        await show_aerodrome_details(callback.message, aerodrome)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при выборе аэродрома: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

@router.callback_query(F.data == "info_aerodrome_btn")
async def info_aerodrome_back(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✈️ Поиск информации об аэродроме\n\n"
        "Пожалуйста, напишите название аэродрома или города,\n"
        "информация о котором вас интересует"
    )
    await state.set_state(KnowledgeState.aerodrome_search)
    await callback.answer()

@router.callback_query(F.data.startswith("aero_docs_"))
async def aerodrome_documents_show(callback: types.CallbackQuery):
    aerodrome_id = int(callback.data.split("_")[-1])
    documents = get_aerodrome_documents(aerodrome_id)
    
    if not documents:
        await callback.answer("📄 Документы не найдены", show_alert=True)
        return
    
    text = "📄 Полезные документы:\n\n"
    for doc in documents:
        text += f"• {doc['doc_name']}\n"
    
    await callback.message.answer(text)
    await callback.answer()

# ============================================================
# БЛОКИ БЕЗОПАСНОСТИ
# ============================================================

@router.callback_query(F.data == "info_safety")
async def info_safety(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🛡️ Блоки по безопасности полетов\n\n"
        "Выберите номер блока:"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("safety_block_"))
async def safety_block_show(callback: types.CallbackQuery):
    block_number = int(callback.data.split("_")[-1])
    block = db.get_safety_block_by_number(block_number)
    
    if not block:
        await callback.answer("❌ Блок не найден", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"🛡️ Блок безопасности №{block_number}\n\n"
        f"{block['block_text']}"
    )
    await callback.answer()

# ============================================================
# ЗНАНИЯ О САМОЛЕТЕ
# ============================================================

@router.callback_query(F.data == "info_aircraft")
async def info_aircraft(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "✈️ Полезные сведения о самолете\n\n"
        "Выберите тему:"
    )
    await callback.answer()

# ============================================================
# НАЗАД
# ============================================================

@router.callback_query(F.data == "info_back")
async def info_back(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "📚 Полезная информация\n\n"
        "Выберите раздел:"
    )
    await callback.answer()
