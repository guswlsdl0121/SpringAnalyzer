import json
import base64
import logging

logger = logging.getLogger('message.receive_callback')

class MessageProcessor:
    def __init__(self, file_service):
        self.file_service = file_service

    def process(self, body):        
        try:
            message = json.loads(body)
            project_id = message.get("projectId")
            
            if not project_id:
                logger.error("프로젝트 ID가 없습니다.")
                return False
            
            file_content = message.get("fileContent")
            
            if not file_content:
                logger.error("파일 내용이 없습니다.")
                return False
            
            file_data = base64.b64decode(file_content)
            
            result = self.file_service.extract_project(project_id, file_data)
            
            if result and result.success:
                logger.info(f"프로젝트 {project_id} 처리 성공: {result.project_dir}")
                return True
            
            error_msg = result.error if result else "알 수 없는 오류"
            logger.error(f"프로젝트 {project_id} 처리 실패: {error_msg}")
            return False
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 디코딩 오류: {str(e)}")
            return False
        
        except Exception as e:
            logger.error(f"예외 발생: {str(e)}", exc_info=True)
            return False
