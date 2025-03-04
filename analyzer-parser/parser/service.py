import logging
from pathlib import Path
from .process import ParserProcess

class ParserService:
    """프로젝트 분석을 담당하는 서비스 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger("analyzer.parser.service")
        self.parser_process = ParserProcess()
    
    def analyze_project(self, project_id, source_dir, output_dir):
        """프로젝트 파일 분석 수행"""
        try:
            # 출력 디렉토리 생성
            target_dir = Path(output_dir)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 파싱 프로세스 실행
            result = self.parser_process.process_project(source_dir, output_dir)
            
            if result['success']:
                self.logger.info(f"프로젝트 {project_id} 파싱 완료: JSON={result['analysis_file']}, 요약={result['summary_file']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"프로젝트 파싱 실패: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"파싱 오류: {str(e)}"
            }