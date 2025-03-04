import logging
import mimetypes
from pathlib import Path
import re

logger = logging.getLogger("analyzer.file.collector")

class FileCollector:
    """프로젝트 파일 수집 담당 클래스"""
    
    def __init__(self):
        # 제외할 불필요한 파일/디렉터리
        self.exclude_dirs = {
            '.git', 'build', 'out', '.idea', 'target', 'bin', '.mvn', 
            'logs', '.gradle', 'gradle', 'node_modules', 'dist', 
            'coverage'
        }
        
        self.exclude_files = {
            '.gitattributes', '.gitignore', 'HELP.md', 'gradlew', 
            'gradlew.bat', '.DS_Store', 'Thumbs.db', 
            '.project', '.classpath'
        }
        
        self.exclude_extensions = {
            '.class', '.jar', '.war', '.exe', '.dll', '.so', '.dylib',
            '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.log', '.iml'
        }
        
        # 최대 파일 크기 (1MB)
        self.max_file_size_kb = 1024
    
    def collect_files(self, source_dir):
        """프로젝트 디렉토리에서 분석 대상 파일 수집"""
        source = Path(source_dir)
        collected_files = []
        skipped_count = {'binary': 0, 'large': 0, 'excluded': 0}
        
        # README 파일 찾기
        readme_content = None
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
               not any(exclude_dir in path.parts for exclude_dir in self.exclude_dirs) and \
               path.name not in self.exclude_files and \
               (path.suffix.lower() not in self.exclude_extensions or 
                path.name in ['build.gradle', 'build.gradle.kts', 'settings.gradle.kts', 'pom.xml']):
                
                try:
                    # 파일 크기 제한 (1MB)
                    if path.stat().st_size > self.max_file_size_kb * 1024:
                        skipped_count['large'] += 1
                        continue
                    
                    relative_path = path.relative_to(source)
                    
                    try:
                        content = path.read_text(encoding='utf-8', errors='ignore')
                    except Exception:
                        # 바이너리 파일 처리
                        skipped_count['binary'] += 1
                        continue
                    
                    file_info = {
                        'path': str(relative_path),
                        'package': '/'.join(relative_path.parts[:-1]),
                        'content': content
                    }

                    # 파일 유형 및 추가 정보 판별
                    if path.name in ['build.gradle', 'build.gradle.kts', 'settings.gradle.kts']:
                        file_info['file_type'] = 'build'
                    elif path.name == 'pom.xml':
                        file_info['file_type'] = 'build'
                    elif path.name in ['application.yml', 'application.yaml', 'application.properties']:
                        file_info['file_type'] = 'config'
                    elif path.suffix == '.java':
                        # Java 파일의 추가 처리
                        cleaned_content = self.remove_imports(content)
                        file_type = self.determine_file_type(str(relative_path), content)
                        
                        file_info['content'] = cleaned_content
                        file_info['file_type'] = file_type
                        
                        # 클래스 정보 등 추가 정보는 파서에서 별도로 추출
                    elif path.suffix in ['.yml', '.yaml', '.properties']:
                        file_info['file_type'] = 'config'
                    else:
                        file_info['file_type'] = 'resource'
                    
                    collected_files.append(file_info)
                
                except Exception as e:
                    print(f"File reading error {path}: {str(e)}")
        
        return collected_files, readme_content
    
    def remove_imports(self, content):
        """Java 파일에서 import 문 제거"""
        # import 블록 제거 (패키지 문부터 첫 클래스/인터페이스 선언까지)
        cleaned_content = re.sub(r'(package\s+[\w.]+;)\s*(import\s+[\w.*]+;\s*)*', r'\1\n\n', content)
        return cleaned_content
    
    def determine_file_type(self, path, content):
        """Java 파일 유형 판별"""
        if 'Controller' in path and ('@Controller' in content or '@RestController' in content):
            return 'controller'
        elif 'Service' in path and '@Service' in content:
            return 'service'
        elif 'Repository' in path and '@Repository' in content:
            return 'repository'
        elif '@Entity' in content:
            return 'entity'
        elif '@Configuration' in content:
            return 'config'
        elif ('DTO' in path or 'Dto' in path or 'dto' in path.lower() or 
              'Request' in path or 'Response' in path or 'record' in content.lower()):
            return 'dto'
        elif 'Mapper' in path:
            return 'mapper'
        elif 'Util' in path or 'Utils' in path:
            return 'util'
        elif '.domain.' in path.lower():
            return 'domain'
        elif '.dto.' in path.lower():
            return 'dto'
        
        return None