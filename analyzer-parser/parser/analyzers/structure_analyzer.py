import logging
from pathlib import Path

logger = logging.getLogger("analyzer.parser.structure_analyzer")

class StructureAnalyzer:
    """프로젝트 구조 분석 클래스"""
    
    def analyze(self, source_dir):
        """어노테이션을 기반으로 Spring Boot 프로젝트 구조 분석"""
        structure = {
            'controllers': [],     # @Controller, @RestController
            'services': [],        # @Service
            'repositories': [],    # @Repository
            'entities': [],        # @Entity
            'configs': [],         # @Configuration
            'dtos': [],            # Data Transfer Objects
            'models': [],          # Model classes
            'utils': [],           # Utility classes
            'aspects': [],         # @Aspect
            'interceptors': [],    # HandlerInterceptor implementations
            'exceptions': [],      # Exception classes
            'tests': []            # @Test
        }
        
        source = Path(source_dir)
        for path in source.rglob("*.java"):
            try:
                relative_path = path.relative_to(source)
                content = path.read_text(encoding='utf-8', errors='ignore')
                
                # Spring 어노테이션 및 명명 규칙에 기반한 분류
                self.classify_file(structure, str(relative_path), content)
                
            except Exception as e:
                logger.error(f"파일 분석 오류 {path}: {str(e)}")
        
        return structure
    
    def classify_file(self, structure, relative_path, content):
        """파일 내용 및 경로를 기반으로 분류"""
        if '@Controller' in content or '@RestController' in content:
            structure['controllers'].append(relative_path)
        elif '@Service' in content:
            structure['services'].append(relative_path)
        elif '@Repository' in content:
            structure['repositories'].append(relative_path)
        elif '@Entity' in content:
            structure['entities'].append(relative_path)
        elif '@Configuration' in content:
            structure['configs'].append(relative_path)
        elif '@Aspect' in content:
            structure['aspects'].append(relative_path)
        elif 'HandlerInterceptor' in content:
            structure['interceptors'].append(relative_path)
        elif relative_path.endswith('DTO.java') or relative_path.endswith('Dto.java') or 'dto' in relative_path.lower():
            structure['dtos'].append(relative_path)
        elif relative_path.endswith('Exception.java') or 'exception' in relative_path.lower():
            structure['exceptions'].append(relative_path)
        elif relative_path.endswith('Model.java') or 'model' in relative_path.lower():
            structure['models'].append(relative_path)
        elif relative_path.endswith('Util.java') or relative_path.endswith('Utils.java') or 'util' in relative_path.lower():
            structure['utils'].append(relative_path)
        elif '@Test' in content:
            structure['tests'].append(relative_path)