# message/publisher.py
import logging
from config import Config
from message.serializer import MessageSerializer

class ReulstDispatcher:
    """분석 결과 발행을 담당하는 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger("analyzer.message.publisher")
        self._publisher = None
    
    def _get_publisher(self):        
        if not self._publisher:
            from rabbitmq import publish_result
            self._publisher = publish_result
        return self._publisher
    
    def publish_success(self, project_id, analysis_result):
        """성공 결과 발행"""
        publisher = self._get_publisher()
        message = MessageSerializer.create_result_message(
            project_id, 
            analysis_result['analysis_file'], 
            analysis_result['summary_file'], 
            analysis_result['files_processed']
        )
        publisher(Config.ROUTING_RESULT_COMPLETED, message)
        self.logger.info(f"프로젝트 {project_id} 분석 결과 전송 완료")
    
    def publish_error(self, project_id, error_message):
        """오류 결과 발행"""
        publisher = self._get_publisher()
        message = MessageSerializer.create_error_message(project_id, error_message)
        publisher(Config.ROUTING_RESULT_ERROR, message)
        self.logger.info(f"프로젝트 {project_id} 오류 결과 전송 완료")