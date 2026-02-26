import logging
import re
from aiogram import Router, F, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import GROUP_ID
from utils.admin_check import is_admin
from utils.yandex_disk_client import disk_client

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# 🔥 БЛОКИ БЕЗОПАСНОСТИ ИЗ YANDEX DISK
# ✅ Работает и в ЛС, и в группе!
# ============================================================

@router.message(
    F.text.regexp(re.compile(r'^(блок\s*№?\s*\d+)$', re.IGNORECASE))
)
async def group_safety_block_from_disk(message: types.Message):
    """Показать блок безопасности из Yandex Disk"""
    
    # Проверяем что это наша группа ИЛИ личное сообщение
    if message.chat.id != GROUP_ID and message.chat.type != "private":
        return
    
    # ✅ Проверяем что клиент инициализирован
    if disk_client is None:
        logger.error("❌ Yandex Disk клиент не инициализирован! Проверьте токен.")
        await message.answer("❌ Ошибка подключения к хранилищу файлов.")
        return
    
    # Извлекаем номер блока
    text = message.text.lower()
    match = re.search(r'(\d+)', text)
    
    if not match:
        return
    
    block_number = int(match.group(1))
    username = message.from_user.username or f"user_{message.from_user.id}"
    
    logger.info(f"🔍 Запрос блока {block_number} от {username}")
    
    # Ищем файл на Yandex Disk
    files = disk_client.list_files()
    
    # Пробуем разные форматы и названия
    possible_names = [
        f"block_{block_number}.docx",
        f"block_{block_number}.pdf",
        f"block_{block_number}.txt",
        f"blocks_{block_number}.docx",
        f"blocks_{block_number}.pdf",
        f"blocks_{block_number}.txt",
        f"блок_{block_number}.docx",
        f"блок_{block_number}.pdf",
        f"блок_{block_number}.txt",
        f"блоки_{block_number}.docx",
        f"блоки_{block_number}.pdf",
        f"блоки_{block_number}.txt",
        f"Блок_{block_number}.docx",
        f"Блок_{block_number}.pdf",
        f"Блок_{block_number}.txt",
        f"Блоки_{block_number}.docx",
        f"Блоки_{block_number}.pdf",
    ]
    
    file_info = None
    for name in possible_names:
        file_info = next((f for f in files if f['name'].lower() == name.lower()), None)
        if file_info:
            logger.info(f"✅ Найден файл: {file_info['name']}")
            break
    
    if not file_info:
        await message.answer(
            f"❌ <b>Блок №{block_number} не найден!</b>\n\n"
            "Используйте /блоки для просмотра списка.",
            parse_mode="HTML"
        )
        return
    
    # 🔥 СКАЧИВАЕМ ФАЙЛ В ПАМЯТЬ (вместо получения ссылки!)
    file_content = disk_client.download_file(file_info['name'])
    
    if not file_content:
        await message.answer("❌ Ошибка при скачивании файла.")
        return
    
    # Форматируем размер
    file_size = file_info['size']
    size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
    
    # 🔥 ОТПРАВЛЯЕМ ФАЙЛ ИЗ ПАМЯТИ (bytes)
    await message.answer_document(
        document=file_content,  # ✅ bytes, а не URL!
        caption=f"🛡 <b>Блок безопасности №{block_number}</b>\n\n"
                f"📄 {file_info['name']}\n"
                f"📏 {size_str}\n\n"
                f"💡 <i>Сохраните!</i>",
        parse_mode="HTML"
    )
    
    logger.info(f"📤 Блок {block_number} отправлен {username}")

# ============================================================
# ОБРАБОТКА СООБЩЕНИЙ В ГРУППЕ (ОБЩИЙ ОБРАБОТЧИК)
# ============================================================

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def group_message_handler(message: types.Message):
    """Обработка сообщений в группе"""
    
    if message.from_user.is_bot:
        return
    
    if message.chat.id != GROUP_ID:
        return
    
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text
    
    logger.info(f"💬 Сообщение в группе от {username} ({user_id}): {text[:50] if text else 'медиа'}")
    
    if text and text.startswith('/профиль'):
        await handle_group_profile(message, user_id)
        return
    
    if text and (text.startswith('/помощь') or text.startswith('/help')):
        await handle_group_help(message)
        return
    
    if text and text.startswith('/блоки'):
        await group_safety_blocks_list(message)
        return

async def handle_group_profile(message: types.Message, user_id: int):
    """Показать профиль пользователя в группе"""
    from db_manager import db
    
    user = db.get_user(user_id)
    
    if not user:
        await message.answer(
            "❌ Вы ещё не зарегистрированы в боте.\n"
            "Напишите боту в личные сообщения: /start"
        )
        return
    
    fio = user[3] or "Не указано"
    rank = user[4] or "Не указано"
    
    await message.answer(
        f"👤 <b>{fio}</b>\n"
        f"🎖 Звание: {rank}\n\n"
        f"Полный профиль доступен в ЛС бота.",
        parse_mode="HTML"
    )

