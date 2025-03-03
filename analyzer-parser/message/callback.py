# message/processor.py
import logging
from .util import MessageUtils
from worker import worker_pool

class MessageProcessor:
    """메시지 처리를 담당하는 서비스 클래스"""
    
    def __init__(self, file_service, parser_service, result_dispatcher):
        self.file_service = file_service
        self.parser_service = parser_service
        self.result_dispatcher = result_dispatcher
        self.logger = logging.getLogger("analyzer.messaging.processor")
    
    def on_message(self, body):
        """
        메시지 처리의 진입점
        """
        project_id = None
        try:
            self.logger.info("메시지 처리 시작")
            
            # 1. 메시지 검증
            project_id, file_data = MessageUtils.validate_message(body)
            if not project_id:
                return False
            
            # 작업자 풀에 작업 제출
            worker_pool.submit(
                project_id,
                self._process_message,
                project_id,
                file_data
            )
            
            # 메시지는 성공적으로 받았으므로 True 반환
            return True
            
        except Exception as e:
            self.logger.error(f"메시지 처리 중 예외 발생: {str(e)}", exc_info=True)
            if project_id:
                self.result_dispatcher.publish_error(project_id, f"처리 오류: {str(e)}")
            return False
    
    def _process_message(self, project_id, file_data):
        """작업자 풀에서 실행될 실제 처리 로직"""
        try:
            # 2. 프로젝트 추출
            extraction_result = self.file_service.extract_project(project_id, file_data)
            if not extraction_result.success:
                self.result_dispatcher.publish_error(project_id, extraction_result.error)
                return False
            
            # 3. 프로젝트 분석
            analysis_result = self.parser_service.analyze_project(
                project_id, 
                extraction_result.project_dir, 
                extraction_result.output_dir
            )
            
            # 4. 결과 발행
            if analysis_result['success']:
                self.result_dispatcher.publish_success(project_id, analysis_result)
                return True
            else:
                self.result_dispatcher.publish_error(project_id, analysis_result['error'])
                return False
                
        except Exception as e:
            self.logger.error(f"작업 처리 중 예외 발생: {str(e)}", exc_info=True)
            self.result_dispatcher.publish_error(project_id, f"처리 오류: {str(e)}")
            return False