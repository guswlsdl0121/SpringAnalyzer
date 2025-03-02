from .service import FileService
from config import Config

file_service = FileService(Config.TEMP_DIR)

__all__ = ['file_service']