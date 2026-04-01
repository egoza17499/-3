#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✈️ handlers/aerodrome_search.py
Поиск и отображение аэродромов
✅ Использует правильные импорты и методы БД
"""

from aiogram import Router, F, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup  # ✅ Message отсюда
from db_manager import db, get_aerodromes_by_city, get_aerodrome_by_id, get_aerodrome_phones
import logging

logger = logging.getLogger(__name__)  # ✅ __name__ правильно
router = Router()


async def send_all_aerodromes_in_city(message: Message, city_name: str):
    """Отправить все аэродромы в городе"""
    try:
        # ✅ ИСПОЛЬЗУЕМ готовую функцию из db_manager
        aerodromes = get_aerodromes_by_city(city_name)
        
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
        
        keyboard_buttons = []
        
        for aero in aerodromes:
            display_name = aero.get('airport_name') if aero.get('airport_name') else aero.get('name')
            text += f"• {display_name}\n"
            
            keyboard_buttons.append([InlineKeyboardButton(
                f"🛫 {display_name}",
                callback_data=f"aerodrome_{aero['id']}"
            )])
        
        keyboard_buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_search")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка при поиске аэродромов в {city_name}: {e}")
        await message.answer("❌ Произошла ошибка при поиске")


async def show_aerodrome_details(message: Message, aerodrome_id: int):
    """Показать подробную информацию об аэродроме"""
    try:
        # ✅ Получаем информацию об аэродроме через готовую функцию
        aero_info = get_aerodrome_by_id(aerodrome_id)
        
        if not aero_info:
            await message.answer("❌ Аэродром не найден")
            return
        
        # ✅ Получаем телефоны через готовую функцию
        phones = get_aerodrome_phones(aerodrome_id)
        
        # Формируем сообщение
        display_name = aero_info.get('airport_name') if aero_info.get('airport_name') else aero_info.get('name')
        text = f"✈️ <b>{display_name}</b>\n"
        text += f"🏙️ <b>Город:</b> {aero_info.get('city')}\n"
        
        if aero_info.get('airport_name') and aero_info.get('airport_name') != aero_info.get('name'):
            text += f"📍 <b>Аэродром:</b> {aero_info.get('airport_name')}\n"
        
        text += f"🏠 <b>Жилье:</b> {aero_info.get('housing_info') if aero_info.get('housing_info') else 'Уточняется'}\n\n"
        
        if phones:
            text += "📞 <b>Полезные номера телефонов:</b>\n"
            for phone in phones:
                text += f"• {phone.get('phone_name')}: {phone.get('phone_number')}\n"
        
        # Кнопки
        keyboard_buttons = [
            [InlineKeyboardButton("🔍 Повторный поиск", callback_data="new_search")],
            [InlineKeyboardButton("📋 В главное меню", callback_data="main_menu")]
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка при показе аэродрома {aerodrome_id}: {e}")
        await message.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("aerodrome_"))
async def callback_aerodrome_selection(callback: types.CallbackQuery):
    """Обработчик выбора аэродрома из списка"""
    try:
        aerodrome_id = int(callback.data.split("_")[1])
        await show_aerodrome_details(callback.message, aerodrome_id)
        await callback.answer()
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка: неверный ID аэродрома", show_alert=True)


def register_multiple_aerodromes_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)
