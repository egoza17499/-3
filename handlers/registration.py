# handlers/registration.py
# Регистрация пользователя — шаг за шагом через FSM
# Данные сохраняются в таблицу users в Neon PostgreSQL

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from states import RegistrationState
from db_manager import db, get_user, add_user, update_user, set_registration_complete
from validators import is_valid_date

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# РАНГИ И КВАЛИФИКАЦИИ (клавиатуры для выбора)
# ============================================================

RANKS = [
    "Рядовой", "Ефрейтор", "Младший сержант", "Сержант",
    "Старший сержант", "Старшина", "Прапорщик", "Старший прапорщик",
    "Младший лейтенант", "Лейтенант", "Старший лейтенант", "Капитан",
    "Майор", "Подполковник", "Полковник",
    "Генерал-майор", "Генерал-лейтенант", "Генерал-полковник"
]

QUALIFICATIONS = [
    "Лётчик 3-го класса",
    "Лётчик 2-го класса",
    "Лётчик 1-го класса",
    "Военный лётчик-снайпер",
]

DATE_FIELDS = [
    ("leave_start_date",    "📅 Введи дату НАЧАЛА последнего отпуска (формат: дд.мм.гггг):\n\nНапример: 15.06.2024"),
    ("leave_end_date",      "📅 Введи дату ОКОНЧАНИЯ последнего отпуска (формат: дд.мм.гггг):\n\nНапример: 15.07.2024"),
    ("vlk_date",            "🏥 Введи дату прохождения ВЛК (врачебно-лётная комиссия, формат: дд.мм.гггг):\n\nНапример: 10.01.2024"),
    ("umo_date",            "🔬 Введи дату УМО (углублённое медицинское обследование, формат: дд.мм.гггг)\n\nЕсли не проходил — напиши <b>нет</b>"),
    ("exercise_4_md_m_date",  "✈️ Введи дату выполнения <b>КБП-4 на Ил-76 МД-М</b> (формат: дд.мм.гггг)\n\nЕсли не выполнял — напиши <b>нет</b>"),
    ("exercise_7_md_m_date",  "✈️ Введи дату выполнения <b>КБП-7 на Ил-76 МД-М</b> (формат: дд.мм.гггг)\n\nЕсли не выполнял — напиши <b>нет</b>"),
    ("exercise_4_md_90a_date","✈️ Введи дату выполнения <b>КБП-4 на Ил-76 МД-90А</b> (формат: дд.мм.гггг)\n\nЕсли не выполнял — напиши <b>нет</b>"),
    ("exercise_7_md_90a_date","✈️ Введи дату выполнения <b>КБП-7 на Ил-76 МД-90А</b> (формат: дд.мм.гггг)\n\nЕсли не выполнял — напиши <b>нет</b>"),
    ("parachute_jump_date", "🪂 Введи дату последнего прыжка с парашютом (формат: дд.мм.гггг)\n\nЕсли освобождён — напиши <b>освобожден</b>"),
]

# Поля, которые могут быть "нет"/"освобожден"
NULLABLE_DATE_FIELDS = {
    "umo_date", "exercise_4_md_m_date", "exercise_7_md_m_date",
    "exercise_4_md_90a_date", "exercise_7_md_90a_date", "parachute_jump_date"
}

FREED_WORDS = ['нет', 'освобожден', 'освобождён', 'осв', 'освобождение', 'не требуется']


def make_rank_keyboard():
    buttons = [[KeyboardButton(text=r)] for r in RANKS]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def make_qualification_keyboard():
    buttons = [[KeyboardButton(text=q)] for q in QUALIFICATIONS]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def make_skip_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="нет")]],
        resize_keyboard=True, one_time_keyboard=True
    )


# ============================================================
# СТАРТ РЕГИСТРАЦИИ
# ============================================================

