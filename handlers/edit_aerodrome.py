from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db_manager import (
    db,
    get_aerodrome_by_id,
    get_aerodrome_phones,
    add_aerodrome_phone,
    delete_aerodrome_phone
)
from states import EditAerodromeState
import logging

logger = logging.getLogger(__name__)
router = Router()

# ============================================================
# МЕНЮ РЕДАКТИРОВАНИЯ АЭРОДРОМА
# ============================================================

@router.callback_query(F.data.startswith("edit_aerodrome_"))
async def edit_aerodrome_menu(callback: types.CallbackQuery, state: FSMContext):
    """Показать меню редактирования аэродрома"""
    try:
        aerodrome_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка: неверный ID аэродрома", show_alert=True)
        return
    
    # Получаем информацию об аэродроме
    aerodrome = get_aerodrome_by_id(aerodrome_id)
    
    if not aerodrome:
        await callback.answer("❌ Аэродром не найден", show_alert=True)
        return
    
    # Сохраняем ID в состоянии
    await state.update_data(aerodrome_id=aerodrome_id)
    
    # Получаем телефоны
    phones = get_aerodrome_phones(aerodrome_id)
    
    # Формируем текст
    text = f"✏️ <b>Редактирование: {aerodrome['name']}</b>\n\n"
    
    if aerodrome['city']:
        text += f"🏙 <b>Город:</b> {aerodrome['city']}\n"
    
    if aerodrome['airport_name'] and aerodrome['airport_name'] != aerodrome['name']:
        text += f"✈️ <b>Аэродром:</b> {aerodrome['airport_name']}\n"
    
    text += f"🏠 <b>Жилье:</b> {aerodrome['housing_info'] or 'Не указано'}\n\n"
    
    if phones:
        text += "📞 <b>Текущие телефоны:</b>\n"
        for phone in phones:
            text += f"• {phone['phone_name']}: {phone['phone_number']}\n"
    else:
        text += "📞 <b>Телефоны:</b> Не добавлены\n"
    
    text += "\n<b>Выберите действие:</b>"
    
    # Создаем меню
    keyboard = [
        [InlineKeyboardButton(text="📱 Добавить телефон", callback_data="edit_add_phone")],
        [InlineKeyboardButton(text="✏️ Изменить телефон", callback_data="edit_change_phone")],
        [InlineKeyboardButton(text="🏠 Изменить жилье", callback_data="edit_change_housing")],
        [InlineKeyboardButton(text="🔙 Назад к аэродрому", callback_data=f"edit_back_{aerodrome_id}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()

# ============================================================
# ДОБАВЛЕНИЕ ТЕЛЕФОНА
# ============================================================

@router.callback_query(F.data == "edit_add_phone")
async def edit_add_phone(callback: types.CallbackQuery, state: FSMContext):
    """Начать добавление телефона"""
    await callback.message.edit_text(
        "📱 <b>Добавление телефона</b>\n\n"
        "Введите название телефона (например: АДП, Диспетчер, УС и т.д.):",
        parse_mode="HTML"
    )
    await state.set_state(EditAerodromeState.add_phone_name)
    await callback.answer()

@router.message(EditAerodromeState.add_phone_name)
async def edit_add_phone_name(message: types.Message, state: FSMContext):
    """Сохраняем название телефона и запрашиваем номер"""
    phone_name = message.text.strip()
    await state.update_data(phone_name=phone_name)
    
    await message.answer(
        "📱 <b>Введите номер телефона:</b>\n\n"
        "Пример: 8-999-123-45-67",
        parse_mode="HTML"
    )
    await state.set_state(EditAerodromeState.add_phone_number)

@router.message(EditAerodromeState.add_phone_number)
async def edit_add_phone_number(message: types.Message, state: FSMContext):
    """Добавляем телефон в базу"""
    phone_number = message.text.strip()
    data = await state.get_data()
    aerodrome_id = data.get('aerodrome_id')
    phone_name = data.get('phone_name')
    
    if not aerodrome_id or not phone_name:
        await message.answer("❌ Ошибка: потеряны данные. Начните сначала.")
        await state.clear()
        return
    
    # Добавляем телефон
    try:
        add_aerodrome_phone(aerodrome_id, phone_name, phone_number)
        
        await message.answer(
            f"✅ <b>Телефон добавлен!</b>\n\n"
            f"📱 {phone_name}: {phone_number}\n\n"
            "Выберите дальнейшее действие:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ Добавить еще телефон", callback_data="edit_add_phone")],
                [InlineKeyboardButton(text="🔙 К меню аэродрома", callback_data=f"edit_aerodrome_{aerodrome_id}")]
            ])
        )
    except Exception as e:
        logger.error(f"Ошибка при добавлении телефона: {e}")
        await message.answer("❌ Ошибка при добавлении телефона. Попробуйте снова.")
    
    await state.clear()

