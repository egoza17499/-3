import requests
import logging
from config import YANDEX_DISK_TOKEN, YANDEX_DISK_FOLDER

logger = logging.getLogger(__name__)

class YandexDiskClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://cloud-api.yandex.net/v1/disk"  # ✅ Без пробелов!
        self.headers = {"Authorization": f"OAuth {token}"}
    
    def get_file_link(self, file_path):
        """Получить ссылку для скачивания файла"""
        try:
            full_path = f"{YANDEX_DISK_FOLDER}/{file_path}"
            response = requests.get(
                f"{self.base_url}/resources/download",
                headers=self.headers,
                params={"path": full_path}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Получена ссылка на файл: {file_path}")
                return data.get("href")
            else:
                logger.error(f"❌ Ошибка получения ссылки ({response.status_code}): {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка Yandex Disk: {e}")
            return None
    
    def list_files(self):
        """Получить список файлов в папке"""
        try:
            response = requests.get(
                f"{self.base_url}/resources",
                headers=self.headers,
                params={"path": YANDEX_DISK_FOLDER}
            )
            
            if response.status_code == 200:
                data = response.json()
                files = []
                for item in data.get('_embedded', {}).get('items', []):
                    if item['type'] != 'directory':
                        files.append({
                            'name': item['name'],
                            'path': item['path'],
                            'size': item['size']
                        })
                logger.info(f"📁 Найдено файлов: {len(files)}")
                return files
            else:
                logger.error(f"❌ Ошибка получения списка файлов: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка: {e}")
            return []
    
    def file_exists(self, file_name):
        """Проверить существует ли файл"""
        files = self.list_files()
        return any(f['name'].lower() == file_name.lower() for f in files)

# ============================================================
# ГЛОБАЛЬНЫЙ КЛИЕНТ (с проверкой токена!)
# ============================================================

if YANDEX_DISK_TOKEN:
    disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
    logger.info("✅ Yandex Disk клиент инициализирован")
else:
    disk_client = None
    logger.warning("⚠️ YANDEX_DISK_TOKEN не найден!")
