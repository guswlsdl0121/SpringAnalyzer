from pathlib import Path
from datetime import datetime
import json
import re

# 분석기 모듈 임포트
from parser.analyzers.structure_analyzer import analyze_project_structure
from parser.analyzers.code_analyzer import calculate_code_complexity
from parser.analyzers.endpoint_analyzer import analyze_endpoints
from parser.analyzers.business_analyzer import find_business_objects

# 파서 모듈 임포트
from parser.parsers.build_parser import parse_gradle_file, parse_maven_file

def create_project_summary(source_dirs, target_dir):
    """
    분석된 각 프로젝트에 대한 개별 요약 생성 (JSON 형식)
    """
    summary_files = []
    
    for source_dir in source_dirs:
        try:
            source = Path(source_dir)
            
            # 기본 프로젝트 정보
            project_name = source.name
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            summary_filename = f"{timestamp}_{project_name}_summary.json"
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
            
            # 프로젝트 구조 분석
            structure = analyze_project_structure(source_dir)
            component_counts = {component: len(paths) for component, paths in structure.items() if paths}
            
            # API 엔드포인트 추출 (재밌는 정보 추가)
            files_info = []
            for path in source.rglob('*.java'):
                try:
                    content = path.read_text(encoding='utf-8', errors='ignore')
                    files_info.append({
                        'path': str(path.relative_to(source)),
                        'content': content
                    })
                except Exception as e:
                    print(f"Error reading file {path}: {str(e)}")
            
            endpoints = analyze_endpoints(files_info)
            
            # 비즈니스 객체 추출
            business_objects = find_business_objects(files_info)
            
            # 복잡도 지표 계산
            complexity_metrics = {
                'avg_method_count': 0,
                'avg_complexity': 0,
                'max_complexity': 0,
                'complex_files': []
            }
            
            java_files = [f for f in files_info if f['path'].endswith('.java')]
            if java_files:
                total_methods = sum(len(re.findall(r'\b(public|private|protected)\s+\w+\s+\w+\s*\(', f['content'])) for f in java_files)
                total_complexity = 0
                max_complexity = 0
                complex_file = ''
                
                for f in java_files:
                    complexity = calculate_code_complexity(f['content'])
                    if complexity['cyclomatic'] > max_complexity:
                        max_complexity = complexity['cyclomatic']
                        complex_file = f['path']
                    total_complexity += complexity['cyclomatic']
                
                complexity_metrics['avg_method_count'] = round(total_methods / len(java_files), 2)
                complexity_metrics['avg_complexity'] = round(total_complexity / len(java_files), 2)
                complexity_metrics['max_complexity'] = max_complexity
                complexity_metrics['complex_files'] = complex_file
            
            # 요약 JSON 생성
            summary = {
                "projectName": project_name,
                "generated": datetime.now().isoformat(),
                "buildInfo": {
                    "group": build_info.get('group', 'N/A'),
                    "version": build_info.get('version', 'N/A'),
                    "springBootVersion": build_info.get('springBootVersion', 'N/A'),
                    "javaVersion": build_info.get('javaVersion', 'N/A')
                },
                "components": component_counts,
                "apiEndpoints": {
                    "count": len(endpoints),
                    "routes": [f"{e['method']} {e['path']}" for e in endpoints[:5]]  # 상위 5개만
                },
                "businessObjects": {
                    "count": len(business_objects),
                    "names": [bo['name'] for bo in business_objects[:5]]  # 상위 5개만
                },
                "complexityMetrics": complexity_metrics,
                "dependencies": {
                    "count": len(build_info.get('dependencies', [])),
                    "topDeps": build_info.get('dependencies', [])[:7]  # 상위 7개만
                }
            }
            
            # JSON 저장
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            summary_files.append(summary_filename)
            print(f"Project JSON summary created: {summary_filename}")
            
        except Exception as e:
            print(f"Summary generation failed for {source_dir}: {str(e)}")
    
    return summary_files