# ============================================================
# ИЗМЕНЕНИЕ ТЕЛЕФОНА
# ============================================================

@router.callback_query(F.data == "edit_change_phone")
async def edit_change_phone(callback: types.CallbackQuery, state: FSMContext):
    """Показать список телефонов для изменения"""
    data = await state.get_data()
    aerodrome_id = data.get('aerodrome_id')
    
    if not aerodrome_id:
        await callback.answer("❌ Ошибка: не найден аэродром", show_alert=True)
        return
    
    phones = get_aerodrome_phones(aerodrome_id)
    
    if not phones:
        await callback.answer("❌ Нет телефонов для изменения", show_alert=True)
        return
    
    text = "✏️ <b>Выберите телефон для изменения:</b>\n\n"
    
    keyboard = []
    for phone in phones:
        keyboard.append([InlineKeyboardButton(
            text=f"📱 {phone['phone_name']}: {phone['phone_number']}",
            callback_data=f"edit_phone_{phone['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        text="🔙 Назад",
        callback_data=f"edit_aerodrome_{aerodrome_id}"
    )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("edit_phone_"))
async def edit_phone_select(callback: types.CallbackQuery, state: FSMContext):
    """Выбор действия для телефона"""
    try:
        phone_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка: неверный ID телефона", show_alert=True)
        return
    
    await state.update_data(phone_id=phone_id)
    
    text = "✏️ <b>Что сделать с телефоном?</b>\n\n"
    text += "Выберите действие:"
    
    keyboard = [
        [InlineKeyboardButton(text="🔄 Изменить номер", callback_data="edit_phone_change_number")],
        [InlineKeyboardButton(text="🗑️ Удалить телефон", callback_data="edit_phone_delete")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="edit_change_phone")]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "edit_phone_change_number")
async def edit_phone_change_number(callback: types.CallbackQuery, state: FSMContext):
    """Изменить номер телефона"""
    await callback.message.edit_text(
        "📱 <b>Введите новый номер телефона:</b>\n\n"
        "Пример: 8-999-123-45-67",
        parse_mode="HTML"
    )
    await state.set_state(EditAerodromeState.change_phone_number)
    await callback.answer()

@router.message(EditAerodromeState.change_phone_number)
async def edit_phone_change_number_process(message: types.Message, state: FSMContext):
    """Сохраняем новый номер телефона"""
    new_number = message.text.strip()
    data = await state.get_data()
    phone_id = data.get('phone_id')
    aerodrome_id = data.get('aerodrome_id')
    
    if not phone_id or not aerodrome_id:
        await message.answer("❌ Ошибка: потеряны данные. Начните сначала.")
        await state.clear()
        return
    
    try:
        # Обновляем номер
        db.execute_query(
            "UPDATE aerodrome_phones SET phone_number = %s WHERE id = %s",
            (new_number, phone_id)
        )
        
        await message.answer(
            f"✅ <b>Номер телефона обновлен!</b>\n\n"
            f"📱 Новый номер: {new_number}\n\n"
            "Выберите дальнейшее действие:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Изменить другой телефон", callback_data="edit_change_phone")],
                [InlineKeyboardButton(text="🔙 К меню аэродрома", callback_data=f"edit_aerodrome_{aerodrome_id}")]
            ])
        )
    except Exception as e:
        logger.error(f"Ошибка при обновлении телефона: {e}")
        await message.answer("❌ Ошибка при обновлении номера. Попробуйте снова.")
    
    await state.clear()

