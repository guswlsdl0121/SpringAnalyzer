import logging
import json
import base64

class MessageOperations:    
    @staticmethod
    def parse_and_validate(body):
        logger = logging.getLogger("analyzer.messaging.parser")
        
        try:
            # 메시지 JSON 파싱
            try:
                message = json.loads(body)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 디코딩 오류: {str(e)}")
                return None, None
            
            # 필수 필드 검증
            project_id = message.get("projectId")
            if not project_id:
                logger.error("프로젝트 ID가 없습니다.")
                return None, None
            
            file_content = message.get("fileContent")
            if not file_content:
                logger.error("파일 내용이 없습니다.")
                return None, None
            
            # Base64 디코딩
            try:
                file_data = base64.b64decode(file_content)
                return project_id, file_data
            except Exception as e:
                logger.error(f"Base64 디코딩 오류: {str(e)}")
                return None, None
                
        except Exception as e:
            logger.error(f"메시지 파싱/검증 중 예외 발생: {str(e)}", exc_info=True)
            return None, None