import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from db_manager import db

logger = logging.getLogger(__name__)
router = Router()

# Этот обработчик теперь НЕ будет перехватывать сообщения когда пользователь в состоянии поиска аэродромов
@router.message(lambda msg: msg.text not in ["👤 Мой профиль", "📚 Полезная информация", "🛡️ Административные функции"])
async def search_aerodrome(message: types.Message, state: FSMContext):
    # Проверяем состояние — если пользователь в поиске аэродрома, пропускаем сообщение
    current_state = await state.get_state()
    if current_state == "KnowledgeState:aerodrome_search":
        return  # Пропускаем сообщение, пусть обрабатывает knowledge.py
    
    keyword = message.text
    results = db.search_aerodromes(keyword)
    if results:
        for result in results:
            await message.answer(result[0])
    else:
        await message.answer("❌ Информация не найдена")
