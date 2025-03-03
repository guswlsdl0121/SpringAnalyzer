import os
import logging
from message.serializer import MessageSerializer
from parser.analysis_generator import analyze_projects
from parser.summary_generator import create_project_summary
from config import Config

class MessageProcessor:
    """메시지 처리를 담당하는 서비스 클래스"""
    
    def __init__(self, file_service, rabbitmq_service=None):
        self.file_service = file_service
        self.rabbitmq_service = rabbitmq_service
        self.logger = logging.getLogger("analyzer.messaging.processor")
    
    def set_rabbitmq_service(self, rabbitmq_service):
        """RabbitMQ 서비스 설정 (순환 참조 방지)"""
        self.rabbitmq_service = rabbitmq_service
    
    def process(self, body):
        try:
            self.logger.info("메시지 처리 시작")
            
            # 메시지 파싱 및 검증
            project_id, file_data = MessageSerializer.parse_and_validate(body)
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
                    
                    # 결과 정보 저장
                    self.logger.info(f"프로젝트 {project_id} 파싱 완료: XML={parsed_files}, 요약={summary_files}")
                    
                    # 분석 결과 파일 경로 구성
                    analysis_file_path = None
                    if parsed_files and len(parsed_files) > 0:
                        analysis_file_path = os.path.join(extraction_result.output_dir, parsed_files[0])
                    
                    summary_file_path = None
                    if summary_files and len(summary_files) > 0:
                        summary_file_path = os.path.join(extraction_result.output_dir, summary_files[0])
                    
                    # 결과 메시지 생성 및 전송
                    if self.rabbitmq_service and self.rabbitmq_service.publisher:
                        result_message = MessageSerializer.create_result_message(
                            project_id, 
                            analysis_file_path, 
                            summary_file_path, 
                            len(parsed_files)
                        )
                        
                        self.rabbitmq_service.publisher.publish_result(
                            Config.ROUTING_RESULT_COMPLETED,
                            result_message
                        )
                        
                        self.logger.info(f"프로젝트 {project_id} 분석 결과 전송 완료")
                    
                    return True
                    
                except Exception as parse_error:
                    self.logger.error(f"프로젝트 파싱 실패: {str(parse_error)}", exc_info=True)
                    
                    # 오류 메시지 전송
                    if self.rabbitmq_service and self.rabbitmq_service.publisher:
                        error_message = MessageSerializer.create_error_message(
                            project_id, 
                            f"파싱 오류: {str(parse_error)}"
                        )
                        
                        self.rabbitmq_service.publisher.publish_result(
                            Config.ROUTING_RESULT_ERROR,
                            error_message
                        )
                        
                        self.logger.info(f"프로젝트 {project_id} 오류 결과 전송 완료")
                    
                    return False
            else:
                # 파일 추출 실패 메시지 전송
                if self.rabbitmq_service and self.rabbitmq_service.publisher:
                    error_message = MessageSerializer.create_error_message(
                        project_id, 
                        extraction_result.error
                    )
                    
                    self.rabbitmq_service.publisher.publish_result(
                        Config.ROUTING_RESULT_ERROR,
                        error_message
                    )
                    
                    self.logger.info(f"프로젝트 {project_id} 오류 결과 전송 완료")
                
                return False
            
        except Exception as e:
            self.logger.error(f"메시지 처리 중 예외 발생: {str(e)}", exc_info=True)
            return False