@router.callback_query(F.data == "start_registration")
async def start_registration_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username or ""

    # Добавляем пользователя в БД если не существует
    add_user(user_id, username)

    await state.set_state(RegistrationState.fio)
    await callback.message.answer(
        "📝 <b>Начинаем регистрацию!</b>\n\n"
        "Шаг 1 из 12\n\n"
        "Введи своё <b>ФИО</b> полностью:\n"
        "<i>Например: Иванов Иван Иванович</i>",
        reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()


@router.message(F.text == "📝 Регистрация")
async def start_registration_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or ""

    # Проверяем — не зарегистрирован ли уже
    user = get_user(user_id)
    if user and user.get('is_registered'):
        await message.answer(
            "✅ Ты уже зарегистрирован!\n\n"
            "Используй меню для навигации.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    add_user(user_id, username)
    await state.set_state(RegistrationState.fio)
    await message.answer(
        "📝 <b>Начинаем регистрацию!</b>\n\n"
        "Шаг 1 из 12\n\n"
        "Введи своё <b>ФИО</b> полностью:\n"
        "<i>Например: Иванов Иван Иванович</i>",
        reply_markup=ReplyKeyboardRemove()
    )


# ============================================================
# ШАГ 1: ФИО
# ============================================================

@router.message(RegistrationState.fio)
async def process_fio(message: Message, state: FSMContext):
    fio = message.text.strip()
    if len(fio) < 3:
        await message.answer("❌ Введи полное ФИО (минимум 3 символа):")
        return

    await state.update_data(fio=fio)
    await state.set_state(RegistrationState.rank)
    await message.answer(
        f"✅ ФИО: <b>{fio}</b>\n\n"
        "Шаг 2 из 12\n\n"
        "Выбери своё <b>воинское звание</b>:",
        reply_markup=make_rank_keyboard()
    )


# ============================================================
# ШАГ 2: ЗВАНИЕ
# ============================================================

@router.message(RegistrationState.rank)
async def process_rank(message: Message, state: FSMContext):
    rank = message.text.strip()
    if rank not in RANKS:
        await message.answer(
            "❌ Выбери звание из списка на клавиатуре:",
            reply_markup=make_rank_keyboard()
        )
        return

    await state.update_data(rank=rank)
    await state.set_state(RegistrationState.qualification)
    await message.answer(
        f"✅ Звание: <b>{rank}</b>\n\n"
        "Шаг 3 из 12\n\n"
        "Выбери свою <b>классную квалификацию</b>:",
        reply_markup=make_qualification_keyboard()
    )


# ============================================================
# ШАГ 3: КВАЛИФИКАЦИЯ
# ============================================================

@router.message(RegistrationState.qualification)
async def process_qualification(message: Message, state: FSMContext):
    qualification = message.text.strip()
    if qualification not in QUALIFICATIONS:
        await message.answer(
            "❌ Выбери квалификацию из списка на клавиатуре:",
            reply_markup=make_qualification_keyboard()
        )
        return

    await state.update_data(qualification=qualification)

    # Переходим к датам
    await state.update_data(date_step=0)
    await state.set_state(RegistrationState.dates)

    field_key, prompt = DATE_FIELDS[0]
    skip_kb = make_skip_keyboard() if field_key in NULLABLE_DATE_FIELDS else ReplyKeyboardRemove()

    await message.answer(
        f"✅ Квалификация: <b>{qualification}</b>\n\n"
        f"Шаг 4 из 12\n\n{prompt}",
        reply_markup=skip_kb
    )


# ============================================================
# ШАГИ 4-12: ДАТЫ
# ============================================================

@router.message(RegistrationState.dates)
async def process_dates(message: Message, state: FSMContext):
    data = await state.get_data()
    step = data.get('date_step', 0)
    field_key, prompt = DATE_FIELDS[step]
    value = message.text.strip()

    # Проверка значения
    if field_key in NULLABLE_DATE_FIELDS and value.lower() in FREED_WORDS:
        # Разрешено пропустить
        save_value = value.lower()
    else:
        if not is_valid_date(value):
            skip_hint = "\n\nИли напиши <b>нет</b> чтобы пропустить." if field_key in NULLABLE_DATE_FIELDS else ""
            await message.answer(
                f"❌ Неверный формат даты. Введи в формате <b>дд.мм.гггг</b>{skip_hint}\n\n"
                f"Например: <b>15.06.2024</b>"
            )
            return
        save_value = value

    await state.update_data(**{field_key: save_value})

    next_step = step + 1

    if next_step < len(DATE_FIELDS):
        await state.update_data(date_step=next_step)
        next_field_key, next_prompt = DATE_FIELDS[next_step]
        skip_kb = make_skip_keyboard() if next_field_key in NULLABLE_DATE_FIELDS else ReplyKeyboardRemove()

        await message.answer(
            f"✅ Сохранено!\n\n"
            f"Шаг {next_step + 4} из 12\n\n{next_prompt}",
            reply_markup=skip_kb
        )
    else:
        # Все поля заполнены — сохраняем в БД
        await finish_registration(message, state)


async def finish_registration(message: Message, state: FSMContext):
    """Сохранить все данные в БД и завершить регистрацию."""
    data = await state.get_data()
    user_id = message.from_user.id

    try:
        update_user(
            user_id,
            fio=data.get('fio'),
            rank=data.get('rank'),
            qualification=data.get('qualification'),
            leave_start_date=data.get('leave_start_date'),
            leave_end_date=data.get('leave_end_date'),
            vlk_date=data.get('vlk_date'),
            umo_date=data.get('umo_date'),
            exercise_4_md_m_date=data.get('exercise_4_md_m_date'),
            exercise_7_md_m_date=data.get('exercise_7_md_m_date'),
            exercise_4_md_90a_date=data.get('exercise_4_md_90a_date'),
            exercise_7_md_90a_date=data.get('exercise_7_md_90a_date'),
            parachute_jump_date=data.get('parachute_jump_date'),
        )
        set_registration_complete(user_id)

        await state.clear()
        await message.answer(
            "🎉 <b>Регистрация завершена!</b>\n\n"
            f"👤 ФИО: {data.get('fio')}\n"
            f"🎖 Звание: {data.get('rank')}\n"
            f"🏅 Квалификация: {data.get('qualification')}\n\n"
            "Данные сохранены. Используй /menu для перехода в главное меню.",
            reply_markup=ReplyKeyboardRemove()
        )
        logger.info(f"✅ Пользователь {user_id} завершил регистрацию: {data.get('fio')}")

    except Exception as e:
        logger.error(f"❌ Ошибка сохранения регистрации для {user_id}: {e}")
        await state.clear()
        await message.answer(
            "❌ Произошла ошибка при сохранении данных. Попробуй снова — /start",
            reply_markup=ReplyKeyboardRemove()
        )


# ============================================================
# ОТМЕНА РЕГИСТРАЦИИ
# ============================================================

@router.message(F.text == "/cancel", StateFilter(RegistrationState))
async def cancel_registration(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Регистрация отменена.\n\nДля начала снова используй /start",
        reply_markup=ReplyKeyboardRemove()
    )
