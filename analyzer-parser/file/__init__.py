from .service import FileService
from config import Config

# FileService 초기화
file_service = FileService(Config.TEMP_DIR)

__all__ = ['file_service']