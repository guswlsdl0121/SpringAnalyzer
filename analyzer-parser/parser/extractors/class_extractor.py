"""
Java 클래스 정보를 추출하기 위한 모듈
"""
import re

def extract_class_info(content):
    """
    상속 및 인터페이스를 포함한 종합적인 클래스 정보 추출
    """
    class_info = {}
    
    # 일반 클래스/인터페이스/열거형 매칭 시도
    class_match = re.search(r'(public|private|protected)?\s*(class|interface|enum|@interface)\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w\s,]+))?', content)
    
    if class_match:
        class_info['access'] = class_match.group(1) if class_match.group(1) else "default"
        class_info['type'] = class_match.group(2)
        class_info['name'] = class_match.group(3)
        
        if class_match.group(4):  # extends
            class_info['extends'] = class_match.group(4)
        
        if class_match.group(5):  # implements
            interfaces = [i.strip() for i in class_match.group(5).split(',')]
            class_info['implements'] = interfaces
    else:
        # 레코드 선언 매칭 시도
        record_match = re.search(r'(public|private|protected)?\s*record\s+(\w+)\s*\((.*?)\)(?:\s+implements\s+([\w\s,]+))?', content)
        if record_match:
            class_info['access'] = record_match.group(1) if record_match.group(1) else "default"
            class_info['type'] = 'record'
            class_info['name'] = record_match.group(2)
            
            # 필드로서의 레코드 컴포넌트 추출
            fields = []
            if record_match.group(3):
                components = record_match.group(3).split(',')
                for component in components:
                    component = component.strip()
                    if component:
                        parts = component.split()
                        if len(parts) >= 2:
                            field_type = ' '.join(parts[:-1])
                            field_name = parts[-1]
                            fields.append({
                                'access': 'private final',  # 레코드는 private final 필드를 가짐
                                'type': field_type,
                                'name': field_name
                            })
            
            class_info['fields'] = fields
            
            if record_match.group(4):  # implements
                interfaces = [i.strip() for i in record_match.group(4).split(',')]
                class_info['implements'] = interfaces
    
    # 클래스나 레코드를 찾지 못한 경우 빈 정보 반환
    if not class_info:
        return {}
    
    # 일반 클래스의 경우 필드 추출
    if class_info.get('type') != 'record':
        # 필드 추출
        fields = []
        field_pattern = r'(public|private|protected)?\s+(?:static\s+)?(?:final\s+)?([\w<>\[\]]+)\s+(\w+)\s*(?:=\s*[^;]+)?;'
        for match in re.finditer(field_pattern, content):
            field = {
                'access': match.group(1) if match.group(1) else "default",
                'type': match.group(2),
                'name': match.group(3)
            }
            fields.append(field)
        
        class_info['fields'] = fields
    
    # 반환 유형 및 매개변수가 있는 메서드 추출
    methods = []
    method_pattern = r'(public|private|protected)?\s+(?:static\s+)?(?:final\s+)?([\w<>\[\]]+)\s+(\w+)\s*\((.*?)\)\s*(?:throws\s+[\w,\s]+)?\s*(\{|\;)'
    for match in re.finditer(method_pattern, content):
        # 매개변수 추출
        params = []
        if match.group(4):
            param_text = match.group(4)
            param_entries = [p.strip() for p in param_text.split(',') if p.strip()]
            for param in param_entries:
                param_parts = param.split()
                if len(param_parts) >= 2:
                    param_type = ' '.join(param_parts[:-1])
                    param_name = param_parts[-1]
                    params.append({'type': param_type, 'name': param_name})
        
        method = {
            'access': match.group(1) if match.group(1) else "default",
            'return_type': match.group(2),
            'name': match.group(3),
            'parameters': params,
            'is_implementation': False
        }
        
        # 인터페이스 메서드 구현인지 확인
        if class_info.get('implements'):
            # 이는 단순화된 확인 - 보다 정확한 구현은 실제 인터페이스 정의를 확인해야 함
            method['is_implementation'] = True
        
        methods.append(method)
    
    class_info['methods'] = methods
    
    # 클래스 레벨의 어노테이션 추출
    annotations = []
    annotation_pattern = r'@(\w+)(?:\([^)]*\))?'
    for match in re.finditer(annotation_pattern, content):
        annotations.append(match.group(1))
    
    class_info['annotations'] = annotations
    
    return class_info

def determine_file_type(path, content):
    """
    Java 파일의 유형 결정 (컨트롤러, 서비스, 리포지토리 등)
    """
    # 확장자 기반 기본 분류
    if path.endswith('.java'):
        # 패턴 기반 상세 분류
        if 'Controller' in path and ('@Controller' in content or '@RestController' in content):
            return 'controller'
        elif 'Service' in path and '@Service' in content:
            return 'service'
        elif 'Repository' in path and '@Repository' in content:
            return 'repository'
        elif '@Entity' in content:
            return 'entity'
        elif '@Configuration' in content:
            return 'config'
        # DTO 식별 로직 개선
        elif ('DTO' in path or 'Dto' in path or 'dto' in path.lower() or 
              'Request' in path or 'Response' in path or 'record' in content.lower()):
            return 'dto'
        # 더 많은 패턴 추가
        elif 'Mapper' in path:
            return 'mapper'
        elif 'Util' in path or 'Utils' in path:
            return 'util'
        # 기본 패키지 구조 기반 분류
        elif '.domain.' in path.lower():
            return 'domain'
        elif '.dto.' in path.lower():
            return 'dto'
    
    return None