async def handle_group_help(message: types.Message):
    """Справка по командам в группе"""
    help_text = (
        "🤖 <b>Команды для группы:</b>\n\n"
        "/профиль - Показать ваш профиль\n"
        "/блоки - Список блоков безопасности\n"
        "/помощь - Эта справка\n\n"
        "🔢 <b>Быстрый доступ к блокам:</b>\n"
        "блок 1, блок №1 — показать блок по номеру\n\n"
        "📩 <b>Личные команды</b> (в ЛС бота):\n"
        "/start - Главное меню\n"
        "Мой профиль - Анкета\n"
        "Полезная информация - База знаний"
    )
    
    await message.answer(help_text, parse_mode="HTML")

# ============================================================
# СПИСОК БЛОКОВ БЕЗОПАСНОСТИ
# ============================================================

@router.message(F.text.startswith("/блоки"))
async def group_safety_blocks_list(message: types.Message):
    """Показать список всех блоков из Yandex Disk"""
    
    # Проверяем что клиент инициализирован
    if disk_client is None:
        await message.answer("❌ Модуль Yandex Disk не подключен.")
        return
    
    files = disk_client.list_files()
    
    if not files:
        await message.answer("❌ На диске нет блоков безопасности.")
        return
    
    text = "🛡 <b>Блоки безопасности:</b>\n\n"
    keyboard_buttons = []
    
    def extract_block_number(filename):
        match = re.search(r'(\d+)', filename)
        return int(match.group(1)) if match else 999
    
    sorted_files = sorted(files, key=lambda x: extract_block_number(x['name']))
    
    for file_info in sorted_files:
        match = re.search(r'(\d+)', file_info['name'])
        
        if match:
            block_number = match.group(1)
            file_size = file_info['size']
            size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
            
            text += f"<b>Блок {block_number}:</b> {file_info['name']} ({size_str})\n"
            
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"🛡 Блок {block_number}",
                    callback_data=f"group_block_file_{block_number}"
                )
            ])
    
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Закрыть", callback_data="group_close")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# ============================================================
# CALLBACK ОБРАБОТЧИКИ
# ============================================================

@router.callback_query(F.data.startswith("group_block_file_"))
async def group_block_file_callback(callback: types.CallbackQuery):
    """Отправить файл блока из Yandex Disk по кнопке"""
    
    # Проверяем что клиент инициализирован
    if disk_client is None:
        await callback.answer("❌ Ошибка модуля", show_alert=True)
        return
    
    try:
        block_number = int(callback.data.split("_")[-1])
        
        files = disk_client.list_files()
        
        possible_names = [
            f"block_{block_number}.docx",
            f"block_{block_number}.pdf",
            f"block_{block_number}.txt",
            f"blocks_{block_number}.docx",
            f"blocks_{block_number}.pdf",
        ]
        
        file_info = None
        for name in possible_names:
            file_info = next((f for f in files if f['name'].lower() == name.lower()), None)
            if file_info:
                break
        
        if not file_info:
            await callback.answer("❌ Файл не найден", show_alert=True)
            return
        
        # 🔥 СКАЧИВАЕМ ФАЙЛ В ПАМЯТЬ
        file_content = disk_client.download_file(file_info['name'])
        
        if not file_content:
            await callback.answer("❌ Ошибка при скачивании файла", show_alert=True)
            return
        
        # 🔥 ОТПРАВЛЯЕМ ФАЙЛ ИЗ ПАМЯТИ
        await callback.message.answer_document(
            document=file_content,  # ✅ bytes, а не URL!
            caption=f"🛡 <b>Блок безопасности №{block_number}</b>\n\n"
                    f"📄 {file_info['name']}\n\n"
                    f"💡 <i>Сохраните!</i>",
            parse_mode="HTML"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в callback: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)

@router.callback_query(F.data == "group_close")
async def group_close_callback(callback: types.CallbackQuery):
    """Закрыть сообщение со списком блоков"""
    try:
        await callback.message.delete()
        await callback.answer()
    except:
        await callback.answer("Закрыто")

# ============================================================
# ОТВЕТЫ НА УПОМИНАНИЯ БОТА
# ============================================================

@router.message(F.mention)
async def bot_mention_handler(message: types.Message):
    """Ответ на упоминание бота"""
    
    if message.chat.id != GROUP_ID:
        return
    
    await message.answer(
        "👋 Я здесь! Напишите /помощь для списка команд."
    )

# ============================================================
# ПРИВЕТСТВИЕ НОВЫХ УЧАСТНИКОВ
# ============================================================

@router.my_chat_member()
async def bot_chat_member_handler(message: types.ChatMemberUpdated):
    """Обработка изменения статуса бота в чате"""
    
    new_status = message.new_chat_member.status
    
    if new_status == 'member':
        logger.info(f"➕ Бот добавлен в чат {message.chat.title}")
    elif new_status == 'administrator':
        logger.info(f"⭐ Бот стал администратором в {message.chat.title}")
    elif new_status == 'left':
        logger.info(f"➖ Бот покинул чат {message.chat.title}")
