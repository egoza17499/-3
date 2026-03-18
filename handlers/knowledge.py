import logging
import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import BufferedInputFile
from db_manager import (
    get_aerodromes_by_city,
    get_aerodrome_by_id,
    get_aerodrome_phones,
    get_aerodrome_documents,
    get_safety_block_by_number
)
from states import KnowledgeState
from utils.yandex_disk_client import YandexDiskClient
from config import YANDEX_DISK_TOKEN

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def format_phone_link(phone_number):
    """
    Создает HTML-ссылку tel: для кликабельного номера телефона
    """
    if not phone_number:
        return phone_number
    
    clean_number = re.sub(r'[^\d+]', '', phone_number)
    
    if clean_number.startswith('8'):
        clean_number = '+7' + clean_number[1:]
    elif clean_number.startswith('7'):
        clean_number = '+' + clean_number
    
    return f"<a href='tel:{clean_number}'>{phone_number}</a>"

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
    
    if re.match(r'^(блок\s*№?\s*\d+)$', search_text, re.IGNORECASE):
        logger.info(f"⏭️ Пропускаем команду блока: '{search_text}'")
        return
    
    logger.info(f"✈️ Поиск аэродрома: '{search_text}'")
    
    aerodromes = get_aerodromes_by_city(search_text)
    
    if not aerodromes:
        logger.warning(f"❌ Не найдено по запросу: {search_text}")
        await message.answer(
            f"❌ Информация по запросу \"{search_text}\" не найдена.\n\n"
            "Попробуйте другое название города или аэродрома."
        )
        return
    
    logger.info(f"✅ Найдено аэродромов: {len(aerodromes)}")
    
    if len(aerodromes) == 1:
        await show_aerodrome_details(message, aerodromes[0])
        return
    
    await show_aerodrome_selection(message, aerodromes, search_text)

