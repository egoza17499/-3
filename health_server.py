# health_server.py - HTTP сервер для health check (Render)
from aiohttp import web
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint для Render"""
    return web.json_response({
        'status': 'ok',
        'service': 'telegram-bot',
        'timestamp': str(datetime.now())
    })

async def index(request):
    """Главная страница"""
    return web.json_response({
        'message': 'Telegram Bot is running',
        'endpoints': {
            'health': '/health',
        }
    })

def create_app():
    """Создание веб-приложения"""
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/health', health_check)
    return app

async def start_health_server(port=8080):
    """Запуск HTTP сервера для health check"""
    try:
        app = create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        logger.info(f"✅ HTTP сервер запущен на порту {port}")
        logger.info(f"📊 Health check: http://localhost:{port}/health")
        
        return runner
    except Exception as e:
        logger.error(f"❌ Ошибка запуска HTTP сервера: {e}")
        raise
