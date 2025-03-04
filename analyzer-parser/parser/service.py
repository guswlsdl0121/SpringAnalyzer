import os
import logging
import json
import re
from datetime import datetime
from pathlib import Path

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
from parser.generators.all_analysis_generator import generate_json_output

# 요약 정보 모델 임포트
from parser.models import ProjectSummary

class ParserService:
    """프로젝트 분석을 담당하는 서비스 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger("analyzer.parser.service")
    
    def analyze_project(self, project_id, source_dir, output_dir):
        """
        프로젝트 파일 분석 수행
        """
        try:
            # 출력 디렉토리 생성
            target_dir = Path(output_dir)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 프로젝트 이름 추출
            project_name = Path(source_dir).name
            
            # 단일 서비스 분석 수행
            analysis_filename, summary = self.analyze_single_service(source_dir, output_dir, project_name)
            self.logger.info(f"Service analysis completed: {analysis_filename}")
            
            # 요약 정보 JSON 파일 생성
            summary_filename = self._create_json_summary(summary, output_dir)
            
            # 결과 정보 로깅
            self.logger.info(f"프로젝트 {project_id} 파싱 완료: XML={analysis_filename}, 요약={summary_filename}")
            
            # 결과 파일 경로 구성
            analysis_file_path = None
            if analysis_filename:
                analysis_file_path = os.path.join(output_dir, analysis_filename)
            
            summary_file_path = None
            if summary_filename:
                summary_file_path = os.path.join(output_dir, summary_filename)
            
            return {
                'success': True,
                'analysis_file': analysis_file_path,
                'summary_file': summary_file_path,
                'files_processed': 1  # 단일 프로젝트 분석
            }
                
        except Exception as parse_error:
            self.logger.error(f"프로젝트 파싱 실패: {str(parse_error)}", exc_info=True)
            return {
                'success': False,
                'error': f"파싱 오류: {str(parse_error)}"
            }
    
    def analyze_single_service(self, source_dir, target_dir, project_name):
        """
        단일 Spring Boot 서비스 프로젝트를 분석하고 문서화합니다.
        """
        source = Path(source_dir)
        target = Path(target_dir)
        
        # 요약 정보 객체 초기화
        summary = ProjectSummary(project_name)
        
        # 제외할 불필요한 파일/디렉터리
        exclude_dirs = {'.git', 'build', 'out', '.idea', 'target', 'bin', '.mvn', 'logs', '.gradle', 'gradle'}
        exclude_files = {'.gitattributes', '.gitignore', 'HELP.md', 'gradlew', 'gradlew.bat'}
        exclude_extensions = {'.class', '.jar', '.war', '.exe', '.dll', '.so', '.dylib',
                            '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.log', '.iml',
                     '.sql', '.json'}  # SQL 및 JSON 확장자 추가

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{timestamp}-{project_name}-analysis.json"
        output_path = target / output_filename
        
        project_info = {}
        structure_info = analyze_project_structure(source_dir)
        
        # 요약 데이터에 구조 정보 추가
        summary.update_component_counts({component: len(paths) for component, paths in structure_info.items() if paths})
        
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
        
        # 핵심 파일만 수집
        for path in source.rglob('*'):
            if path.is_file() and \
               not any(exclude_dir in path.parts for exclude_dir in exclude_dirs) and \
               path.name not in exclude_files and \
               (path.suffix.lower() not in exclude_extensions or path.name in ['build.gradle', 'build.gradle.kts', 'settings.gradle.kts', 'pom.xml']):
                try:
                    relative_path = path.relative_to(source)
                    content = path.read_text(encoding='utf-8', errors='ignore')
                    
                    file_info = {
                        'path': str(relative_path),
                        'package': '/'.join(relative_path.parts[:-1]),
                        'content': content
                    }

                    if path.name in ['build.gradle', 'build.gradle.kts', 'settings.gradle.kts']:
                        project_info = parse_gradle_file(content)
                        file_info['file_type'] = 'build'
                        
                        # 요약 데이터에 빌드 정보 추가
                        summary.update_build_info(
                            project_info.get('group'),
                            project_info.get('version'),
                            project_info.get('springBootVersion'),
                            project_info.get('javaVersion')
                        )
                        
                        # 의존성 정보 추가
                        summary.update_dependencies(project_info.get('dependencies', []))
                        
                    elif path.name == 'pom.xml':
                        project_info = parse_maven_file(content)
                        file_info['file_type'] = 'build'
                        
                        # 요약 데이터에 빌드 정보 추가 
                        summary.update_build_info(
                            project_info.get('group'),
                            project_info.get('version'),
                            project_info.get('springBootVersion'),
                            project_info.get('javaVersion')
                        )
                        
                        # 의존성 정보 추가
                        summary.update_dependencies(project_info.get('dependencies', []))
                        
                    elif path.name in ['application.yml', 'application.yaml', 'application.properties']:
                        config = analyze_config_file(path.name, content)
                        config_info.update(config)
                        file_info['file_type'] = 'config'
                    elif path.suffix == '.java':
                        # Java 파일인 경우 메트릭 데이터 수집
                        method_count = len(re.findall(r'\b(public|private|protected)\s+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*(\{|throws)', content))
                        
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
                        complexity = calculate_code_complexity(cleaned_content)
                        file_info['complexity'] = complexity
                        
                        # 요약 정보에 Java 파일 메트릭 추가
                        summary.add_java_file_metrics(
                            method_count,
                            complexity['cyclomatic'],
                            str(relative_path)
                        )
                        
                    elif path.suffix in ['.yml', '.yaml', '.properties']:
                        config = analyze_config_file(str(path), content)
                        file_info['file_type'] = 'config'
                    else:
                        file_info['file_type'] = 'resource'
                    
                    files_info.append(file_info)
                except Exception as e:
                    self.logger.error(f"File reading error {path}: {str(e)}")
        
        # 클래스 간의 관계 추출
        relationships = extract_class_relationships(files_info)
        
        # 비즈니스 객체 찾기
        business_objects = find_business_objects(files_info)
        
        # 요약 데이터에 비즈니스 객체 정보 추가
        for bo in business_objects:
            summary.add_business_object(bo['name'])
        
        # API 엔드포인트 추출
        endpoints = analyze_endpoints(files_info)
        
        # 요약 데이터에 API 엔드포인트 정보 추가
        for endpoint in endpoints:
            summary.add_api_endpoint(endpoint['method'], endpoint['path'])
        
        # 아키텍처 요약 생성
        architecture_summary = extract_architecture_summary(files_info)
        
        # 비즈니스 로직 요약, 데이터 흐름, Spring Boot 특성 분석 추가
        business_logic = extract_business_logic_summary(files_info)
        data_flows = analyze_data_flows(files_info, relationships)
        spring_features = analyze_spring_boot_features(files_info)
        
        # Json 문서 생성        
        output_filename = generate_json_output(
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

        return output_filename, summary
    
    def _create_json_summary(self, summary, target_dir):
        """
        JSON 형식의 요약 정보 파일 생성
        """
        project_name = summary.project_name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_filename = f"{timestamp}_{project_name}_summary.json"
        summary_path = Path(target_dir) / summary_filename
        
        # JSON 저장
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary.to_dict(), f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"JSON 요약 파일 생성됨: {summary_filename}")
        return summary_filename