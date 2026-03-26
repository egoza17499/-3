#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📚 handlers/knowledge.py
Полезная информация: аэродромы, телефоны, жильё, документы, блоки безопасности, знания о самолётах
✅ Телефоны кликабельные (tel: ссылки)
✅ Информация о жилье отображается
✅ Блоки безопасности: поиск по номеру + список файлов
✅ Знания о самолётах с Яндекс Диска
✅ Админ-функции: добавление/редактирование аэродромов, блоков, знаний
✅ Защита от незарегистрированных пользователей
"""

import logging
import re
from io import BytesIO
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, 
    InlineKeyboardMarkup, BufferedInputFile, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
)
from states import KnowledgeState, AdminKnowledgeState
from db_manager import (
    get_aerodrome_by_id,
    get_aerodrome_by_search,
    get_aerodromes_by_city,
    get_aerodrome_phones,
    get_aerodrome_documents,
    get_safety_block_by_number,
    get_all_safety_blocks,
    get_aircraft_knowledge_by_type,
    add_aerodrome,
    update_aerodrome,
    delete_aerodrome,
    add_aerodrome_phone,
    delete_aerodrome_phone,
    add_aerodrome_document,
    delete_aerodrome_document,
    add_safety_block,
    update_safety_block,
    delete_safety_block,
    add_aircraft_knowledge,
    delete_aircraft_knowledge,
    get_user,
    db
)
from utils.yandex_disk_client import YandexDiskClient
from config import YANDEX_DISK_TOKEN, ADMIN_IDS
from utils.admin_check import admin_required, admin_required_callback

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def format_phone_link(phone_number: str) -> str:
    """
    Создает HTML-ссылку tel: для кликабельного номера телефона.
    """
    if not phone_number:
        return "Не указан"
    
    if '<a href' in phone_number.lower():
        return phone_number
    
    clean_number = re.sub(r'[^\d+]', '', phone_number)
    
    if clean_number.startswith('+'):
        pass
    elif clean_number.startswith('8') and len(clean_number) == 11:
        clean_number = '+7' + clean_number[1:]
    elif clean_number.startswith('7') and len(clean_number) == 11:
        clean_number = '+' + clean_number
    
    return f"<a href='tel:{clean_number}'>{phone_number}</a>"


def make_back_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """Создать клавиатуру с кнопкой 'Назад'"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data)]
    ])


