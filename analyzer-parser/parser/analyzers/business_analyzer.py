"""
비즈니스 객체 및 로직을 분석하기 위한 모듈
"""
import re
from collections import defaultdict

def find_business_objects(files_info):
    """
    핵심 비즈니스 객체와 그 관계 식별
    """
    business_objects = []
    
    # 엔티티 클래스 찾기
    entities = [f for f in files_info if f.get('file_type') == 'entity']
    
    for entity in entities:
        class_info = entity.get('class_info', {})
        if not class_info:
            continue
            
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
                if '@OneToMany' in prev_lines:
                    field_annotations.append('OneToMany')
                if '@ManyToOne' in prev_lines:
                    field_annotations.append('ManyToOne')
                if '@OneToOne' in prev_lines:
                    field_annotations.append('OneToOne')
                if '@ManyToMany' in prev_lines:
                    field_annotations.append('ManyToMany')
                if '@JoinColumn' in prev_lines:
                    field_annotations.append('JoinColumn')
                
                field['annotations'] = field_annotations
                
                # 가능한 경우 관련 엔티티 결정
                if any(a in ['OneToMany', 'ManyToOne', 'OneToOne', 'ManyToMany'] for a in field_annotations):
                    object_info['relationships'].append({
                        'from': object_info['name'],
                        'to': field['type'].replace('List<', '').replace('>', ''),
                        'type': field_annotations[0] if field_annotations else 'Association',
                        'field': field['name']
                    })
        
        business_objects.append(object_info)
    
    # 주요 DTO도 비즈니스 객체로 간주
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
    
    return business_objects

def extract_business_logic_summary(files_info):
    """
    서비스 클래스에서 비즈니스 로직 요약 추출
    """
    business_logic = {}
    
    # 서비스 클래스 필터링
    service_files = [f for f in files_info if f.get('file_type') == 'service']
    
    for service in service_files:
        service_name = service.get('class_info', {}).get('name', 'Unknown')
        methods = service.get('class_info', {}).get('methods', [])
        
        # 메서드 수준 비즈니스 로직 추출
        logic_methods = []
        
        for method in methods:
            # 생성자와 getter/setter 제외
            if method['name'] == service_name or method['name'].startswith('get') or method['name'].startswith('set'):
                continue
                
            # 메서드 본문 추출 (근사값)
            method_signature = f"{method['access']} {method['return_type']} {method['name']}"
            method_pos = service['content'].find(method_signature)
            
            if method_pos > -1:
                # 메서드 본문 시작점 찾기
                start_pos = service['content'].find('{', method_pos)
                if start_pos > -1:
                    # 괄호 균형 계산으로 메서드 끝 찾기
                    balance = 1
                    end_pos = start_pos + 1
                    
                    while balance > 0 and end_pos < len(service['content']):
                        if service['content'][end_pos] == '{':
                            balance += 1
                        elif service['content'][end_pos] == '}':
                            balance -= 1
                        end_pos += 1
                    
                    method_body = service['content'][start_pos:end_pos].strip()
                    
                    # 업무 로직 추출을 위한 간단한 휴리스틱
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
                    if '@Transactional' in service['content'][:method_pos]:
                        key_operations.append('transactional')
                    
                    logic_methods.append({
                        'name': method['name'],
                        'return_type': method['return_type'],
                        'parameters': method['parameters'],
                        'operations': key_operations,
                        'summary': f"Performs: {', '.join(key_operations)}" if key_operations else "Utility method"
                    })
        
        if logic_methods:
            business_logic[service_name] = logic_methods
    
    return business_logic

def analyze_data_flows(files_info, relationships):
    """
    컨트롤러에서 리포지토리까지의 데이터 흐름 분석
    """
    # 컨트롤러, 서비스, 리포지토리 식별
    controllers = [f for f in files_info if f.get('file_type') == 'controller']
    services = {f.get('class_info', {}).get('name'): f for f in files_info if f.get('file_type') == 'service'}
    repositories = {f.get('class_info', {}).get('name'): f for f in files_info if f.get('file_type') == 'repository'}
    
    # 관계 맵 구성
    relation_map = defaultdict(list)
    for rel in relationships:
        if rel['type'] in ['has_field', 'autowires']:
            relation_map[rel['source']].append(rel['target'])
    
    data_flows = []
    
    for controller in controllers:
        controller_name = controller.get('class_info', {}).get('name', 'Unknown')
        controller_deps = relation_map.get(controller_name, [])
        
        # 엔드포인트별 데이터 흐름 분석
        endpoints = []
        for method in controller.get('class_info', {}).get('methods', []):
            # API 엔드포인트 메서드만 필터링
            if not method['name'].startswith('get') and not method['name'].startswith('set'):
                endpoint_flow = [controller_name]
                
                # 컨트롤러가 의존하는 서비스 찾기
                for service_name in controller_deps:
                    if service_name in services:
                        endpoint_flow.append(service_name)
                        
                        # 서비스가 의존하는 리포지토리 찾기
                        for repo_name in relation_map.get(service_name, []):
                            if repo_name in repositories:
                                endpoint_flow.append(repo_name)
                
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