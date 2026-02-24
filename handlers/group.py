import logging
import re
from aiogram import Router, F, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import GROUP_ID
from utils.admin_check import is_admin

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# ОБРАБОТКА СООБЩЕНИЙ В ГРУППЕ
# ============================================================

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def group_message_handler(message: types.Message):
    """Обработка сообщений в группе"""
    
    # Игнорируем сообщения от ботов
    if message.from_user.is_bot:
        return
    
    # Проверяем что это наша группа
    if message.chat.id != GROUP_ID:
        return
    
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text
    
    logger.info(f"💬 Сообщение в группе от {username} ({user_id}): {text[:50] if text else 'медиа'}")
    
    # Команда /профиль в группе
    if text and text.startswith('/профиль'):
        await handle_group_profile(message, user_id)
        return
    
    # Команда /помощь в группе
    if text and (text.startswith('/помощь') or text.startswith('/help')):
        await handle_group_help(message)
        return
    
    # Команда /блоки в группе
    if text and text.startswith('/блоки'):
        await group_safety_blocks_list(message)
        return
    
   # ============================================================
# БЛОКИ БЕЗОПАСНОСТИ ИЗ YANDEX DISK (ОТДЕЛЬНЫЙ ОБРАБОТЧИК)
# ============================================================

@router.message(
    F.chat.type.in_({"group", "supergroup"}),
    F.text.regexp(re.compile(r'^(блок\s*№?\s*\d+)$', re.IGNORECASE))
)
async def group_safety_block_from_disk(message: types.Message):
    """Показать блок безопасности из Yandex Disk"""
    
    if message.chat.id != GROUP_ID:
        return
    
    try:
        from utils.yandex_disk_client import disk_client
    except ImportError:
        logger.error("❌ Модуль Yandex Disk не подключен!")
        return
    
    # Извлекаем номер блока
    text = message.text.lower()
    match = re.search(r'(\d+)', text)
    
    if not match:
        return
    
    block_number = int(match.group(1))
    logger.info(f"🔍 Запрос блока {block_number} от {message.from_user.username}")
    
    # Ищем файл на Yandex Disk
    files = disk_client.list_files()
    
    # Пробуем разные форматы и названия
    possible_names = [
        f"block_{block_number}.docx",
        f"block_{block_number}.pdf",
        f"block_{block_number}.txt",
        f"блок_{block_number}.docx",
        f"блок_{block_number}.pdf",
        f"блок_{block_number}.txt",
        f"Блок_{block_number}.docx",
        f"Блок_{block_number}.pdf",
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
    
    # Получаем ссылку
    download_link = disk_client.get_file_link(file_info['name'])
    
    if not download_link:
        await message.answer("❌ Ошибка при получении файла.")
        return
    
    # Отправляем файл
    file_size = file_info['size']
    size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
    
    await message.answer_document(
        document=download_link,
        caption=f"🛡 <b>Блок безопасности №{block_number}</b>\n\n"
                f"📄 {file_info['name']}\n"
                f"📏 {size_str}\n\n"
                f"💡 <i>Сохраните!</i>",
        parse_mode="HTML"
    )
    
    logger.info(f"📤 Блок {block_number} отправлен {message.from_user.username}")

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
        "блок 1, блок №1, № 1 — показать блок по номеру\n\n"
        "📩 <b>Личные команды</b> (в ЛС бота):\n"
        "/start - Главное меню\n"
        "Мой профиль - Анкета\n"
        "Полезная информация - База знаний"
    )
    
    await message.answer(help_text, parse_mode="HTML")

# ============================================================
# БЛОКИ БЕЗОПАСНОСТИ ИЗ YANDEX DISK
# ============================================================

@router.message(
    F.chat.type.in_({"group", "supergroup"}),
    F.text.regexp(re.compile(r'^(блок\s*№?\s*\d+|№\s*\d+)$', re.IGNORECASE)) 
)
async def group_safety_block_from_disk(message: types.Message):
    """Показать блок безопасности из Yandex Disk"""
    
    if message.chat.id != GROUP_ID:
        return
    
    try:
        from utils.yandex_disk_client import disk_client
    except ImportError:
        await message.answer("❌ Модуль Yandex Disk не подключен. Обратитесь к администратору.")
        return
    
    # Извлекаем номер блока из текста
    text = message.text.lower()
    match = re.search(r'(\d+)', text)
    
    if not match:
        return
    
    block_number = int(match.group(1))
    
    # Ищем файл на Yandex Disk
    files = disk_client.list_files()
    
    # Пробуем разные форматы и названия файлов
    possible_names = [
        f"block_{block_number}.docx",
        f"block_{block_number}.pdf",
        f"block_{block_number}.txt",
        f"блок_{block_number}.docx",
        f"блок_{block_number}.pdf",
        f"блок_{block_number}.txt",
        f"Блок_{block_number}.docx",
        f"Блок_{block_number}.pdf",
        f"Блок безопасности {block_number}.docx",
        f"Блок безопасности {block_number}.pdf",
    ]
    
    file_info = None
    for name in possible_names:
        file_info = next((f for f in files if f['name'].lower() == name.lower()), None)
        if file_info:
            break
    
    if not file_info:
        await message.answer(
            f"❌ <b>Блок №{block_number} не найден!</b>\n\n"
            "Используйте /блоки для просмотра списка доступных блоков.",
            parse_mode="HTML"
        )
        return
    
    # Получаем ссылку для скачивания
    download_link = disk_client.get_file_link(file_info['name'])
    
    if not download_link:
        await message.answer("❌ Ошибка при получении файла. Попробуйте позже.")
        return
    
    # Форматируем размер файла
    file_size = file_info['size']
    if file_size < 1024:
        size_str = f"{file_size} B"
    elif file_size < 1024 * 1024:
        size_str = f"{file_size / 1024:.1f} KB"
    else:
        size_str = f"{file_size / (1024 * 1024):.1f} MB"
    
    # Отправляем файл
    await message.answer_document(
        document=download_link,
        caption=f"🛡 <b>Блок безопасности №{block_number}</b>\n\n"
                f"📄 Файл: {file_info['name']}\n"
                f"📏 Размер: {size_str}\n\n"
                f"💡 <i>Сохраните файл в избранное!</i>",
        parse_mode="HTML"
    )
    
    logger.info(f"📤 Блок {block_number} отправлен пользователю {username} ({user_id})")

