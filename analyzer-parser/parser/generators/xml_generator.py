"""
분석 결과에서 XML 출력을 생성하기 위한 모듈
"""
from datetime import datetime

def generate_xml_output(output_path, project_name, project_info, architecture_summary, 
                       endpoints, business_objects, readme_content, structure_info,
                       relationships, business_logic, data_flows, spring_features,
                       config_info, files_info):
    """
    분석 결과를 XML 형식으로 출력 파일에 작성
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<documents>\n')
        f.write('<document index="1">\n')
        f.write(f'<source>{output_path.name}</source>\n')
        f.write('<document_content>\n\n')
        
        # 프로젝트 요약 섹션
        f.write('<project_summary>\n')
        f.write(f"# Spring Boot Service Analysis Report - {project_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 프로젝트 기본 정보
        f.write("## Basic Information\n")
        if project_info.get('group'):
            f.write(f"Group: {project_info.get('group')}\n")
        if project_info.get('version'):
            f.write(f"Version: {project_info.get('version')}\n")
        if project_info.get('springBootVersion'):
            f.write(f"Spring Boot Version: {project_info.get('springBootVersion')}\n")
        if project_info.get('javaVersion'):
            f.write(f"Java Version: {project_info.get('javaVersion')}\n")
        f.write("\n")
        
        # 아키텍처 개요        
        if architecture_summary.get('typical_flows'):
            f.write("Typical Data Flows:\n")
            for flow in architecture_summary['typical_flows']:
                f.write(f"- {flow}\n")
            f.write("\n")
        
        if architecture_summary.get('component_counts'):
            f.write("Component Distribution:\n")
            for component, count in architecture_summary['component_counts'].items():
                f.write(f"- {component.capitalize()}: {count}\n")
            f.write("\n")
        
        # API
        if endpoints:
            f.write("## API Endpoints\n")
            for endpoint in endpoints:
                f.write(f"### {endpoint['method']} {endpoint['path']}\n")
                f.write(f"Handler: `{endpoint['handler']}`\n")
                
                if endpoint.get('description'):
                    f.write(f"Description: {endpoint['description']}\n")
                
                if endpoint.get('requestParams'):
                    f.write("Request Parameters:\n")
                    for param in endpoint['requestParams']:
                        f.write(f"- {param}\n")
                
                if endpoint.get('requestBody'):
                    f.write(f"Request Body: `{endpoint['requestBody']}`\n")
                
                if endpoint.get('responseType'):
                    f.write(f"Response Type: `{endpoint['responseType']}`\n")
                
                f.write("\n")
        
        # 비즈니스 객체
        if business_objects:
            f.write("## Key Business Objects\n")
            for obj in business_objects:
                f.write(f"### {obj['name']} ({obj['type']})\n")
                
                if obj.get('fields'):
                    f.write("Fields:\n")
                    for field in obj['fields']:
                        annotations = ""
                        if field.get('annotations'):
                            annotations = f" [{', '.join(field['annotations'])}]"
                        f.write(f"- {field['name']}: {field['type']}{annotations}\n")
                
                if obj.get('relationships'):
                    f.write("Relationships:\n")
                    for rel in obj['relationships']:
                        f.write(f"- {rel['type']} {rel['to']} via {rel['field']}\n")
                
                f.write("\n")
        
        # README 내용 (이용 가능한 경우)
        if readme_content:
            f.write("## Project README\n")
            f.write(readme_content)
            f.write("\n")
        
        f.write('</project_summary>\n\n')
        
        # 프로젝트 구조 섹션
        f.write('<project_structure>\n')
        for component, paths in structure_info.items():
            if paths:
                f.write(f"<{component}>\n")
                for path in paths:
                    f.write(f"- {path}\n")
                f.write(f"</{component}>\n\n")
        f.write('</project_structure>\n\n')
        
        # 클래스 관계
        f.write('<class_relationships>\n')
        for rel in relationships:
            f.write(f"- {rel['source']} {rel['type']} {rel['target']}\n")
        f.write('</class_relationships>\n\n')
        
        # 비즈니스 로직 요약
        f.write('<business_logic_summary>\n')
        for service, methods in business_logic.items():
            f.write(f"### {service}\n")
            for method in methods:
                f.write(f"- {method['name']}: {method['summary']}\n")
        f.write('</business_logic_summary>\n\n')
        
        # 데이터 흐름
        f.write('<data_flows>\n')
        for flow in data_flows:
            f.write(f"### Controller: {flow['controller']}\n")
            for endpoint in flow['endpoints']:
                f.write(f"- {endpoint['method']}: {endpoint['flow']}\n")
        f.write('</data_flows>\n\n')
        
        # Spring Boot 특화 기능
        f.write('<spring_boot_features>\n')
        for feature, items in spring_features.items():
            if items:
                f.write(f"### {feature.replace('_', ' ').title()}\n")
                for item in items:
                    f.write(f"- {str(item)}\n")
        f.write('</spring_boot_features>\n\n')
        
        # 구성 요약
        if config_info:
            f.write('<configuration>\n')
            for key, value in config_info.items():
                f.write(f"{key}={value}\n")
            f.write('</configuration>\n\n')
        
        # 핵심 파일 내용 섹션
        f.write('<source_files>\n')
        for file_info in sorted(files_info, key=lambda x: x['path']):
            if 'test' not in file_info['path'].lower():
                f.write(f"<file path=\"{file_info['path']}\">\n")
                f.write(f"<package>{file_info['package']}</package>\n")
                
                # 파일 유형 태그 추가(가능한 경우)
                if file_info.get('file_type'):
                    f.write(f"<file_type>{file_info['file_type']}</file_type>\n")
                
                # 클래스 정보 추가(가능한 경우)
                if file_info.get('class_info') and file_info['class_info'].get('name'):
                    f.write(f"<class_name>{file_info['class_info']['name']}</class_name>\n")
                
                # 복잡도 지표 추가(가능한 경우)
                if file_info.get('complexity'):
                    f.write("<complexity>\n")
                    for metric, value in file_info['complexity'].items():
                        f.write(f"{metric}: {value}\n")
                    f.write("</complexity>\n")
                
                # JavaDoc 추가(가능한 경우)
                if file_info.get('javadocs') and file_info['javadocs']:
                    f.write("<javadocs>\n")
                    for doc in file_info['javadocs']:
                        f.write(f"{doc}\n---\n")
                    f.write("</javadocs>\n")
                
                # TODO 추가(가능한 경우)
                if file_info.get('todos') and file_info['todos']:
                    f.write("<todos>\n")
                    for todo in file_info['todos']:
                        f.write(f"- {todo}\n")
                    f.write("</todos>\n")
                
                f.write("<content>\n")
                f.write(file_info['content'])
                f.write("\n</content>\n")
                f.write("</file>\n\n")
        
        f.write('</source_files>\n')
        f.write('</document_content>\n')
        f.write('</document>\n')
        f.write('</documents>')