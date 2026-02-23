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
    aerodrome = get_aerodrome_by_id(aerodrome_id)  # ✅ Исправлено
    
    if not aerodrome:
        await callback.answer("❌ Аэродром не найден", show_alert=True)
        return
    
    # Сохраняем ID в состоянии
    await state.update_data(aerodrome_id=aerodrome_id)
    
    # Получаем телефоны
    phones = get_aerodrome_phones(aerodrome_id)  # ✅ Исправлено
    
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

# ... (остальной код остается без изменений, но везде замените:)
# db.get_aerodrome_by_id() → get_aerodrome_by_id()
# db.get_aerodrome_phones() → get_aerodrome_phones()
# db.add_aerodrome_phone() → add_aerodrome_phone()
# db.delete_aerodrome_phone() → delete_aerodrome_phone()
# db.execute_query() → db.execute_query() (этот оставляем через db)
# db.update_aerodrome() → db.update_aerodrome() (этот оставляем через db)
