# handler/__init__.py
from file import file_service
from .handler import MessageHandler

message_handler = MessageHandler(file_service)

__all__ = ['message_handler']
