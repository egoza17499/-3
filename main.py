# ============================================================================
# main.py - Точка входа Telegram бота
# ============================================================================

import logging
import asyncio
import time
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# ПРОВЕРКА КОНФИГУРАЦИИ
# ============================================================================

def check_config():
    """Проверка необходимых переменных окружения"""
    errors = []
    
    if not os.getenv("BOT_TOKEN"):
        errors.append("❌ BOT_TOKEN не найден")
    
    if not os.getenv("DATABASE_URL"):
        errors.append("❌ DATABASE_URL не найден")
    
    if errors:
        for error in errors:
            logger.error(error)
        raise ValueError("Конфигурация невалидна!")
    
    logger.info("✅ Конфигурация проверена")

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================================================

# Проверяем конфиг до импорта модулей
check_config()

from config import BOT_TOKEN, DATABASE_URL, ADMIN_IDS
from db_manager import db
from health_server import start_health_server

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ============================================================================
# РЕГИСТРАЦИЯ РОУТЕРОВ
# ============================================================================

def setup_routers():
    """Импорт и регистрация всех роутеров"""
    logger.info("🔍 Начинаем регистрацию handlers...")
    
    try:
        # Импортируем роутеры в правильном порядке
        from handlers import welcome      # 1. Приветствие (/start)
        from handlers import registration # 2. Регистрация
        from handlers import menu         # 3. Главное меню
        from handlers import profile      # 4. Профиль
        from handlers import group
        from handlers import knowledge    # 5. Поиск аэродромов (ДО search!)
        from handlers import edit_aerodrome # 6. Редактирование аэродромов
        from handlers import admin        # 7. Админ функции        
        from handlers import search       # 8. Поиск пользователей (только админ)
        from handlers import admin_commands  # 9. Админ команды (ОБНОВЛЕНИЕ ЖИЛЬЯ)
        
        # Регистрируем роутеры (порядок важен!)
        dp.include_router(welcome.router)
        logger.info("✅ welcome зарегистрирован")
        
        dp.include_router(registration.router)
        logger.info("✅ registration зарегистрирован")
        
        dp.include_router(menu.router)
        logger.info("✅ menu зарегистрирован")
        
        dp.include_router(profile.router)
        logger.info("✅ profile зарегистрирован")
        
        dp.include_router(group.router)
        logger.info("✅ group зарегистрирован")
       
        dp.include_router(knowledge.router)
        logger.info("✅ knowledge зарегистрирован")
        
        dp.include_router(edit_aerodrome.router)
        logger.info("✅ edit_aerodrome зарегистрирован")

        dp.include_router(search.router)
        logger.info("✅ search зарегистрирован")

        dp.include_router(admin.router)
        logger.info("✅ admin зарегистрирован")

        dp.include_router(admin_commands.router)  # ← ДОБАВЛЕНО!
        logger.info("✅ admin_commands зарегистрирован")
        
        logger.info("✅ Все роутеры зарегистрированы успешно!")
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта роутеров: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка регистрации роутеров: {e}")
        raise

# ============================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================================

async def main():
    """Основная функция запуска бота"""
    
    logger.info("🚀 Запуск бота...")
    logger.info(f"👤 Запущен от имени: @{(await bot.get_me()).username}")
    
    # Регистрируем роутеры
    setup_routers()
    
    # Генерация ID экземпляра
    instance_id = f"instance_{os.getpid()}_{int(time.time())}"
    logger.info(f"🤖 Запуск экземпляра: {instance_id}")
    
    # Проверка блокировки (для предотвращения дублирования ботов)
    lock_status = db.check_lock_status()
    if lock_status:
        logger.info(f"📊 Текущая блокировка: {lock_status['instance_id']}")
    
    logger.info("🔒 Попытка захвата блокировки...")
    if not db.check_and_acquire_lock(instance_id):
        logger.error("❌ Не удалось захватить блокировку! Другой экземпляр уже работает.")
        return
    
    logger.info("✅ Блокировка успешно захвачена!")
    
    try:
        # Запуск HTTP сервера для health check (Render)
        logger.info("🌐 Запуск HTTP сервера для health check...")
        health_runner = await start_health_server(port=8080)
        
        # Очистка webhook (переключаемся на polling)
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
        else:
            logger.error("❌ Не удалось удалить webhook после 3 попыток")
        
        # Небольшая пауза перед стартом polling
        await asyncio.sleep(5)
        
        # Задача heartbeat для обновления блокировки
        async def heartbeat_task():
            while True:
                try:
                    db.update_heartbeat(instance_id)
                    logger.debug("💓 Heartbeat отправлен")
                except Exception as e:
                    logger.error(f"❌ Ошибка heartbeat: {e}")
                await asyncio.sleep(30)
        
        heartbeat_future = asyncio.create_task(heartbeat_task())
        
        # Разрешённые типы обновлений (оптимизация)
        allowed_updates = dp.resolve_used_update_types()
        logger.info(f"✅ Запускаем polling... (allowed_updates: {allowed_updates})")
        
        # Запуск polling
        await dp.start_polling(bot, allowed_updates=allowed_updates)
        
        # Остановка heartbeat
        heartbeat_future.cancel()
        await health_runner.cleanup()
        
    except KeyboardInterrupt:
        logger.info("⚠️ Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в main: {e}", exc_info=True)
        raise
    finally:
        logger.info("🛑 Остановка бота...")
        try:
            # Освобождаем блокировку
            db.release_lock(instance_id)
            logger.info("🔓 Блокировка освобождена")
            
            # Закрываем сессию бота
            await bot.session.close()
            logger.info("🔌 Сессия бота закрыта")
            
            # Закрываем соединение с БД
            db.close()
            logger.info("🔌 PostgreSQL отключена")
            
            logger.info("✅ Бот полностью остановлен")
        except Exception as e:
            logger.error(f"❌ Ошибка при остановке: {e}", exc_info=True)

# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"💥 Бот завершил работу с ошибкой: {e}", exc_info=True)
        sys.exit(1)