def make_main_menu_keyboard_small() -> ReplyKeyboardMarkup:
    """Маленькое меню для возврата (2 кнопки как в старом образе)"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Мой профиль")],
            [KeyboardButton(text="📚 Полезная информация")]
        ],
        resize_keyboard=True
    )


def check_registration(message: Message) -> bool:
    """
    Проверка регистрации пользователя.
    """
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if not user or not user.get('is_registered'):
        keyboard = make_main_menu_keyboard_small()
        message.answer(
            "⚠️ <b>Сначала завершите регистрацию!</b>\n\n"
            "Нажмите /start или кнопку '📝 Регистрация' чтобы начать.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return False
    return True


# ============================================================
# ГЛАВНОЕ МЕНЮ ИНФОРМАЦИИ (ПОЛЬЗОВАТЕЛЬ)
# ============================================================

@router.callback_query(F.data == "info")
async def info_handler(callback: CallbackQuery, state: FSMContext):
    """Показать меню полезной информации"""
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Поиск аэродрома", callback_data="info_aerodrome")],
        [InlineKeyboardButton(text="📚 Знания о самолёте", callback_data="info_aircraft")],
        [InlineKeyboardButton(text="🛡️ Блоки безопасности", callback_data="info_safety")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        "📚 <b>Полезная информация</b>\n\n"
        "Выберите раздел:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# ============================================================
# ✈️ ПОИСК АЭРОДРОМА (ПОЛЬЗОВАТЕЛЬ)
# ============================================================

@router.callback_query(F.data == "info_aerodrome")
async def info_aerodrome(callback: CallbackQuery, state: FSMContext):
    """Начать поиск аэродрома"""
    await state.set_state(KnowledgeState.aerodrome_search)
    
    await callback.message.edit_text(
        "✈️ <b>Поиск аэродрома</b>\n\n"
        "Напишите название города или аэродрома:\n"
        "<i>Например: Иваново, Самара, Кубинка</i>",
        reply_markup=make_back_keyboard("info"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(KnowledgeState.aerodrome_search)
async def aerodrome_search_handler(message: Message, state: FSMContext):
    """Обработчик поиска аэродрома по тексту"""
    if not check_registration(message):
        return
    
    search_text = message.text.strip()
    
    # Игнорируем команды для блоков безопасности
    if re.match(r'^(блок\s*№?\s*\d+)$', search_text, re.IGNORECASE):
        return
    
    logger.info(f"✈️ Поиск аэродрома: '{search_text}'")
    
    aerodromes = get_aerodromes_by_city(search_text)
    
    if not aerodromes:
        aerodrome = get_aerodrome_by_search(search_text)
        if aerodrome:
            await show_aerodrome_details(message, aerodrome)
            return
        
        await message.answer(
            f"❌ Аэродромы по запросу <b>\"{search_text}\"</b> не найдены.\n\n"
            "Попробуйте другое название:",
            reply_markup=make_main_menu_keyboard_small(),
            parse_mode="HTML"
        )
        return
    
    if len(aerodromes) == 1:
        await show_aerodrome_details(message, aerodromes[0])
    else:
        await show_aerodrome_selection(message, aerodromes, search_text)


async def show_aerodrome_selection(message: Message, aerodromes: list, search_text: str):
    """Показать список аэродромов для выбора"""
    city_name = aerodromes[0].get('city') or search_text
    
    text = f"🏙️ <b>В городе {city_name} найдено:</b>\n\n"
    
    keyboard_buttons = []
    for aero in aerodromes[:10]:
        display_name = aero.get('airport_name') or aero.get('name')
        city = aero.get('city', '')
        
        text += f"• {display_name}"
        if city and city != city_name:
            text += f" ({city})"
        text += "\n"
        
        keyboard_buttons.append([InlineKeyboardButton(
            text=f"🛫 {display_name}",
            callback_data=f"aerodrome_select_{aero['id']}"
        )])
    
    keyboard_buttons.append([InlineKeyboardButton(
        text="🔙 Назад к поиску",
        callback_data="info_aerodrome"
    )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")


async def show_aerodrome_details(message: Message, aerodrome: dict):
    """Показать подробную информацию об аэродроме"""
    logger.info(f"✅ Показываем детали: {aerodrome.get('name')} ({aerodrome.get('city')})")
    
    name = aerodrome.get('name', 'Неизвестно')
    city = aerodrome.get('city') or name
    airport = aerodrome.get('airport_name')
    housing = aerodrome.get('housing_info')
    
    text = f"🏙 <b>{city}</b>"
    if airport and airport != name:
        text += f"\n✈️ Аэродром: {airport}"
    
    if housing and housing.lower() not in ['нет', 'не указано', 'уточняется', '']:
        text += f"\n🏠 Жильё: {housing}"
    else:
        text += "\n🏠 Жильё: <i>Уточняется</i>"
    
    text += "\n"
    
    phones = get_aerodrome_phones(aerodrome['id'])
    if phones:
        text += "\n📞 <b>Полезные номера:</b>\n"
        for phone in phones:
            phone_name = phone.get('phone_name', 'Не указано')
            phone_number = phone.get('phone_number', '')
            formatted_phone = format_phone_link(phone_number)
            text += f"• {phone_name}: {formatted_phone}\n"
        text += "\n<i>📱 Нажмите на номер чтобы позвонить</i>"
    
    documents = get_aerodrome_documents(aerodrome['id'])
    
    keyboard_buttons = []
    
    if documents:
        keyboard_buttons.append([InlineKeyboardButton(
            text=f"📄 Документы ({len(documents)})",
            callback_data=f"aero_docs_{aerodrome['id']}"
        )])
    
    keyboard_buttons.append([InlineKeyboardButton(
        text="🔍 Ещё поиск",
        callback_data="info_aerodrome"
    )])
    
    keyboard_buttons.append([InlineKeyboardButton(
        text="🔙 В меню информации",
        callback_data="info"
    )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")


@router.callback_query(F.data.startswith("aerodrome_select_"))
async def aerodrome_selected(callback: CallbackQuery):
    """Обработчик выбора аэродрома из списка"""
    try:
        aerodrome_id = int(callback.data.split("_")[-1])
        aerodrome = get_aerodrome_by_id(aerodrome_id)
        
        if not aerodrome:
            await callback.answer("❌ Аэродром не найден", show_alert=True)
            return
        
        await show_aerodrome_details(callback.message, aerodrome)
        await callback.answer()
        
    except (ValueError, IndexError) as e:
        logger.error(f"❌ Ошибка при выборе аэродрома: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("aero_docs_"))
async def aerodrome_documents_show(callback: CallbackQuery):
    """Показать документы аэродрома"""
    try:
        aerodrome_id = int(callback.data.split("_")[-1])
        documents = get_aerodrome_documents(aerodrome_id)
        
        if not documents:
            await callback.answer("📄 Документы не найдены", show_alert=True)
            return
        
        text = "📄 <b>Документы аэродрома:</b>\n\n"
        for doc in documents:
            doc_name = doc.get('doc_name', 'Без названия')
            doc_type = doc.get('doc_type', 'Документ')
            text += f"• {doc_name} <i>({doc_type})</i>\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"aerodrome_select_{aerodrome_id}")]
        ])
        
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except (ValueError, IndexError) as e:
        logger.error(f"❌ Ошибка показа документов: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ============================================================
# 🛡️ БЛОКИ БЕЗОПАСНОСТИ (ПОЛЬЗОВАТЕЛЬ)
# ============================================================

@router.callback_query(F.data == "info_safety")
async def info_safety(callback: CallbackQuery, state: FSMContext):
    """Показать меню блоков безопасности"""
    await state.set_state(KnowledgeState.safety_block_search)
    await callback.message.edit_text(
        "🛡️ <b>Блоки по безопасности полетов</b>\n\n"
        "Напишите номер блока который вам необходим\n\n"
        "Пример: <b>1</b> или <b>блок 1</b> или <b>Блок №1</b>\n\n"
        "<i>Или выберите файл из списка ниже:</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Показать список блоков", callback_data="safety_list_files")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "safety_list_files")
async def safety_list_files(callback: CallbackQuery):
    """Показать список файлов блоков с Яндекс Диска"""
    try:
        if not YANDEX_DISK_TOKEN:
            await callback.answer("⚠️ Токен Яндекс Диска не настроен", show_alert=True)
            return
        
        disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
        files = await disk_client.list_files("/Blocks")
        
        if not files:
            await callback.answer("🛡️ Блоки безопасности пока не добавлены", show_alert=True)
            return
        
        keyboard_buttons = []
        for file_info in files:
            file_name = file_info.get('name', 'Без названия')
            match = re.search(r'blocks?[_\s]?(\d+)', file_name.lower())
            if match:
                block_num = match.group(1)
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"🔹 {file_name}",
                    callback_data=f"safety_file_{block_num}"
                )])
        
        keyboard_buttons.append([InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="info_safety"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            f"🛡️ <b>Блоки безопасности</b>\n\n"
            f"Выберите блок (всего: {len(files)}):",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки списка блоков: {e}")
        await callback.answer("❌ Ошибка при загрузке списка", show_alert=True)


@router.message(KnowledgeState.safety_block_search)
async def safety_block_search_handler(message: Message):
    """Обработчик поиска блока по номеру"""
    try:
        text = message.text.strip().lower()
        numbers = re.findall(r'\d+', text)
        
        if not numbers:
            await message.answer(
                "❌ Не удалось найти номер блока. Пожалуйста, введите число.\n\n"
                "Пример: <b>1</b> или <b>блок 1</b> или <b>Блок №1</b>",
                parse_mode="HTML"
            )
            return
        
        block_number = int(numbers[0])
        
        # Сначала ищем в базе данных
        block = get_safety_block_by_number(block_number)
        if block:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 К списку блоков", callback_data="info_safety")],
                [InlineKeyboardButton(text="🔙 В меню информации", callback_data="info")]
            ])
            
            await message.answer(
                f"🛡️ <b>Блок безопасности №{block_number}</b>\n\n"
                f"{block['block_text']}",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            return
        
        # Если не в базе — ищем на Яндекс Диске
        if not YANDEX_DISK_TOKEN:
            await message.answer("⚠️ Токен Яндекс Диска не настроен")
            return
        
        disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
        files = await disk_client.list_files("/Blocks")
        
        if not files:
            await message.answer("🛡️ Блоки безопасности пока не добавлены")
            return
        
        target_file = None
        for file_info in files:
            file_name = file_info.get('name', '').lower()
            if re.search(rf'blocks?[_\s]?{block_number}', file_name):
                target_file = file_info
                break
        
        if not target_file:
            await message.answer(
                f"❌ Блок №{block_number} не найден.\n\n"
                "Попробуйте другой номер или обратитесь к администратору."
            )
            return
        
        file_name = target_file.get('name', 'block.docx')
        full_path = target_file.get('path')
        
        await message.answer("⏳ Загрузка блока...")
        
        file_content = await disk_client.download_file(full_path)
        
        if not file_content:
            await message.answer("❌ Ошибка скачивания файла")
            return
        
        from aiogram.types import BufferedInputFile
        file_buffer = BufferedInputFile(file_content, filename=file_name)
        
        ext = file_name.lower().split('.')[-1] if '.' in file_name else ''
        
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            await message.answer_photo(
                photo=file_buffer,
                caption=f"🛡️ <b>Блок безопасности №{block_number}</b>",
                parse_mode="HTML"
            )
        else:
            await message.answer_document(
                document=file_buffer,
                caption=f"🛡️ <b>Блок безопасности №{block_number}</b>",
                parse_mode="HTML"
            )
        
        logger.info(f"✅ Блок №{block_number} отправлен пользователю {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке блока: {e}")
        await message.answer("❌ Произошла ошибка при отправке блока")


@router.callback_query(F.data.startswith("safety_file_"))
async def safety_file_show(callback: CallbackQuery):
    """Отправка файла блока по callback"""
    try:
        block_number = callback.data.replace("safety_file_", "")
        
        if not YANDEX_DISK_TOKEN:
            await callback.answer("⚠️ Токен не настроен", show_alert=True)
            return
        
        disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
        files = await disk_client.list_files("/Blocks")
        
        target_file = None
        for file_info in files:
            file_name = file_info.get('name', '').lower()
            if re.search(rf'blocks?[_\s]?{block_number}', file_name):
                target_file = file_info
                break
        
        if not target_file:
            await callback.answer("❌ Файл не найден", show_alert=True)
            return
        
        file_name = target_file.get('name', 'block.docx')
        full_path = target_file.get('path')
        
        await callback.answer("⏳ Загрузка...", show_alert=False)
        
        file_content = await disk_client.download_file(full_path)
        
        if not file_content:
            await callback.answer("❌ Ошибка скачивания", show_alert=True)
            return
        
        from aiogram.types import BufferedInputFile
        file_buffer = BufferedInputFile(file_content, filename=file_name)
        
        ext = file_name.lower().split('.')[-1] if '.' in file_name else ''
        
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            await callback.message.answer_photo(
                photo=file_buffer,
                caption=f"🛡️ <b>Блок безопасности №{block_number}</b>",
                parse_mode="HTML"
            )
        else:
            await callback.message.answer_document(
                document=file_buffer,
                caption=f"🛡️ <b>Блок безопасности №{block_number}</b>",
                parse_mode="HTML"
            )
        
        await callback.answer("✅ Файл отправлен!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки файла: {e}")
        await callback.answer("❌ Ошибка отправки файла", show_alert=True)


# ============================================================
# ✈️ ЗНАНИЯ О САМОЛЁТАХ (ПОЛЬЗОВАТЕЛЬ)
# ============================================================

@router.callback_query(F.data == "info_aircraft")
async def info_aircraft(callback: CallbackQuery):
    """Показать выбор модификаций самолёта"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Ил-76МД", callback_data="aircraft_il76md")],
        [InlineKeyboardButton(text="✈️ Ил-76МД-М", callback_data="aircraft_il76mdm")],
        [InlineKeyboardButton(text="✈️ Ил-76МД-90А", callback_data="aircraft_il76md90a")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="info")]
    ])
    
    await callback.message.edit_text(
        "✈️ <b>Знания о самолёте</b>\n\n"
        "Выберите модификацию:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("aircraft_"))
async def aircraft_files(callback: CallbackQuery):
    """Показать файлы для выбранной модификации"""
    folder_map = {
        "aircraft_il76md": ("Il-76MD", "Ил-76МД"),
        "aircraft_il76mdm": ("Il-76MD-M", "Ил-76МД-М"),
        "aircraft_il76md90a": ("Il-76MD-90A", "Ил-76МД-90А"),
    }
    
    if callback.data not in folder_map:
        await callback.answer("❌ Неизвестная модификация", show_alert=True)
        return
    
    folder_path, aircraft_name = folder_map[callback.data]
    
    try:
        if not YANDEX_DISK_TOKEN:
            await callback.answer("⚠️ Токен Яндекс Диска не настроен", show_alert=True)
            return
        
        disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
        files = await disk_client.list_files(f"/{folder_path}")
        
        if not files:
            await callback.answer(f"📁 В папке {aircraft_name} пока нет файлов", show_alert=True)
            return
        
        keyboard_buttons = []
        for idx, file_info in enumerate(files[:20]):
            file_name = file_info.get('name', 'Без названия')
            file_id = f"{folder_path}_{idx}"
            display_name = file_name[:35] + '…' if len(file_name) > 35 else file_name
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"📄 {display_name}",
                callback_data=f"dl_{file_id}"
            )])
        
        keyboard_buttons.append([InlineKeyboardButton(
            text="🔙 К самолётам",
            callback_data="info_aircraft"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            f"✈️ <b>{aircraft_name}</b>\n\n"
            f"📁 Файлов: {len(files)}\n\n"
            f"Нажмите на файл для скачивания:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения файлов: {e}")
        await callback.answer("❌ Ошибка при загрузке списка", show_alert=True)


@router.callback_query(F.data.startswith("dl_"))
async def download_file_handler(callback: CallbackQuery):
    """Скачать и отправить файл с Яндекс Диска"""
    try:
        file_id = callback.data.replace("dl_", "")
        folder_path, idx = file_id.rsplit("_", 1)
        idx = int(idx)
        
        if not YANDEX_DISK_TOKEN:
            await callback.answer("⚠️ Токен не настроен", show_alert=True)
            return
        
        disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
        files = await disk_client.list_files(f"/{folder_path}")
        
        if idx >= len(files):
            await callback.answer("❌ Файл не найден", show_alert=True)
            return
        
        file_info = files[idx]
        file_name = file_info.get('name', 'file')
        full_path = file_info.get('path')
        
        await callback.answer("⏳ Скачиваю...", show_alert=False)
        
        file_content = await disk_client.download_file(full_path)
        
        if not file_content:
            await callback.answer("❌ Ошибка скачивания", show_alert=True)
            return
        
        file_buffer = BufferedInputFile(file_content, filename=file_name)
        ext = file_name.lower().split('.')[-1] if '.' in file_name else ''
        
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            await callback.message.answer_photo(
                photo=file_buffer,
                caption=f"📄 {file_name}",
                parse_mode="HTML"
            )
        else:
            await callback.message.answer_document(
                document=file_buffer,
                caption=f"📄 {file_name}",
                parse_mode="HTML"
            )
        
        await callback.answer("✅ Файл отправлен!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки файла: {e}")
        await callback.answer("❌ Ошибка отправки файла", show_alert=True)


# ============================================================
# 🛠️ АДМИН: УПРАВЛЕНИЕ БАЗОЙ ЗНАНИЙ
# ============================================================

@router.callback_query(F.data == "admin_knowledge")
@admin_required_callback
async def admin_knowledge(callback: CallbackQuery):
    """Меню управления базой знаний"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Аэродромы", callback_data="admin_knowledge_aerodromes")],
        [InlineKeyboardButton(text="🛡️ Блоки безопасности", callback_data="admin_knowledge_safety")],
        [InlineKeyboardButton(text="📖 Знания по самолётам", callback_data="admin_knowledge_aircraft")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions")]
    ])
    
    await callback.message.edit_text(
        "📚 <b>Управление базой знаний</b>\n\n"
        "Выберите раздел:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# ============================================================
# 🛠️ АДМИН: АЭРОДРОМЫ
# ============================================================

@router.callback_query(F.data == "admin_knowledge_aerodromes")
@admin_required_callback
async def admin_knowledge_aerodromes(callback: CallbackQuery):
    """Меню управления аэродромами"""
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
@admin_required_callback
async def admin_aero_add_start(callback: CallbackQuery, state: FSMContext):
    """Начать добавление аэродрома"""
    await callback.message.edit_text(
        "➕ <b>Добавление аэродрома</b>\n\n"
        "Введите название города/аэродрома:\n\n"
        "Пример: Нижний Новгород",
        reply_markup=make_back_keyboard("admin_knowledge_aerodromes"),
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aero_add_name)
    await callback.answer()


@router.message(AdminKnowledgeState.aero_add_name)
@admin_required
async def admin_aero_add_name(message: Message, state: FSMContext):
    """Обработка названия аэродрома"""
    await state.update_data(aero_name=message.text.strip())
    await message.answer(
        "Теперь введите название аэродрома (если отличается от города):\n\n"
        "Пример: Стригино\n\n"
        "Или напишите 'пропустить':",
        reply_markup=make_back_keyboard("admin_knowledge_aerodromes")
    )
    await state.set_state(AdminKnowledgeState.aero_add_airport)


@router.message(AdminKnowledgeState.aero_add_airport)
@admin_required
async def admin_aero_add_airport(message: Message, state: FSMContext):
    """Обработка названия аэропорта"""
    airport = message.text.strip()
    if airport.lower() == 'пропустить':
        airport = None
    await state.update_data(aero_airport=airport)
    await message.answer(
        "Введите информацию о жилье:\n\n"
        "Пример: Предоставляется бесплатно / Не предоставляется / Требуется справка",
        reply_markup=make_back_keyboard("admin_knowledge_aerodromes")
    )
    await state.set_state(AdminKnowledgeState.aero_add_housing)


@router.message(AdminKnowledgeState.aero_add_housing)
@admin_required
async def admin_aero_add_housing(message: Message, state: FSMContext):
    """Обработка информации о жилье"""
    data = await state.get_data()
    db.add_aerodrome(
        name=data['aero_name'],
        city=data['aero_name'],
        airport_name=data.get('aero_airport'),
        housing_info=message.text.strip(),
        created_by=message.from_user.id
    )
    await message.answer(
        "✅ Аэродром добавлен!\n\n"
        "Теперь добавьте телефоны (или напишите 'готово'):",
        reply_markup=make_back_keyboard("admin_knowledge_aerodromes")
    )
    await state.set_state(AdminKnowledgeState.aero_add_phone_name)


@router.message(AdminKnowledgeState.aero_add_phone_name)
@admin_required
async def admin_aero_add_phone_name(message: Message, state: FSMContext):
    """Обработка названия телефона"""
    if message.text.lower() == 'готово':
        await state.clear()
        await message.answer("✅ Аэродром полностью добавлен!", reply_markup=make_main_menu_keyboard_small())
        return
    await state.update_data(phone_name=message.text.strip())
    await message.answer("Введите номер телефона:", reply_markup=make_back_keyboard("admin_knowledge_aerodromes"))
    await state.set_state(AdminKnowledgeState.aero_add_phone_number)


@router.message(AdminKnowledgeState.aero_add_phone_number)
@admin_required
async def admin_aero_add_phone_number(message: Message, state: FSMContext):
    """Обработка номера телефона"""
    data = await state.get_data()
    aerodrome = db.get_aerodrome_by_search(data['aero_name'])
    if aerodrome:
        db.add_aerodrome_phone(aerodrome['id'], data['phone_name'], message.text.strip())
        await message.answer(
            "✅ Телефон добавлен!\n\n"
            "Добавьте ещё телефон или напишите 'готово':",
            reply_markup=make_back_keyboard("admin_knowledge_aerodromes")
        )
        await state.set_state(AdminKnowledgeState.aero_add_phone_name)
    else:
        await message.answer("❌ Ошибка! Аэродром не найден.")
        await state.clear()


@router.callback_query(F.data == "admin_aero_list")
@admin_required_callback
async def admin_aero_list(callback: CallbackQuery):
    """Список аэродромов для админа"""
    try:
        aerodromes = db.get_all_aerodromes_list()
        
        if not aerodromes:
            await callback.answer("✈️ Аэродромов пока нет", show_alert=True)
            return
        
        text = "✈️ <b>Список аэродромов:</b>\n\n"
        keyboard_buttons = []
        
        for aero in aerodromes[:20]:
            name = aero.get('name', 'Неизвестно')
            city = aero.get('city', '')
            airport = aero.get('airport_name', '')
            
            display = f"{name}"
            if city and city != name:
                display += f" ({city})"
            if airport:
                display += f" - {airport}"
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"✈️ {display[:40]}",
                callback_data=f"admin_aero_edit_{aero['id']}"
            )])
        
        keyboard_buttons.append([InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="admin_knowledge_aerodromes"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            f"{text}\nВыберите аэродром для редактирования:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в admin_aero_list: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ============================================================
# 🛠️ АДМИН: БЛОКИ БЕЗОПАСНОСТИ
# ============================================================

@router.callback_query(F.data == "admin_knowledge_safety")
@admin_required_callback
async def admin_knowledge_safety(callback: CallbackQuery):
    """Меню управления блоками безопасности"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить блок", callback_data="admin_safety_add")],
        [InlineKeyboardButton(text="📋 Список блоков", callback_data="admin_safety_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_knowledge")]
    ])
    
    await callback.message.edit_text(
        "🛡️ <b>Управление блоками безопасности</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_safety_add")
