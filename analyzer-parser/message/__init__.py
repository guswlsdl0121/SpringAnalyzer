# message/__init__.py
from file import file_service
from parser import parser_service
from .callback import MessageProcessor
from .dispatcher import ReulstDispatcher

# 서비스 인스턴스 생성
result_dispatcher = ReulstDispatcher()
message_processor = MessageProcessor(file_service, parser_service, result_dispatcher)

__all__ = ['message_processor']