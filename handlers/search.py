import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from db_manager import db

logger = logging.getLogger(__name__)
router = Router()

# Обработчик для поиска ПОЛЬЗОВАТЕЛЕЙ
# ВАЖНО: Фильтр исключает сообщения когда пользователь в поиске аэродрома
@router.message(
    lambda msg: msg.text not in ["👤 Мой профиль", "📚 Полезная информация", "🛡️ Административные функции"]
)
async def search_users_handler(message: types.Message, state: FSMContext):
    # Проверяем состояние
    current_state = await state.get_state()
    
    # Если пользователь в поиске аэродрома — СРАЗУ ВЫХОДИМ
    # Это позволит обработчику из knowledge.py обработать сообщение
    if current_state == "KnowledgeState:aerodrome_search":
        return  # Выходим — сообщение обработают другие обработчики
    
    # Ищем ПОЛЬЗОВАТЕЛЕЙ
    search_text = message.text.strip()
    users = db.search_users(search_text)
    
    if users:
        text = f"🔍 Найдено пользователей: {len(users)}\n\n"
        for user in users:
            user_id = user[0]
            username = user[1] or ""
            fio = user[3] or "Не указано"
            rank = user[4] or ""
            
            text += f"👤 {fio}\n"
            text += f"✈️ @{username}\n"
            if rank:
                text += f"🎖 {rank}\n"
            text += "\n"
        
        await message.answer(text)
    else:
        await message.answer(f"❌ Пользователь \"{search_text}\" не найден")
