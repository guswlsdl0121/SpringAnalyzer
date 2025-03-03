from pathlib import Path
from datetime import datetime

# 분석기 모듈 임포트
from parser.analyzers.structure_analyzer import analyze_project_structure


from parser.analyzers.code_analyzer import calculate_code_complexity, remove_imports
from parser.analyzers.endpoint_analyzer import analyze_endpoints
from parser.analyzers.relationship_analyzer import extract_class_relationships
from parser.analyzers.business_analyzer import (find_business_objects, 
                                         extract_business_logic_summary,
                                         analyze_data_flows)

# 파서 모듈 임포트
from parser.parsers.build_parser import parse_gradle_file, parse_maven_file
from parser.parsers.config_parser import analyze_config_file

# 추출기 모듈 임포트
from parser.extractors.class_extractor import extract_class_info, determine_file_type
from parser.extractors.javadoc_extractor import extract_javadoc
from parser.extractors.todo_extractor import extract_todos

# 생성기 모듈 임포트
from parser.generators.summary_generator import (extract_architecture_summary,
                                          analyze_spring_boot_features)
from parser.generators.xml_generator import generate_xml_output

def analyze_single_service(source_dir, target_dir):
    """
    단일 Spring Boot 서비스 프로젝트를 분석하고 문서화합니다.
    """
    source = Path(source_dir)
    target = Path(target_dir)
    
    # 제외할 불필요한 파일/디렉터리
    exclude_dirs = {'.git', 'build', 'out', '.idea', 'target', 'bin', '.mvn', 'logs', '.gradle', 'gradle'}
    exclude_files = {'.gitattributes', '.gitignore', 'HELP.md', 'gradlew', 'gradlew.bat'}
    exclude_extensions = {'.class', '.jar', '.war', '.exe', '.dll', '.so', '.dylib',
                         '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.log', '.iml'}
    
    # 프로젝트 이름 추출 - 간단히 마지막 디렉토리 이름 사용
    project_name = source.name

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{timestamp}-{project_name}-analysis.xml"
    output_path = target / output_filename
    
    project_info = {}
    structure_info = analyze_project_structure(source_dir)
    config_info = {}
    files_info = []
    readme_content = None
    
    # README 파일 탐색
    for readme_file in ['README.md', 'README.txt', 'readme.md']:
        readme_path = source / readme_file
        if readme_path.exists():
            try:
                readme_content = readme_path.read_text(encoding='utf-8', errors='ignore')
                break
            except:
                pass
    
    # 중요 설정 파일 목록
    important_files = ['build.gradle', 'build.gradle.kts', 'settings.gradle', 'pom.xml', 
                      'application.yml', 'application.yaml', 'application.properties']
    
    # 핵심 파일만 수집
    for path in source.rglob('*'):
        # src 디렉토리 내부 파일 또는 중요 설정 파일인 경우에만 처리
        if path.is_file() and \
           not any(exclude_dir in path.parts for exclude_dir in exclude_dirs) and \
           path.name not in exclude_files and \
           (path.suffix.lower() not in exclude_extensions or path.name in important_files) and \
           ('src' in path.parts or path.name in important_files or 'config' in path.parts):
            try:
                relative_path = path.relative_to(source)
                content = path.read_text(encoding='utf-8', errors='ignore')
                
                file_info = {
                    'path': str(relative_path),
                    'package': '/'.join(relative_path.parts[:-1]),
                    'content': content
                }

                if path.name in ['build.gradle', 'build.gradle.kts', 'settings.gradle']:
                    project_info = parse_gradle_file(content)
                    file_info['file_type'] = 'build'
                elif path.name == 'pom.xml':
                    project_info = parse_maven_file(content)
                    file_info['file_type'] = 'build'
                elif path.name in ['application.yml', 'application.yaml', 'application.properties']:
                    config = analyze_config_file(path.name, content)
                    config_info.update(config)
                    file_info['file_type'] = 'config'
                elif path.suffix == '.java':
                    # 깔끔한 분석을 위해 Java 파일에서 import 문 제거
                    cleaned_content = remove_imports(content)
                    file_info['content'] = cleaned_content
                    
                    # 파일 유형 판별
                    file_type = determine_file_type(str(relative_path), content)
                    file_info['file_type'] = file_type
                    
                    # 클래스 정보 추출
                    file_info['class_info'] = extract_class_info(cleaned_content)
                    
                    # JavaDoc 주석 추출
                    file_info['javadocs'] = extract_javadoc(content)
                    
                    # TODO 추출
                    file_info['todos'] = extract_todos(content)
                    
                    # 코드 복잡도 계산
                    file_info['complexity'] = calculate_code_complexity(cleaned_content)
                elif path.suffix in ['.yml', '.yaml', '.properties']:
                    config = analyze_config_file(str(path), content)
                    file_info['file_type'] = 'config'
                else:
                    file_info['file_type'] = 'resource'
                
                files_info.append(file_info)
            except Exception as e:
                print(f"File reading error {path}: {str(e)}")
    
    # 남은 코드는 원래대로 유지
    # 클래스 간의 관계 추출
    relationships = extract_class_relationships(files_info)
    
    # 비즈니스 객체 찾기
    business_objects = find_business_objects(files_info)
    
    # API 엔드포인트 추출
    endpoints = analyze_endpoints(files_info)
    
    # 아키텍처 요약 생성
    architecture_summary = extract_architecture_summary(files_info)
    
    # 비즈니스 로직 요약, 데이터 흐름, Spring Boot 특성 분석 추가
    business_logic = extract_business_logic_summary(files_info)
    data_flows = analyze_data_flows(files_info, relationships)
    spring_features = analyze_spring_boot_features(files_info)
    
    # XML 문서 생성
    generate_xml_output(
        output_path, 
        project_name,
        project_info,
        architecture_summary,
        endpoints,
        business_objects,
        readme_content,
        structure_info,
        relationships,
        business_logic,
        data_flows,
        spring_features,
        config_info,
        files_info
    )
    
    return output_filename

