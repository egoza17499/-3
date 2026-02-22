# ============================================================================
# main.py - Точка входа Telegram бота
# ============================================================================

import logging
import asyncio
import time
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN, DATABASE_URL
from db_manager import db
from health_server import start_health_server
from handlers.multiple_aerodromes import register_multiple_aerodromes_handlers

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================================================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ============================================================================
# РЕГИСТРАЦИЯ РОУТЕРОВ
# ============================================================================

def setup_routers():
    """Импорт и регистрация всех роутеров"""
    logger.info("🔍 Начинаем импорт handlers...")
    from handlers import registration, menu, profile, admin, search, welcome, knowledge
    
    dp.include_router(registration.router)
    logger.info("✅ registration зарегистрирован")
    
    dp.include_router(menu.router)
    logger.info("✅ menu зарегистрирован")
    
    dp.include_router(profile.router)
    logger.info("✅ profile зарегистрирован")
    
    dp.include_router(admin.router)
    logger.info("✅ admin зарегистрирован")
    
    # ВАЖНО: knowledge ДОЛЖЕН БЫТЬ ДО search!
    dp.include_router(knowledge.router)  # ← ПЕРЕМЕСТИТЬ СЮДА!
    logger.info("✅ knowledge зарегистрирован")
    
    dp.include_router(search.router)
    logger.info("✅ search зарегистрирован")
    
    dp.include_router(welcome.router)
    logger.info("✅ welcome зарегистрирован")
    
    logger.info("✅ Все роутеры зарегистрированы успешно!")

# ============================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================================

async def main():
    """Основная функция запуска бота"""
    
    # Вызываем регистрацию роутеров ВНУТРИ main()
    setup_routers()
    
    instance_id = f"instance_{os.getpid()}_{int(time.time())}"
    logger.info(f"🤖 Запуск экземпляра: {instance_id}")
    
    # Проверка блокировки
    lock_status = db.check_lock_status()
    if lock_status:
        logger.info(f"📊 Текущая блокировка: {lock_status['instance_id']}")
    
    logger.info("🔒 Попытка захвата блокировки...")
    if not db.check_and_acquire_lock(instance_id):
        logger.error("❌ Не удалось захватить блокировку! Другой экземпляр уже работает.")
        return
    
    logger.info("✅ Блокировка успешно захвачена!")
    
    try:
        # HTTP сервер для health check
        logger.info("🌐 Запуск HTTP сервера для health check...")
        health_runner = await start_health_server(port=8080)
        
        # Очистка webhook
        logger.info("🔄 Очистка webhook...")
        for attempt in range(3):
            try:
                await bot.delete_webhook(drop_pending_updates=True)
                logger.info(f"✅ Webhook удалён (попытка {attempt + 1})")
                await asyncio.sleep(2)
                break
            except Exception as e:
                logger.warning(f"⚠️ Попытка {attempt + 1} не удалась: {e}")
                await asyncio.sleep(3)
        
        await asyncio.sleep(5)
        
        # Heartbeat задача
        async def heartbeat_task():
            while True:
                try:
                    db.update_heartbeat(instance_id)
                except Exception as e:
                    logger.error(f"❌ Ошибка heartbeat: {e}")
                await asyncio.sleep(30)
        
        heartbeat_future = asyncio.create_task(heartbeat_task())
        
        # Запуск polling
        logger.info("✅ Запускаем polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
        heartbeat_future.cancel()
        await health_runner.cleanup()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в main: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        logger.info("🛑 Остановка бота...")
        db.release_lock(instance_id)
        await bot.session.close()
        db.close()
        logger.info("✅ Бот полностью остановлен")

# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == "__main__":
    asyncio.run(main())
