import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, GROUP_ID, TOPIC_ID, MAIN_ADMIN_ID, ADMIN_IDS
from database import Database
from validators import is_valid_date, check_parameter_status

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database('bot_database.db')

# Машина состояний для регистрации
class RegistrationState(StatesGroup):
    fio = State()
    rank = State()
    qualification = State()
    leave_dates = State()
    vlk_date = State()
    umo_date = State()
    exercise_4_md_m = State()
    exercise_7_md_m = State()
    exercise_4_md_90a = State()
    exercise_7_md_90a = State()
    parachute_jump = State()

# Клавиатуры
def get_main_keyboard(is_admin=False):
    keyboard = [
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="📚 Полезная информация")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="🛡 Административные функции")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_list")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_manage")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_profile_edit_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    is_admin = user_id in ADMIN_IDS or db.check_admin_status(user_id)
    
    # Проверяем, зарегистрирован ли пользователь
    # Здесь должна быть логика проверки регистрации
    # Для простоты пока просто показываем меню
    
    await message.answer(
        f"👋 Добро пожаловать, {message.from_user.full_name}!",
        reply_markup=get_main_keyboard(is_admin)
    )

# Обработка кнопки "Мой профиль"
@dp.message(lambda msg: msg.text == "👤 Мой профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    # Здесь будет логика получения данных из БД
    await message.answer("📋 Ваш профиль:\n\nЗдесь будет информация о пользователе")

# Обработка кнопки "Полезная информация"
@dp.message(lambda msg: msg.text == "📚 Полезная информация")
async def show_info(message: types.Message):
    await message.answer(
        "📚 **Полезная информация**\n\n"
        "Введите название аэродрома или города для поиска контактной информации."
    )

# Обработка кнопки "Административные функции"
@dp.message(lambda msg: msg.text == "🛡 Административные функции")
async def admin_functions(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS and not db.check_admin_status(user_id):
        await message.answer("❌ У вас нет доступа к административным функциям")
        return
    
    await message.answer(
        "🛡 **Административные функции**",
        reply_markup=get_admin_keyboard()
    )

# Callback handlers
@dp.callback_query(lambda c: c.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    is_admin = callback.from_user.id in ADMIN_IDS
    await callback.message.edit_text(
        "Главное меню",
        reply_markup=get_main_keyboard(is_admin)
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_list")
async def admin_list(callback: types.CallbackQuery):
    users = db.get_all_users()
    text = "📋 **Список пользователей:**\n\n"
    for user in users:
        text += f"• {user[2]} {user[3]} {user[4]}\n"  # last_name, first_name, patronymic
    await callback.message.edit_text(text)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    users = db.get_all_users()
    total = len(users)
    text = f"📊 **Статистика:**\n\n"
    text += f"Всего пользователей: {total}\n"
    # Здесь можно добавить дополнительную статистику
    await callback.message.edit_text(text)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_manage")
async def admin_manage(callback: types.CallbackQuery):
    text = "👥 **Управление администраторами**\n\n"
    text += "Выберите действие:\n"
    text += "➕ Добавить админа\n"
    text += "➖ Удалить админа"
    await callback.message.edit_text(text)
    await callback.answer()

# Запуск бота
async def main():
    logging.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
