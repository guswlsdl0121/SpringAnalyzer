"""
클래스 간 관계를 분석하기 위한 모듈
"""
import re

def extract_class_relationships(files_info):
    """
    클래스 간의 관계(의존성, 상속 등) 추출
    """
    relationships = []
    class_map = {}
    
    # 클래스 이름을 파일 정보에 매핑하는 맵 구축
    for file_info in files_info:
        if file_info.get('class_info') and file_info['class_info'].get('name'):
            class_name = file_info['class_info']['name']
            class_map[class_name] = file_info
    
    # 관계 분석
    for source_class, source_info in class_map.items():
        class_info = source_info['class_info']
        
        # 상속 관계 기록
        if class_info.get('extends'):
            parent_class = class_info['extends']
            if parent_class in class_map:
                relationships.append({
                    'source': source_class,
                    'target': parent_class,
                    'type': 'extends'
                })
        
        # 인터페이스 구현 기록
        if class_info.get('implements'):
            for interface in class_info['implements']:
                if interface in class_map:
                    relationships.append({
                        'source': source_class,
                        'target': interface,
                        'type': 'implements'
                    })
        
        # 필드 의존성 분석
        for field in class_info.get('fields', []):
            field_type = field['type'].split('<')[0].strip()  # 제네릭 처리
            if field_type in class_map:
                relationships.append({
                    'source': source_class,
                    'target': field_type,
                    'type': 'has_field'
                })
        
        # 메서드 파라미터와 반환 유형 의존성 분석
        for method in class_info.get('methods', []):
            return_type = method['return_type'].split('<')[0].strip()
            if return_type in class_map:
                relationships.append({
                    'source': source_class,
                    'target': return_type,
                    'type': 'returns'
                })
            
            for param in method.get('parameters', []):
                param_type = param['type'].split('<')[0].strip()
                if param_type in class_map:
                    relationships.append({
                        'source': source_class,
                        'target': param_type,
                        'type': 'uses_param'
                    })
        
        # @Autowired 의존성 찾기
        content = source_info['content']
        for target_class in class_map.keys():
            # 필드나 생성자 파라미터에서 autowired 검색
            if re.search(r'@Autowired[^;]*' + target_class, content):
                relationships.append({
                    'source': source_class,
                    'target': target_class,
                    'type': 'autowires'
                })
    
    return relationships