@admin_required_callback
async def admin_safety_add_start(callback: CallbackQuery, state: FSMContext):
    """Начать добавление блока безопасности"""
    await callback.message.edit_text(
        "➕ <b>Добавление блока безопасности</b>\n\n"
        "Введите номер блока:\n\n"
        "Пример: 1",
        reply_markup=make_back_keyboard("admin_knowledge_safety"),
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.safety_add_number)
    await callback.answer()


@router.message(AdminKnowledgeState.safety_add_number)
@admin_required
async def admin_safety_add_number(message: Message, state: FSMContext):
    """Обработка номера блока"""
    try:
        block_number = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите корректный номер (число)")
        return
    
    existing = db.get_safety_block_by_number(block_number)
    if existing:
        await message.answer(f"❌ Блок №{block_number} уже существует!\n\nВведите другой номер:")
        return
    
    await state.update_data(safety_number=block_number)
    await message.answer(
        "Теперь отправьте текст блока:",
        reply_markup=make_back_keyboard("admin_knowledge_safety")
    )
    await state.set_state(AdminKnowledgeState.safety_add_text)


@router.message(AdminKnowledgeState.safety_add_text)
@admin_required
async def admin_safety_add_text(message: Message, state: FSMContext):
    """Обработка текста блока"""
    data = await state.get_data()
    db.add_safety_block(
        block_number=data['safety_number'],
        block_text=message.text,
        created_by=message.from_user.id
    )
    await message.answer(f"✅ Блок безопасности №{data['safety_number']} добавлен!")
    await state.clear()


