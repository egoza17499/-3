import logging
from aiogram import Router, F, types

logger = logging.getLogger(__name__)
router = Router()

@router.message(lambda msg: msg.text not in ["👤 Мой профиль", "📚 Полезная информация", "🛡 Административные функции"])
async def search_aerodrome(message: types.Message):
    from main import db
    keyword = message.text
    results = db.search_aerodromes(keyword)
    if results:
        for result in results:
            await message.answer(result[0])
    else:
        await message.answer("❌ Информация не найдена")
