import logging
import re
from collections import defaultdict

logger = logging.getLogger("analyzer.parser.business_analyzer")

class BusinessAnalyzer:
    """비즈니스 객체 및 로직 분석 클래스"""
    
    def find_business_objects(self, files_info):
        """핵심 비즈니스 객체와 그 관계 식별"""
        business_objects = []
        
        # 엔티티 클래스 찾기
        entities = [f for f in files_info if f.get('file_type') == 'entity']
        
        # 엔티티 분석
        for entity in entities:
            business_objects.append(self.analyze_entity(entity))
        
        # 주요 DTO도 비즈니스 객체로 간주
        self.analyze_dtos(files_info, business_objects)
        
        return business_objects
    
    def analyze_entity(self, entity):
        """엔티티 분석 및 관계 추출"""
        class_info = entity.get('class_info', {})
        if not class_info:
            return None
            
        object_info = {
            'name': class_info.get('name', 'Unknown'),
            'type': 'Entity',
            'fields': class_info.get('fields', []),
            'relationships': []
        }
        
        # JPA 관계 어노테이션 찾기
        for field in object_info['fields']:
            field_annotations = []
            field_pattern = field['name'] + r'\s*;'
            field_pos = entity['content'].find(field['name'])
            if field_pos > -1:
                # 필드 앞의 3줄에서 어노테이션 찾기
                prev_lines = entity['content'][max(0, field_pos-200):field_pos]
                
                # 어노테이션 검색
                for annotation in ['OneToMany', 'ManyToOne', 'OneToOne', 'ManyToMany', 'JoinColumn']:
                    if f'@{annotation}' in prev_lines:
                        field_annotations.append(annotation)
                
                field['annotations'] = field_annotations
                
                # 가능한 경우 관련 엔티티 결정
                if any(a in ['OneToMany', 'ManyToOne', 'OneToOne', 'ManyToMany'] for a in field_annotations):
                    object_info['relationships'].append({
                        'from': object_info['name'],
                        'to': field['type'].replace('List<', '').replace('>', ''),
                        'type': field_annotations[0] if field_annotations else 'Association',
                        'field': field['name']
                    })
        
        return object_info
    
    def analyze_dtos(self, files_info, business_objects):
        """DTO 분석 및 비즈니스 객체 추가"""
        dtos = [f for f in files_info if f.get('file_type') == 'dto' or 
                (f.get('path', '').lower().find('dto') > -1)]
        
        for dto in dtos:
            class_info = dto.get('class_info', {})
            if not class_info:
                continue
                
            object_info = {
                'name': class_info.get('name', 'Unknown'),
                'type': 'DTO',
                'fields': class_info.get('fields', []),
                'relationships': []
            }
            
            business_objects.append(object_info)
    
    def extract_logic(self, files_info):
        """서비스 클래스에서 비즈니스 로직 요약 추출"""
        business_logic = {}
        
        # 서비스 클래스 필터링
        service_files = [f for f in files_info if f.get('file_type') == 'service']
        
        for service in service_files:
            service_name = service.get('class_info', {}).get('name', 'Unknown')
            methods = service.get('class_info', {}).get('methods', [])
            
            # 메서드 수준 비즈니스 로직 추출
            logic_methods = self.analyze_service_methods(service, methods)
            
            if logic_methods:
                business_logic[service_name] = logic_methods
        
        return business_logic
    
    def analyze_service_methods(self, service, methods):
        """서비스 메서드 분석"""
        logic_methods = []
        service_name = service.get('class_info', {}).get('name', 'Unknown')
        
        for method in methods:
            # 생성자와 getter/setter 제외
            if method['name'] == service_name or method['name'].startswith('get') or method['name'].startswith('set'):
                continue
                
            # 메서드 본문 추출 (근사값)
            method_signature = f"{method['access']} {method['return_type']} {method['name']}"
            method_pos = service['content'].find(method_signature)
            
            if method_pos > -1:
                method_body = self.extract_method_body(service['content'], method_pos)
                key_operations = self.identify_key_operations(method_body, service['content'], method_pos)
                
                logic_methods.append({
                    'name': method['name'],
                    'return_type': method['return_type'],
                    'parameters': method['parameters'],
                    'operations': key_operations,
                    'summary': f"Performs: {', '.join(key_operations)}" if key_operations else "Utility method"
                })
        
        return logic_methods
    
    def extract_method_body(self, content, method_pos):
        """메서드 본문 추출"""
        # 메서드 본문 시작점 찾기
        start_pos = content.find('{', method_pos)
        if start_pos == -1:
            return ""
            
        # 괄호 균형 계산으로 메서드 끝 찾기
        balance = 1
        end_pos = start_pos + 1
        
        while balance > 0 and end_pos < len(content):
            if content[end_pos] == '{':
                balance += 1
            elif content[end_pos] == '}':
                balance -= 1
            end_pos += 1
        
        return content[start_pos:end_pos].strip()
    
    def identify_key_operations(self, method_body, full_content, method_pos):
        """업무 로직 추출을 위한 휴리스틱"""
        key_operations = []
        
        # DB 조회/저장 작업
        if 'repository.find' in method_body or 'repository.save' in method_body:
            key_operations.append('data_access')
        
        # 데이터 변환 작업
        if '.stream().map(' in method_body or '.builder()' in method_body:
            key_operations.append('data_transformation')
        
        # 비즈니스 룰 검증
        if 'if' in method_body and ('throw' in method_body or 'Exception' in method_body):
            key_operations.append('business_rule_validation')
        
        # 트랜잭션 존재 여부
        if '@Transactional' in full_content[:method_pos]:
            key_operations.append('transactional')
        
        return key_operations
    
    def analyze_flows(self, files_info, relationships):
        """컨트롤러에서 리포지토리까지의 데이터 흐름 분석"""
        # 컨트롤러, 서비스, 리포지토리 식별
        controllers = [f for f in files_info if f.get('file_type') == 'controller']
        services = {f.get('class_info', {}).get('name'): f for f in files_info if f.get('file_type') == 'service'}
        repositories = {f.get('class_info', {}).get('name'): f for f in files_info if f.get('file_type') == 'repository'}
        
        # 관계 맵 구성
        relation_map = self.build_relation_map(relationships)
        
        # 컨트롤러별 데이터 흐름 분석
        data_flows = self.analyze_controller_flows(controllers, relation_map, services, repositories)
        
        return data_flows
    
    def build_relation_map(self, relationships):
        """관계 맵 구성"""
        relation_map = defaultdict(list)
        for rel in relationships:
            if rel['type'] in ['has_field', 'autowires']:
                relation_map[rel['source']].append(rel['target'])
        return relation_map
    
    def analyze_controller_flows(self, controllers, relation_map, services, repositories):
        """컨트롤러별 데이터 흐름 분석"""
        data_flows = []
        
        for controller in controllers:
            controller_name = controller.get('class_info', {}).get('name', 'Unknown')
            controller_deps = relation_map.get(controller_name, [])
            
            # 엔드포인트별 데이터 흐름 분석
            endpoints = []
            for method in controller.get('class_info', {}).get('methods', []):
                # API 엔드포인트 메서드만 필터링 (getter/setter 제외)
                if not method['name'].startswith('get') and not method['name'].startswith('set'):
                    endpoint_flow = self.trace_endpoint_flow(controller_name, controller_deps, services, repositories, relation_map)
                    
                    if len(endpoint_flow) > 1:  # 컨트롤러보다 더 많은 컴포넌트가 있을 때만
                        endpoints.append({
                            'method': method['name'],
                            'flow': ' → '.join(endpoint_flow)
                        })
            
            if endpoints:
                data_flows.append({
                    'controller': controller_name,
                    'endpoints': endpoints
                })
        
        return data_flows
    
    def trace_endpoint_flow(self, controller_name, controller_deps, services, repositories, relation_map):
        """엔드포인트 흐름 추적"""
        endpoint_flow = [controller_name]
        
        # 컨트롤러가 의존하는 서비스 찾기
        for service_name in controller_deps:
            if service_name in services:
                endpoint_flow.append(service_name)
                
                # 서비스가 의존하는 리포지토리 찾기
                for repo_name in relation_map.get(service_name, []):
                    if repo_name in repositories:
                        endpoint_flow.append(repo_name)
        
        return endpoint_flow
    
    def analyze_spring_features(self, files_info):
        """Spring Boot 특화 기능 및 패턴 분석"""
        spring_features = {
            'auto_configuration': [],
            'dependency_injection_patterns': [],
            'profiles': [],
            'properties_usage': [],
            'exception_handling': []
        }
        
        # Java 파일 분석
        for file in files_info:
            if file.get('file_type') not in ['controller', 'service', 'repository', 'config', 'entity']:
                continue
                
            content = file.get('content', '')
            class_name = file.get('class_info', {}).get('name', 'Unknown')
            
            # 자동 구성 감지
            if '@EnableAutoConfiguration' in content or '@SpringBootApplication' in content:
                spring_features['auto_configuration'].append(file.get('path'))
            
            # 의존성 주입 패턴 감지
            self.detect_di_patterns(content, class_name, spring_features)
            
            # 프로필 사용 감지
            self.detect_profiles(content, class_name, spring_features)
            
            # 프로퍼티 사용 감지
            self.detect_properties(content, class_name, spring_features)
            
            # 예외 처리 패턴 감지
            self.detect_exception_handling(content, class_name, spring_features)
        
        return spring_features
    
    def detect_di_patterns(self, content, class_name, spring_features):
        """의존성 주입 패턴 감지"""
        di_patterns = {
            'constructor': '@Autowired' in content and 'public ' + class_name in content,
            'field': re.search(r'@Autowired\s+private', content) is not None,
            'setter': re.search(r'@Autowired\s+(?:public|protected|private)\s+void\s+set', content) is not None
        }
        
        if any(di_patterns.values()):
            spring_features['dependency_injection_patterns'].append({
                'class': class_name,
                'patterns': [k for k, v in di_patterns.items() if v]
            })
    
    def detect_profiles(self, content, class_name, spring_features):
        """프로필 사용 감지"""
        if '@Profile' in content:
            profiles = re.findall(r'@Profile\(["\']([^"\']+)["\']\)', content)
            if profiles:
                spring_features['profiles'].append({
                    'class': class_name,
                    'profiles': profiles
                })
    
    def detect_properties(self, content, class_name, spring_features):
        """프로퍼티 사용 감지"""
        if '@Value' in content:
            properties = re.findall(r'@Value\(["\'](\$\{[^"\']+\})["\']', content)
            if properties:
                spring_features['properties_usage'].append({
                    'class': class_name,
                    'properties': properties
                })
    
    def detect_exception_handling(self, content, class_name, spring_features):
        """예외 처리 패턴 감지"""
        if '@ExceptionHandler' in content or '@ControllerAdvice' in content:
            spring_features['exception_handling'].append({
                'class': class_name,
                'global': '@ControllerAdvice' in content
            })