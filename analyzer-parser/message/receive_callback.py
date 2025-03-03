import logging
from message.operations import MessageOperations
from parser.analysis_generator import analyze_projects
from parser.summary_generator import create_project_summary

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
            
            # 파일 추출 처리
            extraction_result = self.file_service.extract_project(project_id, file_data)
            
            if extraction_result.success:
                # 추출 후 파싱 트리거
                try:
                    # XML 분석 파일 생성
                    parsed_files = analyze_projects(
                        source_dirs=[extraction_result.project_dir], 
                        target_dir=extraction_result.output_dir
                    )
                    
                    # 요약 정보 생성
                    summary_files = create_project_summary(
                        source_dirs=[extraction_result.project_dir], 
                        target_dir=extraction_result.output_dir
                    )
                    
                    # 결과 정보 저장 (여기서는 로깅만 수행)
                    self.logger.info(f"프로젝트 {project_id} 파싱 완료: XML={parsed_files}, 요약={summary_files}")
                    
                    # 여기에 필요한 경우 RabbitMQ를 통해 결과 전송 코드 추가 가능
                    # self.send_analysis_result(project_id, parsed_files, summary_files)
                    
                except Exception as parse_error:
                    self.logger.error(f"프로젝트 파싱 실패: {str(parse_error)}")
                
                return True
            
        except Exception as e:
            self.logger.error(f"메시지 처리 중 예외 발생: {str(e)}", exc_info=True)
            return False