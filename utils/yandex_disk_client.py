import requests
import logging
from config import YANDEX_DISK_TOKEN, YANDEX_DISK_FOLDER

logger = logging.getLogger(__name__)

class YandexDiskClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {"Authorization": f"OAuth {token}"}
    
    def get_file_link(self, file_path):
        """Получить ссылку для скачивания файла"""
        try:
            full_path = f"{YANDEX_DISK_FOLDER}/{file_path}"
            
            # Пробуем получить прямую ссылку через API
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
                    logger.info(f"✅ Получена прямая ссылка на файл: {file_path}")
                    return direct_link
            
            logger.warning(f"⚠️ Прямая ссылка не доступна, пробуем публичную...")
            
            # Пробуем получить публичную ссылку
            response = requests.get(
                f"{self.base_url}/resources",
                headers=self.headers,
                params={"path": full_path},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                public_url = data.get("public_url")
                if public_url:
                    logger.info(f"✅ Получена публичная ссылка: {public_url}")
                    return public_url
            
            logger.error(f"❌ Не удалось получить ссылку на файл: {file_path}")
            return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Тайм-аут при запросе к Yandex Disk для файла: {file_path}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка запроса к Yandex Disk: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Неизвестная ошибка Yandex Disk: {e}")
            return None
    
    def list_files(self):
        """Получить список файлов в папке"""
        try:
            response = requests.get(
                f"{self.base_url}/resources",
                headers=self.headers,
                params={
                    "path": YANDEX_DISK_FOLDER,
                    "limit": 100
                },
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
                logger.info(f"📁 Найдено файлов: {len(files)}")
                return files
            else:
                logger.error(f"❌ Ошибка получения списка файлов ({response.status_code}): {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("❌ Тайм-аут при получении списка файлов")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка запроса списка файлов: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Неизвестная ошибка при получении списка: {e}")
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
