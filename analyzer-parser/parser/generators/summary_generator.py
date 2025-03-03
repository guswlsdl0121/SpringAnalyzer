"""
프로젝트 분석 결과에서 요약을 생성하기 위한 모듈
"""
import re
from collections import defaultdict

def extract_architecture_summary(files_info):
    """
    분석된 정보에서 고수준 아키텍처 요약 생성
    """
    # 유형별 구성 요소 수 계산
    component_counts = defaultdict(int)
    for file in files_info:
        if file.get('file_type'):
            component_counts[file.get('file_type')] += 1
    
    # 주요 데이터 흐름 식별
    typical_flows = []
    if component_counts.get('controller', 0) > 0 and component_counts.get('service', 0) > 0:
        flow = "Controller → Service"
        if component_counts.get('repository', 0) > 0:
            flow += " → Repository"
        typical_flows.append(flow)
    
    # 공통 횡단 관심사 식별
    cross_cutting = []
    if component_counts.get('aspect', 0) > 0:
        cross_cutting.append("Aspect-Oriented Programming (AOP)")
    if component_counts.get('interceptor', 0) > 0:
        cross_cutting.append("Interceptors")
    if any('config' in f['path'].lower() for f in files_info if 'path' in f):
        cross_cutting.append("Centralized Configuration")
    
    summary = {
        'component_counts': dict(component_counts),
        'typical_flows': typical_flows,
        'cross_cutting_concerns': cross_cutting
    }
    
    return summary

def analyze_spring_boot_features(files_info):
    """
    Spring Boot 특화 기능 및 패턴 분석
    """
    spring_features = {
        'auto_configuration': [],
        'dependency_injection_patterns': [],
        'profiles': [],
        'properties_usage': [],
        'exception_handling': []
    }
    
    # 모든 Java 파일 순회
    for file in files_info:
        if file.get('file_type') not in ['controller', 'service', 'repository', 'config', 'entity']:
            continue
            
        content = file.get('content', '')
        
        # 자동 구성 감지
        if '@EnableAutoConfiguration' in content or '@SpringBootApplication' in content:
            spring_features['auto_configuration'].append(file.get('path'))
        
        # 의존성 주입 패턴 감지
        di_patterns = {
            'constructor': '@Autowired' in content and 'public ' + file.get('class_info', {}).get('name', '') in content,
            'field': re.search(r'@Autowired\s+private', content) is not None,
            'setter': re.search(r'@Autowired\s+(?:public|protected|private)\s+void\s+set', content) is not None
        }
        
        if any(di_patterns.values()):
            spring_features['dependency_injection_patterns'].append({
                'class': file.get('class_info', {}).get('name', 'Unknown'),
                'patterns': [k for k, v in di_patterns.items() if v]
            })
        
        # 프로필 사용 감지
        if '@Profile' in content:
            profiles = re.findall(r'@Profile\(["\']([^"\']+)["\']\)', content)
            if profiles:
                spring_features['profiles'].append({
                    'class': file.get('class_info', {}).get('name', 'Unknown'),
                    'profiles': profiles
                })
        
        # 프로퍼티 사용 감지
        if '@Value' in content:
            properties = re.findall(r'@Value\(["\'](\$\{[^"\']+\})["\']', content)
            if properties:
                spring_features['properties_usage'].append({
                    'class': file.get('class_info', {}).get('name', 'Unknown'),
                    'properties': properties
                })
        
        # 예외 처리 패턴 감지
        if '@ExceptionHandler' in content or '@ControllerAdvice' in content:
            spring_features['exception_handling'].append({
                'class': file.get('class_info', {}).get('name', 'Unknown'),
                'global': '@ControllerAdvice' in content
            })
    
    return spring_features