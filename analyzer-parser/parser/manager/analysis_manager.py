from pathlib import Path
from datetime import datetime
import re

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
from parser.generators.all_analysis_generator import generate_xml_output

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
    
    # 프로젝트 이름 추출 - 로컬 파서와 동일한 방식으로 변경
    path_parts = str(source_dir).split('/')
    if len(path_parts) >= 4:
        project_name = path_parts[3]  # 4번째 디렉터리 이름 (인덱스 3)
    else:
        project_name = source.name  # 기본적으로 마지막 디렉터리 이름

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{timestamp}-{project_name}-analysis.xml"  # 하이픈 사용으로 통일
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
    
    # 중요 설정 파일 목록 - 로컬 파서와 동일하게 설정
    important_files = ['build.gradle', 'build.gradle.kts', 'settings.gradle', 'settings.gradle.kts', 'pom.xml', 
                      'application.yml', 'application.yaml', 'application.properties']
    
    # 파일 수집 로직 - 로컬 파서와 유사하게 조정
    for path in source.rglob('*'):
        # 파일 수집 조건 확인
        if path.is_file() and \
           not any(exclude_dir in path.parts for exclude_dir in exclude_dirs) and \
           path.name not in exclude_files and \
           (path.suffix.lower() not in exclude_extensions or path.name in important_files):
            try:
                relative_path = path.relative_to(source)
                content = path.read_text(encoding='utf-8', errors='ignore')
                
                file_info = {
                    'path': str(relative_path),
                    'package': '/'.join(relative_path.parts[:-1]),
                    'content': content
                }

                if path.name in ['build.gradle', 'build.gradle.kts', 'settings.gradle', 'settings.gradle.kts']:
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
                elif path.suffix in ['.html', '.js', '.css']:
                    file_info['file_type'] = 'resource'
                else:
                    file_info['file_type'] = 'resource'
                
                files_info.append(file_info)
            except Exception as e:
                print(f"File reading error {path}: {str(e)}")
    
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

def analyze_projects(source_dirs, target_dir):
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