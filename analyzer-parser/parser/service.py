# parser/service.py
import os
import logging
from parser.manager.analysis_manager import analyze_projects
from parser.manager.summary_manager import create_project_summary

class ParserService:
    """프로젝트 분석을 담당하는 서비스 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger("analyzer.parser.service")
    
    def analyze_project(self, project_id, source_dir, output_dir):
        """
        프로젝트 파일 분석 수행
        """
        try:
            # XML 분석 파일 생성
            parsed_files = analyze_projects(
                source_dirs=[source_dir], 
                target_dir=output_dir
            )
            
            # 요약 정보 생성
            summary_files = create_project_summary(
                source_dirs=[source_dir], 
                target_dir=output_dir
            )
            
            # 결과 정보 로깅
            self.logger.info(f"프로젝트 {project_id} 파싱 완료: XML={parsed_files}, 요약={summary_files}")
            
            # 결과 파일 경로 구성
            analysis_file_path = None
            if parsed_files and len(parsed_files) > 0:
                analysis_file_path = os.path.join(output_dir, parsed_files[0])
            
            summary_file_path = None
            if summary_files and len(summary_files) > 0:
                summary_file_path = os.path.join(output_dir, summary_files[0])
            
            return {
                'success': True,
                'analysis_file': analysis_file_path,
                'summary_file': summary_file_path,
                'files_processed': len(parsed_files)
            }
                
        except Exception as parse_error:
            self.logger.error(f"프로젝트 파싱 실패: {str(parse_error)}", exc_info=True)
            return {
                'success': False,
                'error': f"파싱 오류: {str(parse_error)}"
            }