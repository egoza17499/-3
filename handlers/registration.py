import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_IDS
from validators import is_valid_date, generate_profile_text, check_flight_ban
from db_manager import db  # <-- Импортируем db из db_manager

logger = logging.getLogger(__name__)
router = Router()

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

def get_main_keyboard(is_admin=False):
    keyboard = [
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="📚 Полезная информация")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="🛡 Административные функции")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):  # <-- БЕЗ db параметра!
    user_id = message.from_user.id
    is_admin = user_id in ADMIN_IDS or db.check_admin_status(user_id)
    db.add_user(user_id, message.from_user.username)
    user = db.get_user(user_id)
    
    if user and user[15]:
        await message.answer(f"С возвращением, {message.from_user.full_name}!", reply_markup=get_main_keyboard(is_admin))
    else:
        await message.answer("Добро пожаловать! Для доступа к функциям необходимо пройти регистрацию.\n\nНачнём регистрацию?")
        await state.set_state(RegistrationState.fio)
        await message.answer("1️⃣ Введите вашу Фамилию Имя Отчество:")

@router.message(RegistrationState.fio)
async def reg_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(RegistrationState.rank)
    await message.answer("2️⃣ Введите воинское звание:")

@router.message(RegistrationState.rank)
async def reg_rank(message: types.Message, state: FSMContext):
    await state.update_data(rank=message.text)
    await state.set_state(RegistrationState.qualification)
    await message.answer("3️⃣ Введите квалификацию:")

@router.message(RegistrationState.qualification)
async def reg_qual(message: types.Message, state: FSMContext):
    await state.update_data(qualification=message.text)
    await state.set_state(RegistrationState.leave_dates)
    await message.answer("4️⃣ Введите даты отпуска (формат: ДД.ММ.ГГГГ - ДД.ММ.ГГГГ):")

@router.message(RegistrationState.leave_dates)
async def reg_leave(message: types.Message, state: FSMContext):
    if '-' not in message.text:
        await message.answer("❌ Неверный формат! Используйте: ДД.ММ.ГГГГ - ДД.ММ.ГГГГ")
        return
    parts = message.text.split('-')
    if len(parts) != 2:
        await message.answer("❌ Ошибка! Введите две даты через дефис")
        return
    await state.update_data(leave_start_date=parts[0].strip(), leave_end_date=parts[1].strip())
    await state.set_state(RegistrationState.vlk_date)
    await message.answer("5️⃣ Введите дату ВЛК (ДД.ММ.ГГГГ):")

@router.message(RegistrationState.vlk_date)
async def reg_vlk(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат! Используйте: ДД.ММ.ГГГГ")
        return
    await state.update_data(vlk_date=message.text)
    await state.set_state(RegistrationState.umo_date)
    await message.answer("6️⃣ Введите дату УМО (ДД.ММ.ГГГГ) или 'нет':")

@router.message(RegistrationState.umo_date)
async def reg_umo(message: types.Message, state: FSMContext):
    umo = message.text if message.text.lower() != 'нет' else None
    await state.update_data(umo_date=umo)
    await state.set_state(RegistrationState.exercise_4_md_m)
    await message.answer("7️⃣ Упражнение 4 программы 3 КБП (на самолете Ил-76 МД-М) (ДД.ММ.ГГГГ):")

@router.message(RegistrationState.exercise_4_md_m)
async def reg_ex4_md_m(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    await state.update_data(exercise_4_md_m_date=message.text)
    await state.set_state(RegistrationState.exercise_7_md_m)
    await message.answer("8️⃣ Упражнение 7 программы 3 КБП (на самолете Ил-76 МД-М) (ДД.ММ.ГГГГ):")

@router.message(RegistrationState.exercise_7_md_m)
async def reg_ex7_md_m(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    await state.update_data(exercise_7_md_m_date=message.text)
    await state.set_state(RegistrationState.exercise_4_md_90a)
    await message.answer("9️⃣ Упражнение 4 программы 3 КБП (на самолете Ил-76 МД-90А) (ДД.ММ.ГГГГ):")

@router.message(RegistrationState.exercise_4_md_90a)
async def reg_ex4_md_90a(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    await state.update_data(exercise_4_md_90a_date=message.text)
    await state.set_state(RegistrationState.exercise_7_md_90a)
    await message.answer("🔟 Упражнение 7 программы 3 КБП (на самолете Ил-76 МД-90А) (ДД.ММ.ГГГГ):")

@router.message(RegistrationState.exercise_7_md_90a)
async def reg_ex7_md_90a(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    await state.update_data(exercise_7_md_90a_date=message.text)
    await state.set_state(RegistrationState.parachute_jump)
    await message.answer("1️⃣1️⃣ Дата прыжков с парашютом (ДД.ММ.ГГГГ) или 'освобожден':")

@router.message(RegistrationState.parachute_jump)
async def reg_finish(message: types.Message, state: FSMContext):
    if message.text.lower() in ['освобожден', 'освобождён', 'осв']:
        parachute = 'освобожден'
    elif not is_valid_date(message.text):
        await message.answer("❌ Неверный формат! Используйте: ДД.ММ.ГГГГ или 'освобожден'")
        return
    else:
        parachute = message.text
    
    data = await state.get_data()
    data['parachute_jump_date'] = parachute
    chat_id = message.from_user.id
    db.update_user(chat_id, **data)
    db.set_registration_complete(chat_id)
    await state.clear()
    
    is_admin = chat_id in ADMIN_IDS or db.check_admin_status(chat_id)
    user = db.get_user(chat_id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    
    await message.answer("✅ Регистрация завершена!\n\n" + profile_text, reply_markup=get_main_keyboard(is_admin))
