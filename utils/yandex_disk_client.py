import requests
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
        Возвращает полный путь с учётом YANDEX_DISK_FOLDER.
        Если путь начинается с /Il-76 или /Blocks — используем как есть.
        """
        # Если путь уже абсолютный (папка самолета или Blocks) — не добавляем префикс
        if path.startswith(('/Il-76', '/Blocks', '/')):
            return path
        # Иначе добавляем базовую папку
        return f"{YANDEX_DISK_FOLDER}/{path}".replace('//', '/')
    
    def get_file_link(self, file_path):
        """Получить ссылку для скачивания файла"""
        try:
            full_path = self._get_full_path(file_path)
            
            response = requests.get(
                f"{self.base_url}/resources/download",
                headers=self.headers,
                params={"path": full_path},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                direct_link = data.get("href")
                if direct_link:
                    logger.info(f"✅ Получена ссылка на файл: {file_path}")
                    return direct_link
            
            logger.error(f"❌ Не удалось получить ссылку: {file_path} (status: {response.status_code})")
            return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка get_file_link: {e}")
            return None
    
    def download_file(self, file_path):
        """Скачать файл в память (bytes)"""
        try:
            download_url = self.get_file_link(file_path)
            if not download_url:
                return None
            
            response = requests.get(download_url, timeout=30)
            if response.status_code == 200:
                logger.info(f"✅ Файл скачан: {file_path} ({len(response.content)} байт)")
                return response.content
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка download_file: {e}")
            return None
    
    def list_files(self, folder_path=None):
        """Получить список файлов в папке"""
        try:
            path = self._get_full_path(folder_path) if folder_path else YANDEX_DISK_FOLDER
            
            response = requests.get(
                f"{self.base_url}/resources",
                headers=self.headers,
                params={"path": path, "limit": 100},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
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
            logger.error(f"❌ Ошибка list_files: {response.status_code}")
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
