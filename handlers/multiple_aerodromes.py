from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db_manager import db
import logging

logger = logging.getLogger(__name__)

async def send_all_aerodromes_in_city(message: types.Message, city_name: str):
    """Отправить все аэродромы в городе"""
    try:
        # Ищем все аэродромы в городе (учитываем разные написания)
        aerodromes = db.get_aerodromes_by_city(city_name)
        
        if not aerodromes:
            await message.answer(f"❌ Аэродромы в городе {city_name} не найдены")
            return
        
        # Если найден только один аэродром - показываем его сразу
        if len(aerodromes) == 1:
            await show_aerodrome_details(message, aerodromes[0]['id'])
            return
        
        # Если несколько аэродромов - показываем список с выбором
        text = f"🏙️ <b>В городе {city_name} найдено аэродромов: {len(aerodromes)}</b>\n\n"
        text += "Выберите нужный аэродром:\n\n"
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        
        for aero in aerodromes:
            display_name = aero['airport_name'] if aero['airport_name'] else aero['name']
            text += f"• {display_name}\n"
            
            keyboard.add(InlineKeyboardButton(
                f"🛫 {display_name}",
                callback_data=f"aerodrome_{aero['id']}"
            ))
        
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_search"))
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка при поиске аэродромов в {city_name}: {e}")
        await message.answer("❌ Произошла ошибка при поиске")

async def show_aerodrome_details(message: types.Message, aerodrome_id: int):
    """Показать подробную информацию об аэродроме"""
    try:
        # Получаем информацию об аэродроме
        aerodrome = db.get_aerodrome_by_id(aerodrome_id)
        
        if not aerodrome:
            await message.answer("❌ Аэродром не найден")
            return
        
        # Получаем телефоны
        phones = db.get_aerodrome_phones(aerodrome_id)
        
        # Формируем сообщение
        display_name = aerodrome['airport_name'] if aerodrome['airport_name'] else aerodrome['name']
        text = f"✈️ <b>{display_name}</b>\n"
        text += f"🏙️ <b>Город:</b> {aerodrome['city']}\n"
        
        if aerodrome['airport_name'] and aerodrome['airport_name'] != aerodrome['name']:
            text += f"📍 <b>Аэродром:</b> {aerodrome['airport_name']}\n"
        
        text += f"🏠 <b>Жилье:</b> {aerodrome['housing_info'] if aerodrome['housing_info'] else 'Уточняется'}\n\n"
        
        if phones:
            text += "📞 <b>Полезные номера телефонов:</b>\n"
            for phone in phones:
                text += f"• {phone['phone_name']}: {phone['phone_number']}\n"
        
        # Кнопки
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton("🔍 Повторный поиск", callback_data="new_search"))
        keyboard.add(InlineKeyboardButton("📋 В главное меню", callback_data="main_menu"))
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка при показе аэродрома {aerodrome_id}: {e}")
        await message.answer("❌ Произошла ошибка")

async def callback_aerodrome_selection(callback: types.CallbackQuery):
    """Обработчик выбора аэродрома из списка"""
    if callback.data.startswith("aerodrome_"):
        aerodrome_id = int(callback.data.split("_")[1])
        await show_aerodrome_details(callback.message, aerodrome_id)
        await callback.answer()

def register_multiple_aerodromes_handlers(dp: Dispatcher):
    """Регистрация обработчиков"""
    dp.register_callback_handler(callback_aerodrome_selection, lambda c: c.data.startswith("aerodrome_"))
