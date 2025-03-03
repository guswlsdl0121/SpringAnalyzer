import logging
from message.serializer import MessageSerializer

class MessageUtils:
    """메시지 처리 유틸리티"""
    
    @staticmethod
    def validate_message(body):
        """메시지 유효성 검증"""
        logger = logging.getLogger("analyzer.utils.message")
        project_id, file_data = MessageSerializer.parse_and_validate(body)
        if not project_id or not file_data:
            logger.warning("유효하지 않은 메시지 형식")
            return None, None
        return project_id, file_data