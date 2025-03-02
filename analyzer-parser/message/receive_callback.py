import logging
from operations import MessageOperations

logger = logging.getLogger('message.receive_callback')

class MessageProcessor:
    """메시지 처리를 담당하는 서비스 클래스"""
    
    def __init__(self, file_service):
        self.file_service = file_service
        self.logger = logging.getLogger("analyzer.messaging.processor")
    
    def process(self, body):
        try:
            self.logger.info("메시지 처리 시작")
            
            # 메시지 파싱 및 검증
            project_id, file_data = MessageOperations.parse_and_validate(body)
            if not project_id or not file_data:
                return False
            
            # 파일 처리 요청
            result = self.file_service.extract_project(project_id, file_data)
            
            if result and result.success:
                self.logger.info(f"프로젝트 {project_id} 처리 성공: {result.project_dir}")
                return True
            
        except Exception as e:
            self.logger.error(f"메시지 처리 중 예외 발생: {str(e)}", exc_info=True)
            return False