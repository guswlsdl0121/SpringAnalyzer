import logging
from ..models.summary import SummaryData

logger = logging.getLogger("analyzer.parser.generators.summary")

class SummaryGenerator:
    """요약 데이터 생성 클래스"""
    
    def generate(self, project_name, project_info, structure_info, endpoints, business_objects, java_files):
        """요약 데이터 생성"""
        summary = SummaryData(project_name)
        
        # 빌드 정보 업데이트
        summary.update_build_info(
            project_info.get('group'),
            project_info.get('version'),
            project_info.get('springBootVersion'),
            project_info.get('javaVersion')
        )
        
        # 컴포넌트 카운트 업데이트
        component_counts = {component: len(paths) for component, paths in structure_info.items() if paths}
        summary.update_component_counts(component_counts)
        
        # 의존성 정보 업데이트
        summary.update_dependencies(project_info.get('dependencies', []))
        
        # API 엔드포인트 추가
        for endpoint in endpoints:
            summary.add_api_endpoint(endpoint['method'], endpoint['path'])
        
        # 비즈니스 객체 추가
        for bo in business_objects:
            summary.add_business_object(bo['name'])
        
        # Java 파일 메트릭 추가
        for java_file in java_files:
            complexity = java_file.get('complexity', {})
            if complexity:
                summary.add_java_file_metrics(
                    method_count=complexity.get('methods', 0),
                    cyclomatic_complexity=complexity.get('cyclomatic', 0),
                    file_path=java_file['path']
                )
        
        return summary