import logging
import re

logger = logging.getLogger("analyzer.parser.relationship_analyzer")

class RelationshipAnalyzer:
    """클래스 관계 분석 클래스"""
    
    def analyze(self, files_info):
        """클래스 간의 관계(의존성, 상속 등) 추출"""
        relationships = []
        class_map = {}
        
        # 클래스 이름을 파일 정보에 매핑하는 맵 구축
        self.build_class_map(files_info, class_map)
        
        # 관계 분석
        self.analyze_relationships(class_map, relationships)
        
        return relationships
    
    def build_class_map(self, files_info, class_map):
        """클래스 이름과 파일 매핑"""
        for file_info in files_info:
            if file_info.get('class_info') and file_info['class_info'].get('name'):
                class_name = file_info['class_info']['name']
                class_map[class_name] = file_info
    
    def analyze_relationships(self, class_map, relationships):
        """모든 클래스 관계 분석"""
        for source_class, source_info in class_map.items():
            class_info = source_info['class_info']
            
            # 상속 관계 분석
            self.analyze_inheritance(relationships, source_class, class_info, class_map)
            
            # 필드 의존성 분석
            self.analyze_field_dependencies(relationships, source_class, class_info, class_map)
            
            # 메서드 파라미터와 반환 유형 의존성 분석
            self.analyze_method_dependencies(relationships, source_class, class_info, class_map)
            
            # @Autowired 의존성 분석
            self.analyze_autowired_dependencies(relationships, source_class, source_info, class_map)
    
    def analyze_inheritance(self, relationships, source_class, class_info, class_map):
        """상속 및 인터페이스 구현 관계 분석"""
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
    
    def analyze_field_dependencies(self, relationships, source_class, class_info, class_map):
        """필드 의존성 분석"""
        for field in class_info.get('fields', []):
            field_type = field['type'].split('<')[0].strip()  # 제네릭 처리
            if field_type in class_map:
                relationships.append({
                    'source': source_class,
                    'target': field_type,
                    'type': 'has_field'
                })
    
    def analyze_method_dependencies(self, relationships, source_class, class_info, class_map):
        """메서드 파라미터와 반환 유형 의존성 분석"""
        for method in class_info.get('methods', []):
            # 반환 유형 분석
            return_type = method['return_type'].split('<')[0].strip()
            if return_type in class_map:
                relationships.append({
                    'source': source_class,
                    'target': return_type,
                    'type': 'returns'
                })
            
            # 파라미터 유형 분석
            for param in method.get('parameters', []):
                param_type = param['type'].split('<')[0].strip()
                if param_type in class_map:
                    relationships.append({
                        'source': source_class,
                        'target': param_type,
                        'type': 'uses_param'
                    })
    
    def analyze_autowired_dependencies(self, relationships, source_class, source_info, class_map):
        """@Autowired 의존성 분석"""
        content = source_info['content']
        for target_class in class_map.keys():
            # 필드나 생성자 파라미터에서 autowired 검색
            if re.search(r'@Autowired[^;]*' + target_class, content):
                relationships.append({
                    'source': source_class,
                    'target': target_class,
                    'type': 'autowires'
                })