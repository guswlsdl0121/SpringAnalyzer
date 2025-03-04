import logging

logger = logging.getLogger("analyzer.parser.generators.data")

class FullDataGenerator:
    """전체 분석 데이터 생성 클래스"""
    
    def create_full_data(self, project_name, project_info, structure_info, 
                      readme_content, config_info, all_files, relationships, 
                      business_objects, endpoints, business_logic, data_flows,
                      spring_features):
        """전체 분석 데이터 생성"""
        from ..models.full import FullData
        
        full_data = FullData(project_name)
        
        # 기본 정보 설정
        self.set_basic_info(full_data, project_info)
        
        # 아키텍처 정보 설정
        self.set_architecture_info(full_data, structure_info)
        
        # README 설정
        if readme_content:
            full_data.set_readme(readme_content)
        
        # 설정 정보 설정
        full_data.update_configuration(config_info)
        
        # 소스 파일 설정
        for file_info in all_files:
            self.add_source_file(full_data, file_info)
        
        # 엔드포인트 설정
        for endpoint in endpoints:
            self.add_endpoint(full_data, endpoint)
        
        # 비즈니스 객체 설정
        for bo in business_objects:
            self.add_business_object(full_data, bo)
        
        # 관계 설정
        full_data.set_relationships(relationships)
        
        # 비즈니스 로직 설정
        for service, methods in business_logic.items():
            full_data.add_business_logic(service, methods)
        
        # 데이터 흐름 설정
        for flow in data_flows:
            full_data.add_data_flow(flow['controller'], flow.get('endpoints', []))
        
        # Spring 특성 설정
        full_data.set_spring_features(spring_features)
        
        return full_data
    
    def set_basic_info(self, full_data, project_info):
        """기본 프로젝트 정보 설정"""
        full_data.update_basic_info(
            project_info.get('group'),
            project_info.get('version'),
            project_info.get('springBootVersion'),
            project_info.get('javaVersion')
        )
    
    def set_architecture_info(self, full_data, structure_info):
        """아키텍처 정보 설정"""
        # 구성 요소 카운트 계산
        component_counts = {component: len(paths) for component, paths in structure_info.items() if paths}
        
        # 주요 흐름 결정
        typical_flows = []
        if structure_info.get('controllers') and structure_info.get('services'):
            flow = "Controller → Service"
            if structure_info.get('repositories'):
                flow += " → Repository"
            typical_flows.append(flow)
        
        full_data.update_architecture(typical_flows, component_counts)
    
    def add_source_file(self, full_data, file_info):
        """소스 파일 정보 추가"""
        full_data.add_source_file(
            path=file_info['path'],
            package=file_info['package'],
            content=file_info['content'],
            file_type=file_info.get('file_type'),
            class_name=file_info.get('class_info', {}).get('name'),
            complexity=file_info.get('complexity'),
            javadocs=file_info.get('javadocs', []),
            todos=file_info.get('todos', [])
        )
    
    def add_endpoint(self, full_data, endpoint):
        """API 엔드포인트 추가"""
        full_data.add_endpoint(
            method=endpoint['method'],
            path=endpoint['path'],
            handler=endpoint['handler'],
            description=endpoint.get('description'),
            request_params=endpoint.get('requestParams', []),
            request_body=endpoint.get('requestBody'),
            response_type=endpoint.get('responseType')
        )
    
    def add_business_object(self, full_data, business_object):
        """비즈니스 객체 추가"""
        bo_index = len(full_data.domain["businessObjects"])
        
        # 기본 비즈니스 객체 추가
        full_data.add_business_object(
            name=business_object['name'],
            type_name=business_object['type']
        )
        
        # 필드 추가
        for field in business_object.get('fields', []):
            full_data.add_field(
                business_object_index=bo_index,
                name=field['name'],
                type_name=field['type'],
                annotations=field.get('annotations', [])
            )
        
        # 관계 추가
        for rel in business_object.get('relationships', []):
            full_data.add_relationship(
                business_object_index=bo_index,
                from_class=rel['from'],
                to_class=rel['to'],
                type_name=rel['type'],
                field=rel.get('field')
            )