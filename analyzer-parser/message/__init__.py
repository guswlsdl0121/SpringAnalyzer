from file import file_service
from .receive_callback import MessageProcessor

message_processor = MessageProcessor(file_service)

__all__ = ['message_processor']
