# ============================================================================
# main.py - Точка входа Telegram бота
# ============================================================================

import logging
import asyncio
import time
import os
from datetime import datetime
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, DB_NAME
from database import Database
from health_server import start_health_server

# Импортируем роутеры из handlers
from handlers import registration, menu, profile, admin, search, welcome

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database(DB_NAME)

# Регистрируем роутеры
dp.include_router(registration.router)
dp.include_router(menu.router)
dp.include_router(profile.router)
dp.include_router(admin.router)
dp.include_router(search.router)
dp.include_router(welcome.router)

async def main():
    """Основная функция запуска бота"""
    
    # Генерируем уникальный ID экземпляра
    instance_id = f"instance_{os.getpid()}_{int(time.time())}"
    logging.info(f"🤖 Запуск экземпляра: {instance_id}")
    
    # Проверка текущего статуса блокировки
    lock_status = db.check_lock_status()
    if lock_status:
        logging.info(f"📊 Текущая блокировка: {lock_status['instance_id']}")
    
    # Попытка захвата блокировки
    logging.info("🔒 Попытка захвата блокировки...")
    if not db.check_and_acquire_lock(instance_id):
        logging.error("❌ Не удалось захватить блокировку! Другой экземпляр уже работает.")
        return
    
    logging.info("✅ Блокировка успешно захвачена!")
    
    try:
        # Запускаем HTTP сервер для health check (чтобы Render был доволен)
        logging.info("🌐 Запуск HTTP сервера для health check...")
        health_runner = await start_health_server(port=8080)
        
        # Принудительная очистка webhook
        logging.info("🔄 Очистка webhook...")
        for attempt in range(3):
            try:
                await bot.delete_webhook(drop_pending_updates=True)
                logging.info(f"✅ Webhook удалён (попытка {attempt + 1})")
                await asyncio.sleep(2)
                break
            except Exception as e:
                logging.warning(f"⚠️ Попытка {attempt + 1} не удалась: {e}")
                await asyncio.sleep(3)
        
        await asyncio.sleep(5)
        
        # Heartbeat задача (обновление блокировки каждые 30 сек)
        async def heartbeat_task():
            while True:
                try:
                    db.update_heartbeat(instance_id)
                    logging.debug("💓 Heartbeat отправлен")
                except Exception as e:
                    logging.error(f"❌ Ошибка heartbeat: {e}")
                await asyncio.sleep(30)
        
               # Запускаем heartbeat в фоне
        heartbeat_future = asyncio.create_task(heartbeat_task())
        
        # Запускаем polling
        logging.info("✅ Запускаем polling...")
        
        # 🔍 DEBUG: Тестовый лог перед polling
        logging.info("🔍 DEBUG: Перед запуском polling")
        print("🔍 DEBUG: Перед запуском polling")
        
        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except Exception as e:
            logging.error(f"❌ Ошибка polling: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # Отменяем heartbeat при остановке
        heartbeat_future.cancel()
        
        # Останавливаем HTTP сервер
        await health_runner.cleanup()
        
    except Exception as e:
        logging.error(f"❌ Ошибка в main: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logging.info("🛑 Остановка бота...")
        db.release_lock(instance_id)
        await bot.session.close()
        db.close()
        logging.info("✅ Бот полностью остановлен")

if __name__ == "__main__":
    asyncio.run(main())
