import logging
from datetime import datetime
from pathlib import Path

from .file_collector import FileCollector
from .analyzers.java_analyzer import JavaAnalyzer
from .analyzers.build_analyzer import BuildAnalyzer
from .analyzers.config_analyzer import ConfigAnalyzer
from .analyzers.structure_analyzer import StructureAnalyzer
from .analyzers.endpoint_analyzer import EndpointAnalyzer
from .analyzers.business_analyzer import BusinessAnalyzer
from .analyzers.relationship_analyzer import RelationshipAnalyzer
from .generators.summary_generator import SummaryGenerator
from .generators.data_generator import FullDataGenerator

logger = logging.getLogger("analyzer.parser.process")

class ParserProcess:
    """파싱 프로세스 전체 조율 클래스"""
    
    def __init__(self):
        self.file_collector = FileCollector()
        self.java_analyzer = JavaAnalyzer()
        self.build_analyzer = BuildAnalyzer()
        self.config_analyzer = ConfigAnalyzer()
        self.structure_analyzer = StructureAnalyzer()
        self.endpoint_analyzer = EndpointAnalyzer()
        self.business_analyzer = BusinessAnalyzer()
        self.relationship_analyzer = RelationshipAnalyzer()
        self.summary_generator = SummaryGenerator()
        self.data_generator = FullDataGenerator()
    
    def process_project(self, source_dir, output_dir):
        """전체 파싱 프로세스 실행"""
        try:
            # 1. 파일 수집
            files_info, readme_content = self.file_collector.collect_files(source_dir)
            
            # 2. 기본 프로젝트 정보 분석
            project_name = Path(source_dir).name
            structure_info = self.structure_analyzer.analyze(source_dir)
            
            # 3. 빌드 파일 분석
            build_files = [f for f in files_info if f['file_type'] == 'build']
            project_info = self.build_analyzer.analyze(build_files)
            
            # 4. 설정 파일 분석
            config_files = [f for f in files_info if f['file_type'] == 'config']
            config_info = self.config_analyzer.analyze(config_files)
            
            # 5. Java 파일 상세 분석
            java_files = [f for f in files_info if f['path'].endswith('.java')]
            analyzed_java_files = self.java_analyzer.analyze_all(java_files)
            
            # 6. 모든 분석 파일 합치기
            all_files = [f for f in files_info if not f['path'].endswith('.java')]
            all_files.extend(analyzed_java_files)
            
            # 7. 고급 분석 
            relationships = self.relationship_analyzer.analyze(analyzed_java_files)
            business_objects = self.business_analyzer.find_business_objects(analyzed_java_files)
            endpoints = self.endpoint_analyzer.analyze(analyzed_java_files)
            business_logic = self.business_analyzer.extract_logic(analyzed_java_files)
            data_flows = self.business_analyzer.analyze_flows(analyzed_java_files, relationships)
            spring_features = self.business_analyzer.analyze_spring_features(analyzed_java_files)
            
            # 8. 결과 데이터 생성
            full_data = self.data_generator.create_full_data(
                project_name, project_info, structure_info, readme_content,
                config_info, all_files, relationships, business_objects,
                endpoints, business_logic, data_flows, spring_features
            )
            
            # 9. 요약 데이터 생성
            summary_data = self.summary_generator.generate(
                project_name, project_info, structure_info, 
                endpoints, business_objects, analyzed_java_files
            )
            
            # 10. 결과 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            analysis_filename = f"{timestamp}-{project_name}-analysis.json"
            summary_filename = f"{timestamp}-{project_name}-summary.json"
            
            analysis_path = Path(output_dir) / analysis_filename
            summary_path = Path(output_dir) / summary_filename
            
            full_data.save_to_file(analysis_path)
            summary_data.save_to_file(summary_path)
            
            return {
                'success': True,
                'analysis_file': str(analysis_path),
                'summary_file': str(summary_path),
                'files_processed': len(all_files)
            }
            
        except Exception as e:
            logger.error(f"프로젝트 파싱 실패: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"파싱 오류: {str(e)}"
            }