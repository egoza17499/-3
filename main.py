import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, GROUP_ID, TOPIC_ID, MAIN_ADMIN_ID, ADMIN_IDS, DB_NAME
from database import Database
from validators import is_valid_date, check_parameter_status, generate_profile_text, check_flight_ban, is_exempt

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database(DB_NAME)

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
        [InlineKeyboardButton(text="✈️ Заполнить базу аэродромов", callback_data="admin_fill_airports")],
        [InlineKeyboardButton(text="👥 Управление админами", callback_data="admin_manage")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_profile_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_edit_profile_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="ФИО", callback_data="edit_fio")],
        [InlineKeyboardButton(text="Звание", callback_data="edit_rank")],
        [InlineKeyboardButton(text="Квалификация", callback_data="edit_qualification")],
        [InlineKeyboardButton(text="Даты отпуска", callback_data="edit_leave")],
        [InlineKeyboardButton(text="ВЛК", callback_data="edit_vlk")],
        [InlineKeyboardButton(text="УМО", callback_data="edit_umo")],
        [InlineKeyboardButton(text="КБП-4 МД-М", callback_data="edit_ex4_md_m")],
        [InlineKeyboardButton(text="КБП-7 МД-М", callback_data="edit_ex7_md_m")],
        [InlineKeyboardButton(text="КБП-4 МД-90А", callback_data="edit_ex4_md_90a")],
        [InlineKeyboardButton(text="КБП-7 МД-90А", callback_data="edit_ex7_md_90a")],
        [InlineKeyboardButton(text="Прыжки", callback_data="edit_parachute")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    is_admin = user_id in ADMIN_IDS or db.check_admin_status(user_id)
    
    # Добавляем пользователя в БД
    db.add_user(user_id, message.from_user.username)
    
    # Проверяем регистрацию
    user = db.get_user(user_id)
    
    if user and user[15]:  # registration_complete
        await message.answer(
            f"С возвращением, {message.from_user.full_name}!",
            reply_markup=get_main_keyboard(is_admin)
        )
    else:
        await message.answer(
            "Добро пожаловать! Для доступа к функциям необходимо пройти регистрацию.\n\n"
            "Начнём регистрацию?"
        )
        await state.set_state(RegistrationState.fio)
        await message.answer("1️⃣ Введите вашу Фамилию Имя Отчество:")

# Регистрация
@dp.message(RegistrationState.fio)
async def reg_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(RegistrationState.rank)
    await message.answer("2️⃣ Введите воинское звание:")

@dp.message(RegistrationState.rank)
async def reg_rank(message: types.Message, state: FSMContext):
    await state.update_data(rank=message.text)
    await state.set_state(RegistrationState.qualification)
    await message.answer("3️⃣ Введите квалификацию:")

@dp.message(RegistrationState.qualification)
async def reg_qual(message: types.Message, state: FSMContext):
    await state.update_data(qualification=message.text)
    await state.set_state(RegistrationState.leave_dates)
    await message.answer("4️⃣ Введите даты отпуска (формат: ДД.ММ.ГГГГ - ДД.ММ.ГГГГ):")

@dp.message(RegistrationState.leave_dates)
async def reg_leave(message: types.Message, state: FSMContext):
    if '-' not in message.text:
        await message.answer("❌ Неверный формат! Используйте: ДД.ММ.ГГГГ - ДД.ММ.ГГГГ")
        return
    
    parts = message.text.split('-')
    if len(parts) != 2:
        await message.answer("❌ Ошибка! Введите две даты через дефис")
        return
    
    await state.update_data(
        leave_start_date=parts[0].strip(),
        leave_end_date=parts[1].strip()
    )
    await state.set_state(RegistrationState.vlk_date)
    await message.answer("5️⃣ Введите дату ВЛК (ДД.ММ.ГГГГ):")

@dp.message(RegistrationState.vlk_date)
async def reg_vlk(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат! Используйте: ДД.ММ.ГГГГ")
        return
    
    await state.update_data(vlk_date=message.text)
    await state.set_state(RegistrationState.umo_date)
    await message.answer("6️⃣ Введите дату УМО (ДД.ММ.ГГГГ) или 'нет':")

@dp.message(RegistrationState.umo_date)
async def reg_umo(message: types.Message, state: FSMContext):
    umo = message.text if message.text.lower() != 'нет' else None
    await state.update_data(umo_date=umo)
    await state.set_state(RegistrationState.exercise_4_md_m)
    await message.answer("7️⃣ Упражнение 4 программы 3 КБП (на самолете Ил-76 МД-М) (ДД.ММ.ГГГГ):")

@dp.message(RegistrationState.exercise_4_md_m)
async def reg_ex4_md_m(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    await state.update_data(exercise_4_md_m_date=message.text)
    await state.set_state(RegistrationState.exercise_7_md_m)
    await message.answer("8️⃣ Упражнение 7 программы 3 КБП (на самолете Ил-76 МД-М) (ДД.ММ.ГГГГ):")

@dp.message(RegistrationState.exercise_7_md_m)
async def reg_ex7_md_m(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    await state.update_data(exercise_7_md_m_date=message.text)
    await state.set_state(RegistrationState.exercise_4_md_90a)
    await message.answer("9️⃣ Упражнение 4 программы 3 КБП (на самолете Ил-76 МД-90А) (ДД.ММ.ГГГГ):")

@dp.message(RegistrationState.exercise_4_md_90a)
async def reg_ex4_md_90a(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    await state.update_data(exercise_4_md_90a_date=message.text)
    await state.set_state(RegistrationState.exercise_7_md_90a)
    await message.answer("🔟 Упражнение 7 программы 3 КБП (на самолете Ил-76 МД-90А) (ДД.ММ.ГГГГ):")

@dp.message(RegistrationState.exercise_7_md_90a)
async def reg_ex7_md_90a(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    await state.update_data(exercise_7_md_90a_date=message.text)
    await state.set_state(RegistrationState.parachute_jump)
    await message.answer("1️⃣1️⃣ Дата прыжков с парашютом (ДД.ММ.ГГГГ) или 'освобожден':")

@dp.message(RegistrationState.parachute_jump)
async def reg_finish(message: types.Message, state: FSMContext):
    # Проверяем на "освобожден"
    if message.text.lower() in ['освобожден', 'освобождён', 'осв']:
        parachute = 'освобожден'
    elif not is_valid_date(message.text):
        await message.answer("❌ Неверный формат! Используйте: ДД.ММ.ГГГГ или 'освобожден'")
        return
    else:
        parachute = message.text
    
    # Получаем все данные
    data = await state.get_data()
    data['parachute_jump_date'] = parachute
    
    # Сохраняем в БД
    chat_id = message.from_user.id
    db.update_user(chat_id, **data)
    db.set_registration_complete(chat_id)
    
    await state.clear()
    
    is_admin = chat_id in ADMIN_IDS or db.check_admin_status(chat_id)
    
    # Показываем профиль
    user = db.get_user(chat_id)
    profile_text = generate_profile_text(user)
    
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    
    await message.answer(
        "✅ Регистрация завершена!\n\n" + profile_text,
        reply_markup=get_main_keyboard(is_admin)
    )

# Кнопки главного меню
@dp.message(lambda msg: msg.text == "👤 Мой профиль")
async def show_profile(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала пройдите регистрацию (/start)")
        return
    
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@dp.message(lambda msg: msg.text == "📚 Полезная информация")
async def show_info(message: types.Message):
    await message.answer(
        "📚 Полезная информация\n\n"
        "Введите название аэродрома или города для поиска контактной информации."
    )

@dp.message(lambda msg: msg.text == "🛡 Административные функции")
async def admin_functions(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS and not db.check_admin_status(user_id):
        await message.answer("❌ У вас нет доступа")
        return
    
    await message.answer(
        "🛡 Административные функции",
        reply_markup=get_admin_keyboard()
    )

# Callback handlers
@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    is_admin = callback.from_user.id in ADMIN_IDS or db.check_admin_status(callback.from_user.id)
    await callback.message.edit_text(
        "Главное меню",
        reply_markup=get_main_keyboard(is_admin)
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_profile")
async def back_to_profile(callback: types.CallbackQuery):
    await show_profile(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "edit_profile")
async def edit_profile(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "✏️ Редактирование профиля\n\nВыберите поле:",
        reply_markup=get_edit_profile_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    is_admin = callback.from_user.id in ADMIN_IDS or db.check_admin_status(callback.from_user.id)
    await callback.message.edit_text(
        "Главное меню",
        reply_markup=get_main_keyboard(is_admin)
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_list")
async def admin_list(callback: types.CallbackQuery):
    users = db.get_all_users()
    if not users:
        await callback.message.edit_text("📋 Список пуст")
        await callback.answer()
        return
    
    text = "📋 Список пользователей:\n\n"
    for user in users:
        fio = user[3] or "Не указано"
        rank = user[4] or "Не указано"
        text += f"• {fio} ({rank})\n"
    
    await callback.message.edit_text(text)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    users = db.get_all_users()
    total = len(users)
    
    # Считаем кто может летать
    can_fly = 0
    for user in users:
        bans = check_flight_ban(user)
        if not bans:
            can_fly += 1
    
    text = f"📊 Статистика:\n\n"
    text += f"👥 Всего пользователей: {total}\n"
    text += f"✅ Готовы к полётам: {can_fly}\n"
    text += f"🚫 Не могут летать: {total - can_fly}"
    
    await callback.message.edit_text(text)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_fill_airports")
async def admin_fill_airports(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ Заполняю базу аэродромов...")
    # Здесь будет код заполнения базы
    await callback.message.edit_text("✅ База заполнена!")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_manage")
async def admin_manage(callback: types.CallbackQuery):
    text = "👥 Управление администраторами\n\n"
    text += "Выберите действие:\n"
    text += "➕ Добавить админа\n"
    text += "➖ Удалить админа"
    await callback.message.edit_text(text)
    await callback.answer()

# Поиск аэродромов
@dp.message(lambda msg: msg.text not in ["👤 Мой профиль", "📚 Полезная информация", "🛡 Административные функции"])
async def search_aerodrome(message: types.Message):
    keyword = message.text
    results = db.search_aerodromes(keyword)
    
    if results:
        for result in results:
            await message.answer(result[0])
    else:
        await message.answer("❌ Информация не найдена")

# Запуск бота
async def main():
    logging.info("🚀 Запуск бота...")
    try:
        await asyncio.sleep(2)
        await bot.delete_webhook(drop_pending_updates=True)
        await asyncio.sleep(1)
        logging.info("✅ Запускаем polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logging.error(f"❌ Ошибка запуска: {e}")
    finally:
        logging.info("🛑 Остановка бота...")
        await bot.session.close()
        if db:
            db.close()

if __name__ == "__main__":
    asyncio.run(main())