@router.callback_query(F.data == "admin_safety_list")
@admin_required_callback
async def admin_safety_list(callback: CallbackQuery):
    """Список блоков для админа"""
    try:
        blocks = db.get_all_safety_blocks()
        
        if not blocks:
            await callback.answer("🛡️ Блоков пока нет", show_alert=True)
            return
        
        text = "🛡️ <b>Список блоков безопасности:</b>\n\n"
        keyboard_buttons = []
        
        for block in blocks[:20]:
            num = block.get('block_number')
            text_preview = block.get('block_text', '')[:50] + '...' if len(block.get('block_text', '')) > 50 else block.get('block_text', '')
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"🔹 Блок №{num}",
                callback_data=f"admin_safety_edit_{num}"
            )])
        
        keyboard_buttons.append([InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="admin_knowledge_safety"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            f"{text}\nВыберите блок для редактирования:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в admin_safety_list: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ============================================================
# 🛠️ АДМИН: ЗНАНИЯ ПО САМОЛЁТАМ
# ============================================================

@router.callback_query(F.data == "admin_knowledge_aircraft")
@admin_required_callback
async def admin_knowledge_aircraft(callback: CallbackQuery):
    """Меню управления знаниями по самолётам"""
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
@admin_required_callback
async def admin_aircraft_add_start(callback: CallbackQuery, state: FSMContext):
    """Выбор типа самолёта для добавления знания"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Ил-76МД", callback_data="aircraft_type_il76md")],
        [InlineKeyboardButton(text="✈️ Ил-76МД-М", callback_data="aircraft_type_il76mdm")],
        [InlineKeyboardButton(text="✈️ Ил-76МД-90А", callback_data="aircraft_type_il76md90a")]
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
@admin_required_callback
async def admin_aircraft_type_select(callback: CallbackQuery, state: FSMContext):
    """Выбор типа самолёта"""
    aircraft_map = {
        "aircraft_type_il76md": "Ил-76МД",
        "aircraft_type_il76mdm": "Ил-76МД-М",
        "aircraft_type_il76md90a": "Ил-76МД-90А"
    }
    aircraft_type = aircraft_map.get(callback.data)
    await state.update_data(aircraft_type=aircraft_type)
    
    await callback.message.edit_text(
        f"✈️ {aircraft_type}\n\n"
        "Введите название материала:\n\n"
        "Пример: Руководство по эксплуатации",
        reply_markup=make_back_keyboard("admin_knowledge_aircraft"),
        parse_mode="HTML"
    )
    await state.set_state(AdminKnowledgeState.aircraft_add_name)
    await callback.answer()


@router.message(AdminKnowledgeState.aircraft_add_name)
@admin_required
async def admin_aircraft_add_name(message: Message, state: FSMContext):
    """Обработка названия знания"""
    await state.update_data(knowledge_name=message.text.strip())
    await message.answer(
        "Теперь отправьте текст материала (или напишите 'пропустить' если только файл):",
        reply_markup=make_back_keyboard("admin_knowledge_aircraft")
    )
    await state.set_state(AdminKnowledgeState.aircraft_add_text)


@router.message(AdminKnowledgeState.aircraft_add_text)
@admin_required
async def admin_aircraft_add_text(message: Message, state: FSMContext):
    """Обработка текста знания"""
    text = message.text.strip()
    if text.lower() == 'пропустить':
        text = None
    await state.update_data(knowledge_text=text)
    
    data = await state.get_data()
    db.add_aircraft_knowledge(
        aircraft_type=data['aircraft_type'],
        knowledge_name=data['knowledge_name'],
        knowledge_text=data.get('knowledge_text')
    )
    
    await message.answer("✅ Знание добавлено!")
    await state.clear()


# ============================================================
# НАЗАД / ОТМЕНА
# ============================================================

@router.callback_query(F.data == "info_back")
async def info_back(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню информации"""
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Поиск аэродрома", callback_data="info_aerodrome")],
        [InlineKeyboardButton(text="📚 Знания о самолёте", callback_data="info_aircraft")],
        [InlineKeyboardButton(text="🛡️ Блоки безопасности", callback_data="info_safety")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        "📚 <b>Полезная информация</b>\n\n"
        "Выберите раздел:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(F.text == "/cancel", F.state == KnowledgeState.aerodrome_search)
async def cancel_search(message: Message, state: FSMContext):
    """Отменить поиск аэродрома"""
    await state.clear()
    await message.answer(
        "❌ Поиск отменен.\n\n"
        "Используйте /start для возврата в меню.",
        reply_markup=ReplyKeyboardRemove()
    )
