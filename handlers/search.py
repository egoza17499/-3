import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db_manager import db
from states import KnowledgeState

logger = logging.getLogger(__name__)
router = Router()

# Обработчик для поиска ПОЛЬЗОВАТЕЛЕЙ
@router.message(lambda msg: msg.text not in ["👤 Мой профиль", "📚 Полезная информация", "🛡️ Административные функции"])
async def search_users_handler(message: types.Message, state: FSMContext):
    # Проверяем состояние — если пользователь в поиске аэродрома, пропускаем
    current_state = await state.get_state()
    
    if current_state == "KnowledgeState:aerodrome_search":
        return  # Пропускаем — обрабатывает knowledge.py
    
    # Ищем ПОЛЬЗОВАТЕЛЕЙ (не аэродромы!)
    search_text = message.text.strip()
    users = db.search_users(search_text)
    
    if users:
        text = f"🔍 Найдено пользователей: {len(users)}\n\n"
        for user in users:
            # user = (user_id, username, registered_at, fio, rank, qualification, ...)
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

# ============================================================================
# АДМИНСКИЕ ФУНКЦИИ
# ============================================================================

@router.callback_query(lambda c: c.data == "admin_functions")
async def admin_functions(callback: types.CallbackQuery):
    # Проверяем права админа
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    if not await db.check_admin_status(user_id, username):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🛡️ Административные функции\n\n"
        "Выберите действие:"
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_user_list")
async def admin_user_list(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    if not await db.check_admin_status(user_id, username):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    users = db.get_all_users()
    
    if not users:
        await callback.answer("📋 Пользователи не найдены", show_alert=True)
        return
    
    text = f"📋 Список пользователей ({len(users)}):\n\n"
    for user in users[:20]:  # Показываем первые 20
        fio = user[3] or "Не указано"
        username_user = user[1] or ""
        text += f"• {fio} (@{username_user})\n"
    
    if len(users) > 20:
        text += f"\n... и ещё {len(users) - 20}"
    
    await callback.message.answer(text)
    await callback.answer()