async def show_aerodrome_selection(message: types.Message, aerodromes: list, search_text: str):
    """Показать список аэродромов для выбора"""
    city_name = aerodromes[0]['city'] or search_text
    
    text = f"🏙️ <b>В городе {city_name} найдено аэродромов: {len(aerodromes)}</b>\n\n"
    text += "Выберите нужный аэродром:\n\n"
    
    keyboard_buttons = []
    for aero in aerodromes:
        display_name = aero['airport_name'] if aero['airport_name'] else aero['name']
        text += f"• {display_name}\n"
        
        keyboard_buttons.append([InlineKeyboardButton(
            text=f"🛫 {display_name}",
            callback_data=f"aerodrome_select_{aero['id']}"
        )])
    
    keyboard_buttons.append([InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="info_aerodrome_btn"
    )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")

async def show_aerodrome_details(message: types.Message, aerodrome: dict):
    """Показать подробную информацию об аэродроме"""
    logger.info(f"✅ Показываем детали: {aerodrome['name']} ({aerodrome['city']})")
    
    city = aerodrome['city'] or aerodrome['name']
    airport = aerodrome['airport_name'] or ""
    housing = aerodrome['housing_info'] or "Информация уточняется"
    
    text = f"🏙 {city}"
    if airport:
        text += f"\n✈️ Аэродром: {airport}"
    text += f"\n🏠 Жилье: {housing}\n\n"
    
    phones = get_aerodrome_phones(aerodrome['id'])
    if phones:
        text += "📞 <b>Полезные номера телефонов:</b>\n\n"
        for phone in phones:
            phone_name = phone['phone_name']
            phone_number = phone['phone_number']
            clickable_phone = format_phone_link(phone_number)
            text += f"• {phone_name}: {clickable_phone}\n"
        text += "\n<i>📱 Нажмите на номер чтобы позвонить</i>\n\n"
    
    documents = get_aerodrome_documents(aerodrome['id'])
    
    keyboard_buttons = []
    
    if documents:
        keyboard_buttons.append([InlineKeyboardButton(
            text="📄 Полезные документы",
            callback_data=f"aero_docs_{aerodrome['id']}"
        )])
    
    keyboard_buttons.append([InlineKeyboardButton(
        text="🔍 Повторный поиск",
        callback_data="info_aerodrome_btn"
    )])
    
    keyboard_buttons.append([InlineKeyboardButton(
        text="✏️ Редактировать",
        callback_data=f"edit_aerodrome_{aerodrome['id']}"
    )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")

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
        doc_type = doc.get('doc_type') or 'Документ'
        text += f"• {doc['doc_name']} ({doc_type})\n"
    
    await callback.message.answer(text)
    await callback.answer()

# ============================================================
# ЗНАНИЯ О САМОЛЕТЕ — ИЗМЕНЕНО!
# ============================================================

@router.callback_query(F.data == "info_aircraft")
async def info_aircraft(callback: types.CallbackQuery):
    """Показываем кнопки с модификациями самолета"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Ил-76МД", callback_data="aircraft_il76md")],
        [InlineKeyboardButton(text="✈️ Ил-76МД-М", callback_data="aircraft_il76mdm")],
        [InlineKeyboardButton(text="✈️ Ил-76МД-90А", callback_data="aircraft_il76md90a")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="info_back")]
    ])
    
    await callback.message.edit_text(
        "✈️ Полезные сведения о самолете\n\n"
        "Выберите модификацию:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data == "aircraft_il76md")
async def aircraft_il76md_files(callback: types.CallbackQuery):
    """Показываем файлы для Ил-76МД"""
    await show_yandex_files(callback, "Il-76MD", "Ил-76МД")

@router.callback_query(F.data == "aircraft_il76mdm")
async def aircraft_il76mdm_files(callback: types.CallbackQuery):
    """Показываем файлы для Ил-76МД-М"""
    await show_yandex_files(callback, "Il-76MD-M", "Ил-76МД-М")

@router.callback_query(F.data == "aircraft_il76md90a")
async def aircraft_il76md90a_files(callback: types.CallbackQuery):
    """Показываем файлы для Ил-76МД-90А"""
    await show_yandex_files(callback, "Il-76MD-90A", "Ил-76МД-90А")

async def show_yandex_files(callback: types.CallbackQuery, folder_path: str, aircraft_name: str):
    """Показываем список файлов из Яндекс Диска (ПАПКИ В КОРНЕ!)"""
    try:
        disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
        
        # Получаем список файлов из папки В КОРНЕ диска
        files = await disk_client.list_files(f"/{folder_path}")
        
        if not files:
            await callback.answer(f"📁 В папке {aircraft_name} пока нет файлов", show_alert=True)
            return
        
        keyboard_buttons = []
        for file_info in files:
            file_name = file_info.get('name', 'Без названия')
            file_path = file_info.get('path', '')
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"📄 {file_name}",
                callback_data=f"download_file_{folder_path}___{file_name}"
            )])
        
        keyboard_buttons.append([InlineKeyboardButton(
            text="🔙 Назад к самолетам",
            callback_data="info_aircraft"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            f"✈️ <b>{aircraft_name}</b>\n\n"
            f"📁 Доступные файлы:\n\n"
            f"Нажмите на файл для скачивания:",
            reply_markup=keyboard
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка файлов: {e}")
        await callback.answer("❌ Ошибка при получении списка файлов", show_alert=True)

@router.callback_query(F.data.startswith("download_file_"))
async def download_file_handler(callback: types.CallbackQuery):
    """Скачиваем и отправляем файл"""
    try:
        data = callback.data.replace("download_file_", "")
        folder_path, file_name = data.split("___")
        
        # ПУТЬ В КОРНЕ ДИСКА (не в /Blocks/!)
        full_path = f"/{folder_path}/{file_name}"
        
        await callback.answer("⏳ Загрузка файла...", show_alert=False)
        
        disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
        file_content = await disk_client.download_file(full_path)
        
        if file_name.endswith('.pdf'):
            media_type = 'document'
        elif file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            media_type = 'photo'
        else:
            media_type = 'document'
        
        file_buffer = BufferedInputFile(file_content, filename=file_name)
        
        if media_type == 'photo':
            await callback.message.answer_photo(
                photo=file_buffer,
                caption=f"📄 {file_name}"
            )
        else:
            await callback.message.answer_document(
                document=file_buffer,
                caption=f"📄 {file_name}"
            )
        
        await callback.answer("✅ Файл отправлен!")
        
    except Exception as e:
        logger.error(f"Ошибка при скачивании файла: {e}")
        await callback.answer("❌ Ошибка при скачивании файла", show_alert=True)

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
    block = get_safety_block_by_number(block_number)
    
    if not block:
        await callback.answer("❌ Блок не найден", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"🛡️ Блок безопасности №{block_number}\n\n"
        f"{block['block_text']}"
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