@router.callback_query(F.data == "edit_phone_delete")
async def edit_phone_delete(callback: types.CallbackQuery, state: FSMContext):
    """Удалить телефон"""
    data = await state.get_data()
    phone_id = data.get('phone_id')
    aerodrome_id = data.get('aerodrome_id')
    
    if not phone_id or not aerodrome_id:
        await callback.answer("❌ Ошибка: потеряны данные", show_alert=True)
        await state.clear()
        return
    
    try:
        # Удаляем телефон
        delete_aerodrome_phone(phone_id)
        
        await callback.message.edit_text(
            "✅ <b>Телефон удален!</b>\n\n"
            "Выберите дальнейшее действие:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Изменить другой телефон", callback_data="edit_change_phone")],
                [InlineKeyboardButton(text="🔙 К меню аэродрома", callback_data=f"edit_aerodrome_{aerodrome_id}")]
            ])
        )
    except Exception as e:
        logger.error(f"Ошибка при удалении телефона: {e}")
        await callback.answer("❌ Ошибка при удалении телефона", show_alert=True)
    
    await state.clear()

# ============================================================
# ИЗМЕНЕНИЕ ИНФОРМАЦИИ О ЖИЛЬЕ
# ============================================================

@router.callback_query(F.data == "edit_change_housing")
async def edit_change_housing(callback: types.CallbackQuery, state: FSMContext):
    """Начать изменение информации о жилье"""
    data = await state.get_data()
    aerodrome_id = data.get('aerodrome_id')
    
    if not aerodrome_id:
        await callback.answer("❌ Ошибка: не найден аэродром", show_alert=True)
        return
    
    aerodrome = get_aerodrome_by_id(aerodrome_id)
    
    if not aerodrome:
        await callback.answer("❌ Аэродром не найден", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"🏠 <b>Изменение информации о жилье</b>\n\n"
        f"Текущая информация: {aerodrome['housing_info'] or 'Не указано'}\n\n"
        f"Введите новую информацию о жилье:",
        parse_mode="HTML"
    )
    await state.set_state(EditAerodromeState.change_housing)
    await callback.answer()

@router.message(EditAerodromeState.change_housing)
async def edit_change_housing_process(message: types.Message, state: FSMContext):
    """Сохраняем новую информацию о жилье"""
    housing_info = message.text.strip()
    data = await state.get_data()
    aerodrome_id = data.get('aerodrome_id')
    
    if not aerodrome_id:
        await message.answer("❌ Ошибка: потеряны данные. Начните сначала.")
        await state.clear()
        return
    
    try:
        # Обновляем информацию
        db.update_aerodrome(aerodrome_id, housing_info=housing_info)
        
        await message.answer(
            f"✅ <b>Информация о жилье обновлена!</b>\n\n"
            f"🏠 {housing_info}\n\n"
            "Выберите дальнейшее действие:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Изменить жилье", callback_data="edit_change_housing")],
                [InlineKeyboardButton(text="🔙 К меню аэродрома", callback_data=f"edit_aerodrome_{aerodrome_id}")]
            ])
        )
    except Exception as e:
        logger.error(f"Ошибка при обновлении жилья: {e}")
        await message.answer("❌ Ошибка при обновлении информации. Попробуйте снова.")
    
    await state.clear()

# ============================================================
# НАЗАД К АЭРОДРОМУ
# ============================================================

@router.callback_query(F.data.startswith("edit_back_"))
async def edit_back_to_aerodrome(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к просмотру аэродрома"""
    try:
        aerodrome_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка: неверный ID аэродрома", show_alert=True)
        return
    
    # Очищаем состояние
    await state.clear()
    
    # Получаем информацию об аэродроме
    aerodrome = get_aerodrome_by_id(aerodrome_id)
    
    if not aerodrome:
        await callback.answer("❌ Аэродром не найден", show_alert=True)
        return
    
    # Формируем текст (дублируем логику из knowledge.py)
    city = aerodrome['city'] or aerodrome['name']
    airport = aerodrome['airport_name'] or ""
    housing = aerodrome['housing_info'] or "Информация уточняется"
    
    text = f"🏙 {city}"
    if airport:
        text += f"\n✈️ Аэродром: {airport}"
    text += f"\n🏠 Жилье: {housing}\n\n"
    
    # Телефоны
    phones = get_aerodrome_phones(aerodrome_id)
    if phones:
        text += "📞 Полезные номера телефонов:\n"
        for phone in phones:
            text += f"• {phone['phone_name']}: {phone['phone_number']}\n"
        text += "\n"
    
    # Кнопки
    keyboard_buttons = [
        [InlineKeyboardButton(text="🔍 Повторный поиск", callback_data="info_aerodrome_btn")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_aerodrome_{aerodrome_id}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Используем edit_text вместо удаления сообщения
    await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()
