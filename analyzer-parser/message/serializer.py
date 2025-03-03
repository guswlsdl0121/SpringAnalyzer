import logging
import json
import base64
import os
from pathlib import Path

class MessageSerializer:    
    @staticmethod
    def parse_and_validate(body):
        logger = logging.getLogger("analyzer.messaging.serializer")
        
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
    
    @staticmethod
    def create_result_message(project_id, analysis_file_path, summary_file_path, files_processed=0):
        """분석 결과 메시지 생성"""
        logger = logging.getLogger("analyzer.messaging.serializer")
        
        try:
            # 분석 파일 읽기 및 Base64 인코딩
            analysis_content = None
            if analysis_file_path and os.path.exists(analysis_file_path):
                with open(analysis_file_path, 'r', encoding='utf-8') as f:
                    analysis_data = f.read()
                    analysis_content = base64.b64encode(analysis_data.encode('utf-8')).decode('utf-8')
            
            # 요약 파일 읽기 및 Base64 인코딩
            summary_content = None
            if summary_file_path and os.path.exists(summary_file_path):
                with open(summary_file_path, 'r', encoding='utf-8') as f:
                    summary_data = f.read()
                    summary_content = base64.b64encode(summary_data.encode('utf-8')).decode('utf-8')
            
            # 메시지 생성
            message = {
                "projectId": project_id,
                "success": True,
                "analysisContent": analysis_content,
                "summaryContent": summary_content,
                "filesProcessed": files_processed
            }
            
            return json.dumps(message)
            
        except Exception as e:
            logger.error(f"결과 메시지 생성 중 오류: {str(e)}", exc_info=True)
            
            # 오류 발생 시 오류 메시지 반환
            error_message = {
                "projectId": project_id,
                "success": False,
                "error": f"결과 메시지 생성 실패: {str(e)}"
            }
            
            return json.dumps(error_message)
    
    @staticmethod
    def create_error_message(project_id, error_message):
        """오류 메시지 생성"""
        return json.dumps({
            "projectId": project_id,
            "success": False,
            "error": error_message
        })