def file_merger(source_dirs, target_dir):
    """
    여러 Spring Boot 서비스 프로젝트를 분석하고 개별 문서 생성
    """
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    
    output_files = []
    for source_dir in source_dirs:
        try:
            output_file = analyze_single_service(source_dir, target_dir)
            output_files.append(output_file)
            print(f"Service analysis completed: {output_file}")
        except Exception as e:
            print(f"Service analysis failed {source_dir}: {str(e)}")
    
    return output_files

def create_project_summary(source_dirs, target_dir):
    """
    분석된 각 프로젝트에 대한 개별 요약 생성
    """
    summary_files = []
    
    for source_dir in source_dirs:
        try:
            source = Path(source_dir)
            
            # 기본 프로젝트 정보
            project_name = source.name
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            summary_filename = f"{timestamp}-{project_name}-summary.md"
            summary_path = Path(target_dir) / summary_filename
            
            # 빌드 파일 찾기
            build_info = {}
            build_files = list(source.glob('build.gradle')) + list(source.glob('build.gradle.kts')) + list(source.glob('pom.xml'))
            if build_files:
                content = build_files[0].read_text(encoding='utf-8', errors='ignore')
                if build_files[0].name.endswith('.xml'):
                    build_info = parse_maven_file(content)
                else:
                    build_info = parse_gradle_file(content)
            
            # 구성 요소 수 계산
            structure = analyze_project_structure(source_dir)
            component_counts = {component: len(paths) for component, paths in structure.items() if paths}
            
            # 개별 요약 파일 작성
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"# Project Analysis Summary - {project_name}\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## Project Overview\n\n")
                f.write(f"- Path: {source_dir}\n")
                
                if build_info.get('group'):
                    f.write(f"- Group: {build_info.get('group', 'N/A')}\n")
                if build_info.get('version'):
                    f.write(f"- Version: {build_info.get('version', 'N/A')}\n")
                if build_info.get('springBootVersion'):
                    f.write(f"- Spring Boot: {build_info.get('springBootVersion', 'N/A')}\n")
                
                f.write("\n## Components\n\n")
                for component, count in component_counts.items():
                    f.write(f"- {component.capitalize()}: {count}\n")
                
                # 의존성 요약 추가
                if build_info.get('dependencies'):
                    f.write("\n## Dependencies\n\n")
                    for dep in build_info.get('dependencies')[:10]:  # 간결함을 위해 10개의 의존성으로 제한
                        f.write(f"- {dep}\n")
                    
                    if len(build_info.get('dependencies')) > 10:
                        f.write(f"- ... 그리고 {len(build_info.get('dependencies')) - 10}개 더\n")
                
                # 플러그인 요약 추가
                if build_info.get('plugins'):
                    f.write("\n## Plugins\n\n")
                    for plugin in build_info.get('plugins'):
                        f.write(f"- {plugin}\n")
            
            summary_files.append(summary_filename)
            print(f"Project summary created: {summary_filename}")
            
        except Exception as e:
            print(f"Summary generation failed for {source_dir}: {str(e)}")
    
    return summary_files