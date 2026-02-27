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
        from handlers import welcome
        from handlers import registration
        from handlers import menu
        from handlers import profile
        from handlers import group
        from handlers import knowledge
        from handlers import edit_aerodrome
        from handlers import admin
        from handlers import search
        
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
    
    # ========================================================================
    # 🔥 ВРЕМЕННЫЙ КОД - ВЫПОЛНЕНИЕ SQL С КЛИКАБЕЛЬНЫМИ НОМЕРАМИ
    # ========================================================================
    try:
        logger.info("="*70)
        logger.info("🔄 ВЫПОЛНЯЮ SQL С КЛИКАБЕЛЬНЫМИ НОМЕРАМИ ТЕЛЕФОНОВ...")
        logger.info("📄 Файл: complete_aerodromes_clickable.sql")
        logger.info("="*70)
        
        import psycopg2
        
        # Читаем SQL файл
        with open('complete_aerodromes_clickable.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        logger.info("📄 SQL файл прочитан")
        
        # Подключаемся к БД
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        logger.info("🔌 Подключение к базе данных...")
        
        # Выполняем SQL
        cursor.execute(sql_script)
        conn.commit()
        
        # Проверяем результат
        cursor.execute("SELECT COUNT(*) FROM aerodromes")
        aerodromes_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM aerodrome_phones")
        phones_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info("="*70)
        logger.info("✅ SQL ВЫПОЛНЕН УСПЕШНО!")
        logger.info("="*70)
        logger.info(f"📊 Аэродромов: {aerodromes_count}")
        logger.info(f"📱 Телефонов: {phones_count}")
        logger.info("📞 Все номера теперь кликабельные!")
        logger.info("="*70)
        
    except FileNotFoundError:
        logger.warning("⚠️  Файл complete_aerodromes_clickable.sql не найден - пропускаю")
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении SQL: {e}")
        logger.info("⚠️  Продолжаю запуск бота несмотря на ошибку...")
    # ========================================================================
    
    # Генерация ID экземпляра
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
        # Запуск HTTP сервера для health check
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
        else:
            logger.error("❌ Не удалось удалить webhook после 3 попыток")
        
        await asyncio.sleep(5)
        
        # Heartbeat task
        async def heartbeat_task():
            while True:
                try:
                    db.update_heartbeat(instance_id)
                    logger.debug("💓 Heartbeat отправлен")
                except Exception as e:
                    logger.error(f"❌ Ошибка heartbeat: {e}")
                await asyncio.sleep(30)
        
        heartbeat_future = asyncio.create_task(heartbeat_task())
        
        allowed_updates = dp.resolve_used_update_types()
        logger.info(f"✅ Запускаем polling... (allowed_updates: {allowed_updates})")
        
        await dp.start_polling(bot, allowed_updates=allowed_updates)
        
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
            db.release_lock(instance_id)
            logger.info("🔓 Блокировка освобождена")
            await bot.session.close()
            logger.info("🔌 Сессия бота закрыта")
            db.close()
            logger.info("🔌 PostgreSQL отключена")
            logger.info("✅ Бот полностью остановлен")
        except Exception as e:
            logger.error(f"❌ Ошибка при остановке: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"💥 Бот завершил работу с ошибкой: {e}", exc_info=True)
        sys.exit(1)