@router.message(F.chat.type.in_({"group", "supergroup"}), F.text.startswith("/блоки"))
async def group_safety_blocks_list(message: types.Message):
    """Показать список всех блоков из Yandex Disk"""
    
    if message.chat.id != GROUP_ID:
        return
    
    try:
        from utils.yandex_disk_client import disk_client
    except ImportError:
        await message.answer("❌ Модуль Yandex Disk не подключен.")
        return
    
    files = disk_client.list_files()
    
    if not files:
        await message.answer(
            "❌ На диске нет блоков безопасности.\n\n"
            "Обратитесь к администратору для добавления блоков."
        )
        return
    
    text = "🛡 <b>Блоки безопасности:</b>\n\n"
    keyboard_buttons = []
    
    # Сортируем файлы по номеру блока
    def extract_block_number(filename):
        match = re.search(r'(\d+)', filename)
        return int(match.group(1)) if match else 999
    
    sorted_files = sorted(files, key=lambda x: extract_block_number(x['name']))
    
    for file_info in sorted_files:
        # Извлекаем номер из имени файла
        match = re.search(r'(\d+)', file_info['name'])
        
        if match:
            block_number = match.group(1)
            
            # Форматируем размер
            file_size = file_info['size']
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            text += f"<b>Блок {block_number}:</b> {file_info['name']} ({size_str})\n"
            
            # Добавляем кнопку
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"🛡 Блок {block_number}",
                    callback_data=f"group_block_file_{block_number}"
                )
            ])
    
    # Кнопка закрытия
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Закрыть", callback_data="group_close")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# ============================================================
# CALLBACK ОБРАБОТЧИКИ ДЛЯ КНОПОК
# ============================================================

@router.callback_query(F.data.startswith("group_block_file_"))
async def group_block_file_callback(callback: types.CallbackQuery):
    """Отправить файл блока из Yandex Disk по нажатию кнопки"""
    
    try:
        from utils.yandex_disk_client import disk_client
    except ImportError:
        await callback.answer("❌ Ошибка модуля", show_alert=True)
        return
    
    try:
        block_number = int(callback.data.split("_")[-1])
        
        # Ищем файл
        files = disk_client.list_files()
        
        possible_names = [
            f"block_{block_number}.docx",
            f"block_{block_number}.pdf",
            f"block_{block_number}.txt",
            f"блок_{block_number}.docx",
            f"блок_{block_number}.pdf",
        ]
        
        file_info = None
        for name in possible_names:
            file_info = next((f for f in files if f['name'].lower() == name.lower()), None)
            if file_info:
                break
        
        if not file_info:
            await callback.answer("❌ Файл не найден", show_alert=True)
            return
        
        # Получаем ссылку
        download_link = disk_client.get_file_link(file_info['name'])
        
        if not download_link:
            await callback.answer("❌ Ошибка получения ссылки", show_alert=True)
            return
        
        # Отправляем файл
        await callback.message.answer_document(
            document=download_link,
            caption=f"🛡 <b>Блок безопасности №{block_number}</b>\n\n"
                    f"📄 {file_info['name']}\n\n"
                    f"💡 <i>Сохраните файл!</i>",
            parse_mode="HTML"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в group_block_file_callback: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)

@router.callback_query(F.data == "group_close")
async def group_close_callback(callback: types.CallbackQuery):
    """Закрыть сообщение со списком блоков"""
    try:
        await callback.message.delete()
        await callback.answer()
    except:
        # Если не удалось удалить, просто отвечаем
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
        "👋 Я здесь! Напишите /помощь для списка команд.\n"
        "Или обратитесь ко мне в личные сообщения."
    )

# ============================================================
# ПРИВЕТСТВИЕ НОВЫХ УЧАСТНИКОВ
# ============================================================

@router.my_chat_member()
async def bot_chat_member_handler(message: types.ChatMemberUpdated):
    """Обработка изменения статуса бота в чате"""
    
    old_status = message.old_chat_member.status
    new_status = message.new_chat_member.status
    
    if new_status == 'member':
        logger.info(f"➕ Бот добавлен в чат {message.chat.title} (ID: {message.chat.id})")
    elif new_status == 'administrator':
        logger.info(f"⭐ Бот стал администратором в {message.chat.title}")
    elif new_status == 'left':
        logger.info(f"➖ Бот покинул чат {message.chat.title}")

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

async def is_bot_admin(chat_id: int) -> bool:
    """Проверить является ли бот администратором в чате"""
    from main import bot
    
    try:
        member = await bot.get_chat_member(chat_id, bot.id)
        return member.is_chat_admin()
    except:
        return False
