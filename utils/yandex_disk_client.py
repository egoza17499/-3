import aiohttp
import logging
from config import YANDEX_DISK_TOKEN, YANDEX_DISK_FOLDER

logger = logging.getLogger(__name__)

class YandexDiskClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {"Authorization": f"OAuth {token}"}
    
    def _get_full_path(self, path: str) -> str:
        """
        Возвращает полный путь.
        Если путь начинается с /Il-76 или / — используем как есть (папки в корне).
        Иначе добавляем YANDEX_DISK_FOLDER.
        """
        if path.startswith(('/Il-76', '/')):
            return path
        return f"{YANDEX_DISK_FOLDER}/{path}".replace('//', '/')
    
    async def get_file_link(self, file_path: str):
        """Получить ссылку для скачивания файла (async)"""
        try:
            full_path = self._get_full_path(file_path)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/resources/download",
                    headers=self.headers,
                    params={"path": full_path},
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        direct_link = data.get("href")
                        if direct_link:
                            logger.info(f"✅ Получена ссылка на файл: {file_path}")
                            return direct_link
                    logger.error(f"❌ Не удалось получить ссылку: {file_path} (status: {response.status})")
                    return None
        except Exception as e:
            logger.error(f"❌ Ошибка get_file_link: {e}")
            return None
    
    async def download_file(self, file_path: str):
        """Скачать файл в память (async)"""
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
        """Получить список файлов в папке (async)"""
        try:
            path = self._get_full_path(folder_path) if folder_path else YANDEX_DISK_FOLDER
            
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
                                    'path': item['path'],
                                    'size': item.get('size', 0)
                                })
                        logger.info(f"📁 Найдено файлов в {path}: {len(files)}")
                        return files
                    else:
                        logger.error(f"❌ Ошибка list_files: {response.status} — {await response.text()}")
                        return []
        except Exception as e:
            logger.error(f"❌ Ошибка list_files: {e}")
            return []

# Глобальный клиент
if YANDEX_DISK_TOKEN:
    disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
    logger.info("✅ Yandex Disk клиент инициализирован")
else:
    disk_client = None
    logger.warning("⚠️ YANDEX_DISK_TOKEN не найден!")
