from aiogram import Router, F, types, Message
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
import logging
import psycopg2
from config import DATABASE_URL


logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "/update_housing")
async def update_housing_command(message: types.Message):
    """Админ команда для обновления информации о жилье"""
    
    user_id = message.from_user.id
    
    # Проверяем что это админ
    if user_id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав для выполнения этой команды")
        return
    
    await message.answer("🔄 Начинаю обновление информации о жилье...")
    
    try:
        from update_aerodromes_housing import update_all_aerodromes
        
        updated_count = update_all_aerodromes()
        
        await message.answer(
            f"✅ Обновление завершено!\n\n"
            f"📊 Обновлено аэродромов: {updated_count}\n"
            f"✅ Теперь проверьте в поиске: 'Москва', 'Новосибирск'"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении жилья: {e}")
        await message.answer(f"❌ Ошибка: {e}")

# Импортируем этот роутер в main.py
