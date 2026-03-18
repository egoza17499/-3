import aiohttp
import logging
from config import YANDEX_DISK_TOKEN, YANDEX_DISK_FOLDER

logger = logging.getLogger(__name__)

class YandexDiskClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {"Authorization": f"OAuth {token}"}
    
    async def get_file_link(self, file_path: str):
        """Получить ссылку для скачивания файла"""
        try:
            # Убираем "disk:/" если есть и начинаем с /
            if file_path.startswith("disk:/"):
                file_path = file_path.replace("disk:/", "/")
            elif not file_path.startswith("/"):
                file_path = "/" + file_path
            
            logger.info(f"🔗 Запрос ссылки для файла: {file_path}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/resources/download",
                    headers=self.headers,
                    params={"path": file_path},
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        download_url = data.get("href")
                        logger.info(f"✅ Получена ссылка для {file_path}")
                        return download_url
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Ошибка {response.status}: {error_text} для пути {file_path}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка get_file_link: {e}")
            return None
    
    async def download_file(self, file_path: str):
        """Скачать файл в память"""
        try:
            download_url = await self.get_file_link(file_path)
            if not download_url:
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        logger.info(f"✅ Файл скачан: {file_path} ({len(content)} байт)")
                        return content
                    return None
        except Exception as e:
            logger.error(f"❌ Ошибка download_file: {e}")
            return None
    
    async def list_files(self, folder_path: str = None):
        """Получить список файлов в папке"""
        try:
            # Формируем правильный путь
            if folder_path:
                if folder_path.startswith("disk:/"):
                    path = folder_path.replace("disk:/", "/")
                elif not folder_path.startswith("/"):
                    path = "/" + folder_path
                else:
                    path = folder_path
            else:
                path = YANDEX_DISK_FOLDER if YANDEX_DISK_FOLDER else "/"
            
            logger.info(f"📁 Запрос списка файлов из: {path}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/resources",
                    headers=self.headers,
                    params={"path": path, "limit": 100},
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        files = []
                        for item in data.get('_embedded', {}).get('items', []):
                            if item['type'] != 'directory':
                                files.append({
                                    'name': item['name'],
                                    'path': item['path'],  # Это уже полный путь от API
                                    'size': item.get('size', 0)
                                })
                        logger.info(f"✅ Найдено файлов в {path}: {len(files)}")
                        return files
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Ошибка {response.status} при получении списка: {error_text}")
                        return []
        except Exception as e:
            logger.error(f"❌ Ошибка list_files: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

# Глобальный клиент
if YANDEX_DISK_TOKEN:
    disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
    logger.info("✅ Yandex Disk клиент инициализирован")
else:
    disk_client = None
    logger.warning("⚠️ YANDEX_DISK_TOKEN не найден!")
