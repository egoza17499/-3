import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db_manager import db
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
    
    # Ищем аэродром
    aerodrome = db.get_aerodrome_by_search(search_text)
    
    if not aerodrome:
        logger.warning(f"❌ Не найдено по запросу: {search_text}")
        await message.answer(
            f"❌ Информация по запросу \"{search_text}\" не найдена.\n\n"
            "Попробуйте другое название города или аэродрома."
        )
        return
    
    logger.info(f"✅ Найдено: {aerodrome['name']} ({aerodrome['city']})")
    
    # Формируем ответ
    city = aerodrome['city'] or aerodrome['name']
    airport = aerodrome['airport_name'] or ""
    housing = aerodrome['housing_info'] or "Информация уточняется"
    
    text = f"🏙 {city}"
    if airport:
        text += f"\n✈️ Аэродром: {airport}"
    text += f"\n🏠 Жилье: {housing}\n\n"
    
    # Телефоны
    phones = db.get_aerodrome_phones(aerodrome['id'])
    if phones:
        text += "📞 Полезные номера телефонов:\n"
        for phone in phones:
            text += f"• {phone['phone_name']}: {phone['phone_number']}\n"
        text += "\n"
    
    # Документы
    documents = db.get_aerodrome_documents(aerodrome['id'])
    
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
    documents = db.get_aerodrome_documents(aerodrome_id)
    
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
