from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

async def send_all_aerodromes_in_city(message: types.Message, city_name: str):
    """Отправить все аэродромы в городе"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ищем все аэродромы в городе (учитываем разные написания)
        cursor.execute("""
            SELECT DISTINCT a.id, a.name, a.airport_name, a.housing_info
            FROM aerodromes a
            WHERE LOWER(a.city) = LOWER(%s) 
               OR LOWER(a.name) ILIKE %s
            ORDER BY a.airport_name, a.name
        """, (city_name, f'%{city_name}%'))
        
        aerodromes = cursor.fetchall()
        
        if not aerodromes:
            await message.answer(f"❌ Аэродромы в городе {city_name} не найдены")
            return
        
        # Если найден только один аэродром - показываем его сразу
        if len(aerodromes) == 1:
            await show_aerodrome_details(message, aerodromes[0][0])
            return
        
        # Если несколько аэродромов - показываем список с выбором
        text = f"🏙️ <b>В городе {city_name} найдено аэродромов: {len(aerodromes)}</b>\n\n"
        text += "Выберите нужный аэродром:\n\n"
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        
        for aero in aerodromes:
            aero_id, name, airport_name, housing = aero
            display_name = airport_name if airport_name else name
            text += f"• {display_name}\n"
            
            keyboard.add(InlineKeyboardButton(
                f"🛫 {display_name}",
                callback_data=f"aerodrome_{aero_id}"
            ))
        
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_search"))
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Ошибка при поиске аэродромов в {city_name}: {e}")
        await message.answer("❌ Произошла ошибка при поиске")

async def show_aerodrome_details(message: types.Message, aerodrome_id: int):
    """Показать подробную информацию об аэродроме"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Получаем информацию об аэродроме
        cursor.execute("""
            SELECT name, city, airport_name, housing_info
            FROM aerodromes
            WHERE id = %s
        """, (aerodrome_id,))
        
        aero_info = cursor.fetchone()
        if not aero_info:
            await message.answer("❌ Аэродром не найден")
            return
        
        name, city, airport_name, housing = aero_info
        
        # Получаем телефоны
        cursor.execute("""
            SELECT phone_name, phone_number
            FROM aerodrome_phones
            WHERE aerodrome_id = %s
            ORDER BY phone_name
        """, (aerodrome_id,))
        
        phones = cursor.fetchall()
        
        # Формируем сообщение
        display_name = airport_name if airport_name else name
        text = f"✈️ <b>{display_name}</b>\n"
        text += f"🏙️ <b>Город:</b> {city}\n"
        
        if airport_name and airport_name != name:
            text += f"📍 <b>Аэродром:</b> {airport_name}\n"
        
        text += f"🏠 <b>Жилье:</b> {housing if housing else 'Уточняется'}\n\n"
        
        if phones:
            text += "📞 <b>Полезные номера телефонов:</b>\n"
            for phone_name, phone_number in phones:
                text += f"• {phone_name}: {phone_number}\n"
        
        # Кнопки
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton("🔍 Повторный поиск", callback_data="new_search"))
        keyboard.add(InlineKeyboardButton("📋 В главное меню", callback_data="main_menu"))
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
        cursor.close()
        conn.close()
        
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
