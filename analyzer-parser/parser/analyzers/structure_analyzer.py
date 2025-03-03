"""
Spring Boot 프로젝트 구조를 분석하기 위한 모듈
"""
from pathlib import Path

def analyze_project_structure(source_dir):
    """
    어노테이션을 기반으로 Spring Boot 프로젝트 구조 분석
    """
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
            if '@Controller' in content or '@RestController' in content:
                structure['controllers'].append(str(relative_path))
            elif '@Service' in content:
                structure['services'].append(str(relative_path))
            elif '@Repository' in content:
                structure['repositories'].append(str(relative_path))
            elif '@Entity' in content:
                structure['entities'].append(str(relative_path))
            elif '@Configuration' in content:
                structure['configs'].append(str(relative_path))
            elif '@Aspect' in content:
                structure['aspects'].append(str(relative_path))
            elif 'HandlerInterceptor' in content:
                structure['interceptors'].append(str(relative_path))
            elif path.name.endswith('DTO.java') or path.name.endswith('Dto.java') or 'dto' in str(relative_path).lower():
                structure['dtos'].append(str(relative_path))
            elif path.name.endswith('Exception.java') or 'exception' in str(relative_path).lower():
                structure['exceptions'].append(str(relative_path))
            elif path.name.endswith('Model.java') or 'model' in str(relative_path).lower():
                structure['models'].append(str(relative_path))
            elif path.name.endswith('Util.java') or path.name.endswith('Utils.java') or 'util' in str(relative_path).lower():
                structure['utils'].append(str(relative_path))
            elif '@Test' in content:
                structure['tests'].append(str(relative_path))
        except Exception as e:
            print(f"File analysis error {path}: {str(e)}")
            continue
    
    return structure