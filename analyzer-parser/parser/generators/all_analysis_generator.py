"""
분석 결과에서 JSON 출력을 생성하기 위한 모듈
"""
from pathlib import Path
from parser.models.analysis_result import (
    ProjectAnalysisResult, ProjectSummaryData, BasicInfo, Architecture,
    ApiData, EndpointData, DomainData, BusinessObjectData, FieldData,
    RelationshipData, DataFlow, EndpointFlow, BusinessLogicMethod, SourceFile
)

def generate_json_output(output_path, project_name, project_info, architecture_summary, 
                       endpoints, business_objects, readme_content, structure_info,
                       relationships, business_logic, data_flows, spring_features,
                       config_info, files_info):
    """
    분석 결과를 모델 객체로 변환하고 JSON 형식으로 출력 파일에 작성
    """
    # 기본 정보 설정
    basic_info = BasicInfo(
        group=project_info.get('group', 'N/A'),
        version=project_info.get('version', 'N/A'),
        springBootVersion=project_info.get('springBootVersion', 'N/A'),
        javaVersion=project_info.get('javaVersion', 'N/A')
    )
    
    # 아키텍처 정보 설정
    architecture = Architecture(
        typicalFlows=architecture_summary.get('typical_flows', []),
        componentCounts=architecture_summary.get('component_counts', {})
    )
    
    # 프로젝트 요약 설정
    project_summary = ProjectSummaryData(
        name=project_name,
        basicInfo=basic_info,
        architecture=architecture,
        readme=readme_content
    )
    
    # API 엔드포인트 설정
    api_data = ApiData(endpoints=[])
    for endpoint in endpoints:
        endpoint_obj = EndpointData(
            method=endpoint['method'],
            path=endpoint['path'],
            handler=endpoint['handler'],
            description=endpoint.get('description'),
            requestParams=endpoint.get('requestParams', []),
            requestBody=endpoint.get('requestBody'),
            responseType=endpoint.get('responseType')
        )
        api_data.endpoints.append(endpoint_obj)
    
    # 도메인 객체 설정
    domain_data = DomainData(businessObjects=[])
    for obj in business_objects:
        fields = []
        for field in obj.get('fields', []):
            field_obj = FieldData(
                name=field['name'],
                type=field['type'],
                annotations=field.get('annotations', [])
            )
            fields.append(field_obj)
        
        rel_objects = []
        for rel in obj.get('relationships', []):
            rel_obj = RelationshipData(
                fromClass=rel['from'],
                toClass=rel['to'],
                type=rel['type'],
                field=rel.get('field')
            )
            rel_objects.append(rel_obj)
        
        business_obj = BusinessObjectData(
            name=obj['name'],
            type=obj['type'],
            fields=fields,
            relationships=rel_objects
        )
        domain_data.businessObjects.append(business_obj)
    
    # 데이터 흐름 설정
    data_flow_list = []
    for flow in data_flows:
        endpoint_flows = []
        for endpoint in flow.get('endpoints', []):
            endpoint_flow = EndpointFlow(
                method=endpoint['method'],
                flow=endpoint['flow']
            )
            endpoint_flows.append(endpoint_flow)
        
        data_flow = DataFlow(
            controller=flow['controller'],
            endpoints=endpoint_flows
        )
        data_flow_list.append(data_flow)
    
    # 비즈니스 로직 설정
    business_logic_dict = {}
    for service, methods in business_logic.items():
        method_list = []
        for method in methods:
            method_obj = BusinessLogicMethod(
                name=method['name'],
                summary=method['summary']
            )
            method_list.append(method_obj)
        business_logic_dict[service] = method_list
    
    # 소스 파일 설정
    source_files = []
    for file_info in sorted(files_info, key=lambda x: x['path']):
        if 'test' not in file_info['path'].lower():
            class_name = None
            if file_info.get('class_info') and file_info['class_info'].get('name'):
                class_name = file_info['class_info']['name']
                
            source_file = SourceFile(
                path=file_info['path'],
                package=file_info['package'],
                content=file_info['content'],
                fileType=file_info.get('file_type'),
                className=class_name,
                complexity=file_info.get('complexity'),
                javadocs=file_info.get('javadocs', []),
                todos=file_info.get('todos', [])
            )
            source_files.append(source_file)
    
    # 분석 결과 객체 생성
    analysis_result = ProjectAnalysisResult(
        projectSummary=project_summary,
        api=api_data,
        domain=domain_data,
        projectStructure=structure_info,
        relationships=relationships,
        businessLogic=business_logic_dict,
        dataFlows=data_flow_list,
        springFeatures=spring_features,
        configuration=config_info,
        sourceFiles=source_files
    )
    
    # JSON 파일로 저장
    analysis_result.save_to_file(output_path)
    
    return Path(output_path).name