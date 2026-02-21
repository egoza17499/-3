import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from validators import generate_profile_text, check_flight_ban
from db_manager import db
from config import ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()

class EditProfileState(StatesGroup):
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

def get_profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])

def get_edit_profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
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
    ])

@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    from handlers.menu import get_main_keyboard
    is_admin = callback.from_user.id in ADMIN_IDS or db.check_admin_status(callback.from_user.id)
    await callback.message.edit_text("Главное меню", reply_markup=get_main_keyboard(is_admin))
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_to_profile")
async def back_to_profile(callback: types.CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if not user:
        await callback.message.edit_text("❌ Сначала пройдите регистрацию (/start)")
        await callback.answer()
        return
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await callback.message.edit_text(profile_text, reply_markup=get_profile_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "edit_profile")
async def edit_profile(callback: types.CallbackQuery):
    await callback.message.edit_text("✏️ Редактирование профиля\n\nВыберите поле:", reply_markup=get_edit_profile_keyboard())
    await callback.answer()

# Обработчики для каждого поля
@router.callback_query(lambda c: c.data == "edit_fio")
async def edit_fio_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите новое ФИО:")
    await state.set_state(EditProfileState.fio)
    await callback.answer()

@router.message(EditProfileState.fio)
async def edit_fio_save(message: types.Message, state: FSMContext):
    db.update_user(message.from_user.id, fio=message.text)
    await message.answer("✅ ФИО обновлено!")
    await state.clear()
    # Показываем профиль снова
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(lambda c: c.data == "edit_rank")
async def edit_rank_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите новое звание:")
    await state.set_state(EditProfileState.rank)
    await callback.answer()

@router.message(EditProfileState.rank)
async def edit_rank_save(message: types.Message, state: FSMContext):
    db.update_user(message.from_user.id, rank=message.text)
    await message.answer("✅ Звание обновлено!")
    await state.clear()
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(lambda c: c.data == "edit_qualification")
async def edit_qual_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите новую квалификацию:")
    await state.set_state(EditProfileState.qualification)
    await callback.answer()

@router.message(EditProfileState.qualification)
async def edit_qual_save(message: types.Message, state: FSMContext):
    db.update_user(message.from_user.id, qualification=message.text)
    await message.answer("✅ Квалификация обновлена!")
    await state.clear()
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(lambda c: c.data == "edit_leave")
async def edit_leave_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите даты отпуска (формат: ДД.ММ.ГГГГ - ДД.ММ.ГГГГ):")
    await state.set_state(EditProfileState.leave_dates)
    await callback.answer()

@router.message(EditProfileState.leave_dates)
async def edit_leave_save(message: types.Message, state: FSMContext):
    if '-' not in message.text:
        await message.answer("❌ Неверный формат! Используйте: ДД.ММ.ГГГГ - ДД.ММ.ГГГГ")
        return
    parts = message.text.split('-')
    if len(parts) != 2:
        await message.answer("❌ Ошибка! Введите две даты через дефис")
        return
    db.update_user(message.from_user.id, leave_start_date=parts[0].strip(), leave_end_date=parts[1].strip())
    await message.answer("✅ Даты отпуска обновлены!")
    await state.clear()
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(lambda c: c.data == "edit_vlk")
async def edit_vlk_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите дату ВЛК (ДД.ММ.ГГГГ):")
    await state.set_state(EditProfileState.vlk_date)
    await callback.answer()

@router.message(EditProfileState.vlk_date)
async def edit_vlk_save(message: types.Message, state: FSMContext):
    from validators import is_valid_date
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат! Используйте: ДД.ММ.ГГГГ")
        return
    db.update_user(message.from_user.id, vlk_date=message.text)
    await message.answer("✅ Дата ВЛК обновлена!")
    await state.clear()
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(lambda c: c.data == "edit_umo")
async def edit_umo_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите дату УМО (ДД.ММ.ГГГГ) или 'нет':")
    await state.set_state(EditProfileState.umo_date)
    await callback.answer()

@router.message(EditProfileState.umo_date)
async def edit_umo_save(message: types.Message, state: FSMContext):
    umo = message.text if message.text.lower() != 'нет' else None
    db.update_user(message.from_user.id, umo_date=umo)
    await message.answer("✅ Дата УМО обновлена!")
    await state.clear()
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(lambda c: c.data == "edit_ex4_md_m")
async def edit_ex4_md_m_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите дату Упражнение 4 (Ил-76 МД-М) (ДД.ММ.ГГГГ):")
    await state.set_state(EditProfileState.exercise_4_md_m)
    await callback.answer()

@router.message(EditProfileState.exercise_4_md_m)
async def edit_ex4_md_m_save(message: types.Message, state: FSMContext):
    from validators import is_valid_date
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    db.update_user(message.from_user.id, exercise_4_md_m_date=message.text)
    await message.answer("✅ Дата обновлена!")
    await state.clear()
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(lambda c: c.data == "edit_ex7_md_m")
async def edit_ex7_md_m_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите дату Упражнение 7 (Ил-76 МД-М) (ДД.ММ.ГГГГ):")
    await state.set_state(EditProfileState.exercise_7_md_m)
    await callback.answer()

@router.message(EditProfileState.exercise_7_md_m)
async def edit_ex7_md_m_save(message: types.Message, state: FSMContext):
    from validators import is_valid_date
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    db.update_user(message.from_user.id, exercise_7_md_m_date=message.text)
    await message.answer("✅ Дата обновлена!")
    await state.clear()
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(lambda c: c.data == "edit_ex4_md_90a")
async def edit_ex4_md_90a_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите дату Упражнение 4 (Ил-76 МД-90А) (ДД.ММ.ГГГГ):")
    await state.set_state(EditProfileState.exercise_4_md_90a)
    await callback.answer()

@router.message(EditProfileState.exercise_4_md_90a)
async def edit_ex4_md_90a_save(message: types.Message, state: FSMContext):
    from validators import is_valid_date
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    db.update_user(message.from_user.id, exercise_4_md_90a_date=message.text)
    await message.answer("✅ Дата обновлена!")
    await state.clear()
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(lambda c: c.data == "edit_ex7_md_90a")
async def edit_ex7_md_90a_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите дату Упражнение 7 (Ил-76 МД-90А) (ДД.ММ.ГГГГ):")
    await state.set_state(EditProfileState.exercise_7_md_90a)
    await callback.answer()

@router.message(EditProfileState.exercise_7_md_90a)
async def edit_ex7_md_90a_save(message: types.Message, state: FSMContext):
    from validators import is_valid_date
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат!")
        return
    db.update_user(message.from_user.id, exercise_7_md_90a_date=message.text)
    await message.answer("✅ Дата обновлена!")
    await state.clear()
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())

@router.callback_query(lambda c: c.data == "edit_parachute")
async def edit_parachute_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите дату прыжков с парашютом (ДД.ММ.ГГГГ) или 'освобожден':")
    await state.set_state(EditProfileState.parachute_jump)
    await callback.answer()

@router.message(EditProfileState.parachute_jump)
async def edit_parachute_save(message: types.Message, state: FSMContext):
    if message.text.lower() in ['освобожден', 'освобождён', 'осв']:
        parachute = 'освобожден'
    else:
        from validators import is_valid_date
        if not is_valid_date(message.text):
            await message.answer("❌ Неверный формат!")
            return
        parachute = message.text
    db.update_user(message.from_user.id, parachute_jump_date=parachute)
    await message.answer("✅ Дата обновлена!")
    await state.clear()
    user = db.get_user(message.from_user.id)
    profile_text = generate_profile_text(user)
    bans = check_flight_ban(user)
    if bans:
        profile_text += "\n\nПОЛЁТЫ ЗАПРЕЩЕНЫ:\n" + "\n".join(bans)
    await message.answer(profile_text, reply_markup=get_profile_keyboard())
