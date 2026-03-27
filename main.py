#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 main.py — Точка входа Telegram бота
✅ Стабильный запуск с heartbeat для Render
✅ Корректная обработка сигналов остановки
✅ Логирование и отладка
"""

# ============================================================
# ИМПОРТЫ
# ============================================================

import logging
import asyncio
import time
import os
import sys
import signal
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Добавляем путь к проекту для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ============================================================
# ПРОВЕРКА КОНФИГУРАЦИИ
# ============================================================

def check_config() -> bool:
    """
    Проверка необходимых переменных окружения.
    
    Returns:
        bool: True если все переменные заданы, иначе выбрасывает исключение
    """
    errors = []
    
    if not os.getenv("BOT_TOKEN"):
        errors.append("❌ BOT_TOKEN не найден в переменных окружения")
    
    if not os.getenv("DATABASE_URL"):
        errors.append("❌ DATABASE_URL не найден в переменных окружения")
    
    if not os.getenv("YANDEX_DISK_TOKEN"):
        logger.warning("⚠️ YANDEX_DISK_TOKEN не задан (функции Яндекс Диска могут не работать)")
    
    if errors:
        for error in errors:
            logger.error(error)
        raise ValueError("❌ Конфигурация невалидна! Проверьте переменные окружения.")
    
    logger.info("✅ Конфигурация проверена успешно")
    return True

# ============================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# ============================================================

# Инициализация бота и диспетчера (после проверки конфига)
bot: Bot | None = None
dp: Dispatcher | None = None
storage: MemoryStorage | None = None

# ============================================================
# РЕГИСТРАЦИЯ РОУТЕРОВ
# ============================================================

def setup_routers() -> None:
    """
    Импорт и регистрация всех роутеров.
    Порядок импорта важен для корректной работы!
    """
    global dp
    
    if dp is None:
        raise RuntimeError("❌ Dispatcher не инициализирован!")
    
    logger.info("🔍 Начинаем регистрацию handlers...")
    
    try:
        # Импортируем роутеры в правильном порядке
        from handlers import welcome          # 1. Приветствие (/start)
        from handlers import registration     # 2. Регистрация
        from handlers import menu             # 3. Главное меню
        from handlers import profile          # 4. Профиль
        from handlers import group            # 5. Групповые сообщения
        from handlers import knowledge        # 6. Поиск аэродромов и знания
        from handlers import edit_aerodrome   # 7. Редактирование аэродромов
        from handlers import search           # 8. Поиск пользователей (админ)
        from handlers import admin            # 9. Админ функции
        
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
        
        logger.info("✅ Все роутеры зарегистрированы успешно!")
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта роутеров: {e}")
        logger.error(f"💡 Проверьте что все файлы в handlers/ существуют и не содержат синтаксических ошибок")
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка регистрации роутеров: {e}")
        raise

# ============================================================
# ОБРАБОТЧИКИ СИГНАЛОВ
# ============================================================

def setup_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    """
    Настройка обработки сигналов для корректной остановки.
    
    Args:
        loop: Event loop для регистрации обработчиков
    """
    def signal_handler(sig):
        logger.info(f"⚠️ Получен сигнал {sig.name}, начинаем корректную остановку...")
        # Создаем задачу для остановки
        asyncio.create_task(graceful_shutdown())
    
    # Регистрируем обработчики для Unix сигналов
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))
    
    logger.info("✅ Обработчики сигналов настроены")

# ============================================================
# КОРЕКТНАЯ ОСТАНОВКА
# ============================================================

async def graceful_shutdown() -> None:
    """Корректная остановка бота с очисткой ресурсов"""
    global bot, dp, db
    
    logger.info("🛑 Начинаем корректную остановку...")
    
    try:
        # Останавливаем polling
        if dp:
            logger.info("⏹️ Останавливаем polling...")
            await dp.stop_polling()
        
        # Закрываем сессию бота
        if bot:
            logger.info("🔌 Закрываем сессию бота...")
            await bot.session.close()
        
        # Закрываем соединение с БД
        from db_manager import db
        if db:
            logger.info("🔌 Закрываем соединение с БД...")
            db.close()
        
        logger.info("✅ Бот полностью остановлен")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при остановке: {e}", exc_info=True)
    
    # Завершаем event loop
    loop = asyncio.get_running_loop()
    loop.stop()

# ============================================================
# ЗАДАЧА HEARTBEAT ДЛЯ RENDER
# ============================================================

async def heartbeat_task(instance_id: str, interval: int = 30) -> None:
    """
    Периодическое обновление блокировки для предотвращения дублирования.
    
    Args:
        instance_id: Уникальный идентификатор экземпляра бота
        interval: Интервал обновления в секундах
    """
    from db_manager import db
    
    logger.info(f"💓 Heartbeat задача запущена (интервал: {interval}с)")
    
    try:
        while True:
            try:
                db.update_heartbeat(instance_id)
                logger.debug(f"💓 Heartbeat отправлен: {instance_id}")
            except Exception as e:
                logger.error(f"❌ Ошибка heartbeat: {e}")
            
            await asyncio.sleep(interval)
            
    except asyncio.CancelledError:
        logger.info("💓 Heartbeat задача остановлена")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в heartbeat: {e}")

# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================

async def main():
    """Основная функция запуска бота"""
    global bot, dp, storage
    
    logger.info("🚀 Запуск бота...")
    
    # Инициализация бота
    try:
        bot = Bot(
            token=os.getenv("BOT_TOKEN"),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        bot_info = await bot.get_me()
        logger.info(f"👤 Бот запущен: @{bot_info.username} (ID: {bot_info.id})")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации бота: {e}")
        return
    
    # Инициализация хранилища и диспетчера
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация роутеров
    try:
        setup_routers()
    except Exception as e:
        logger.error(f"❌ Не удалось зарегистрировать роутеры: {e}")
        await bot.session.close()
        return
    
    # Генерация уникального ID экземпляра
    instance_id = f"instance_{os.getpid()}_{int(time.time())}"
    logger.info(f"🤖 Экземпляр бота: {instance_id}")
    
    # Проверка и захват блокировки (предотвращение дублирования)
    from db_manager import db
    
    lock_status = db.check_lock_status()
    if lock_status:
        logger.info(f"📊 Текущая блокировка: {lock_status.get('instance_id', 'unknown')}")
    
    logger.info("🔒 Попытка захвата блокировки...")
    if not db.check_and_acquire_lock(instance_id):
        logger.error("❌ Не удалось захватить блокировку! Другой экземпляр уже работает.")
        await bot.session.close()
        return
    
    logger.info("✅ Блокировка успешно захвачена!")
    
    try:
        # Запуск HTTP сервера для health check (Render)
        logger.info("🌐 Запуск HTTP сервера для health check на порту 8080...")
        from health_server import start_health_server
        health_runner = await start_health_server(port=8080)
        
        # Очистка webhook (переключаемся на polling)
        logger.info("🔄 Очистка webhook...")
        for attempt in range(3):
            try:
                await bot.delete_webhook(drop_pending_updates=True)
                logger.info(f"✅ Webhook удалён (попытка {attempt + 1}/3)")
                await asyncio.sleep(2)
                break
            except Exception as e:
                logger.warning(f"⚠️ Попытка {attempt + 1} не удалась: {e}")
                if attempt < 2:
                    await asyncio.sleep(3)
        else:
            logger.error("❌ Не удалось удалить webhook после 3 попыток, продолжаем...")
        
        # Настройка обработки сигналов
        loop = asyncio.get_running_loop()
        setup_signal_handlers(loop)
        
        # Запуск задачи heartbeat
        heartbeat_future = asyncio.create_task(heartbeat_task(instance_id))
        
        # Разрешённые типы обновлений (оптимизация)
        allowed_updates = dp.resolve_used_update_types()
        logger.info(f"✅ Запускаем polling... (allowed_updates: {allowed_updates})")
        
        # Запуск polling (основной цикл бота)
        await dp.start_polling(bot, allowed_updates=allowed_updates)
        
    except asyncio.CancelledError:
        logger.info("⚠️ Polling был отменён")
    except KeyboardInterrupt:
        logger.info("⚠️ Получен сигнал прерывания (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в main: {e}", exc_info=True)
        raise
    finally:
        # Корректная очистка ресурсов
        logger.info("🧹 Очистка ресурсов...")
        
        try:
            # Освобождаем блокировку
            db.release_lock(instance_id)
            logger.info("🔓 Блокировка освобождена")
        except Exception as e:
            logger.error(f"⚠️ Ошибка при освобождении блокировки: {e}")
        
        try:
            # Закрываем сессию бота
            if bot:
                await bot.session.close()
                logger.info("🔌 Сессия бота закрыта")
        except Exception as e:
            logger.error(f"⚠️ Ошибка при закрытии сессии бота: {e}")
        
        try:
            # Закрываем соединение с БД
            db.close()
            logger.info("🔌 PostgreSQL отключена")
        except Exception as e:
            logger.error(f"⚠️ Ошибка при отключении БД: {e}")
        
        logger.info("✅ Бот полностью остановлен")

# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    # Проверяем конфигурацию перед запуском
    try:
        check_config()
    except ValueError as e:
        logger.critical(f"💥 Конфигурация невалидна: {e}")
        sys.exit(1)
    
    # Запускаем бота
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот завершил работу по запросу пользователя")
    except Exception as e:
        logger.critical(f"💥 Бот завершил работу с ошибкой: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("🏁 Процесс завершён")
