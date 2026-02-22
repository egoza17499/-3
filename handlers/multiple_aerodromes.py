from aiogram import types, Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db_manager import db
import logging

logger = logging.getLogger(__name__)
router = Router()

async def send_all_aerodromes_in_city(message: types.Message, city_name: str):
    """Отправить все аэродромы в городе"""
    try:
        # Ищем все аэродромы в городе (учитываем разные написания)
        aerodromes = await db.fetch_all(
            """
            SELECT DISTINCT id, name, city, airport_name, housing_info
            FROM aerodromes
            WHERE LOWER(city) = LOWER($1) 
               OR LOWER(name) ILIKE $2
            ORDER BY airport_name, name
            """,
            city_name, f'%{city_name}%'
        )
        
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
        aero_info = await db.fetch_one(
            """
            SELECT id, name, city, airport_name, housing_info
            FROM aerodromes
            WHERE id = $1
            """,
            aerodrome_id
        )
        
        if not aero_info:
            await message.answer("❌ Аэродром не найден")
            return
        
        # Получаем телефоны
        phones = await db.fetch_all(
            """
            SELECT phone_name, phone_number
            FROM aerodrome_phones
            WHERE aerodrome_id = $1
            ORDER BY phone_name
            """,
            aerodrome_id
        )
        
        # Формируем сообщение
        display_name = aero_info['airport_name'] if aero_info['airport_name'] else aero_info['name']
        text = f"✈️ <b>{display_name}</b>\n"
        text += f"🏙️ <b>Город:</b> {aero_info['city']}\n"
        
        if aero_info['airport_name'] and aero_info['airport_name'] != aero_info['name']:
            text += f"📍 <b>Аэродром:</b> {aero_info['airport_name']}\n"
        
        text += f"🏠 <b>Жилье:</b> {aero_info['housing_info'] if aero_info['housing_info'] else 'Уточняется'}\n\n"
        
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

@router.callback_query(F.data.startswith("aerodrome_"))
async def callback_aerodrome_selection(callback: types.CallbackQuery):
    """Обработчик выбора аэродрома из списка"""
    aerodrome_id = int(callback.data.split("_")[1])
    await show_aerodrome_details(callback.message, aerodrome_id)
    await callback.answer()

def register_multiple_aerodromes_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)
