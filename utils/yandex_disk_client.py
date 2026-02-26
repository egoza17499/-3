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
            
            logger.error(f"❌ Не удалось получить ссылку на файл: {file_path}")
            return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Тайм-аут при получении ссылки: {file_path}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка запроса: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Неизвестная ошибка: {e}")
            return None
    
    def download_file(self, file_path):
        """Скачать файл в память (bytes)"""
        try:
            # Сначала получаем ссылку для скачивания
            download_url = self.get_file_link(file_path)
            
            if not download_url:
                logger.error(f"❌ Не удалось получить ссылку для скачивания: {file_path}")
                return None
            
            # Скачиваем файл по ссылке
            response = requests.get(download_url, timeout=30)
            
            if response.status_code == 200:
                file_size = len(response.content)
                logger.info(f"✅ Файл скачан: {file_path} ({file_size} байт)")
                return response.content
            else:
                logger.error(f"❌ Ошибка скачивания файла ({response.status_code}): {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Тайм-аут при скачивании файла: {file_path}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка запроса при скачивании: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Неизвестная ошибка при скачивании: {e}")
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
        try:
            files = self.list_files()
            return any(f['name'].lower() == file_name.lower() for f in files)
        except Exception as e:
            logger.error(f"❌ Ошибка проверки существования файла: {e}")
            return False
    
    def get_file_info(self, file_name):
        """Получить информацию о файле"""
        try:
            files = self.list_files()
            for f in files:
                if f['name'].lower() == file_name.lower():
                    return f
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о файле: {e}")
            return None

# ============================================================
# ГЛОБАЛЬНЫЙ КЛИЕНТ (с проверкой токена!)
# ============================================================

if YANDEX_DISK_TOKEN:
    disk_client = YandexDiskClient(YANDEX_DISK_TOKEN)
    logger.info("✅ Yandex Disk клиент инициализирован")
else:
    disk_client = None
    logger.warning("⚠️ YANDEX_DISK_TOKEN не найден!")
