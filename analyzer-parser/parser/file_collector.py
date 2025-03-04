import logging
from pathlib import Path

logger = logging.getLogger("analyzer.file.collector")

class FileCollector:
    """프로젝트 파일 수집 담당 클래스"""
    
    def __init__(self):
        self.exclude_dirs = {'.git', 'build', 'out', '.idea', 'target', 'bin', '.mvn', 'logs', '.gradle', 'gradle'}
        self.exclude_files = {'.gitattributes', '.gitignore', 'HELP.md', 'gradlew', 'gradlew.bat'}
        self.exclude_extensions = {'.class', '.jar', '.war', '.exe', '.dll', '.so', '.dylib',
                               '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.log', '.iml'}
    
    def collect_files(self, source_dir):
        """프로젝트 디렉토리에서 분석 대상 파일 수집"""
        source = Path(source_dir)
        collected_files = []
        
        # README 파일 찾기
        readme_content = self.find_readme(source)
        
        # 중요 설정 파일 목록
        important_files = ['build.gradle', 'build.gradle.kts', 'settings.gradle', 
                          'settings.gradle.kts', 'pom.xml', 'application.yml', 
                          'application.yaml', 'application.properties']
        
        # 모든 파일 순회
        for path in source.rglob('*'):
            if self.should_process_file(path, important_files):
                try:
                    file_info = self.read_file(source, path)
                    collected_files.append(file_info)
                except Exception as e:
                    logger.error(f"파일 읽기 오류 {path}: {str(e)}")
        
        return collected_files, readme_content
    
    def should_process_file(self, path, important_files):
        """파일이 처리 대상인지 확인"""
        if not path.is_file():
            return False
            
        if any(exclude_dir in path.parts for exclude_dir in self.exclude_dirs):
            return False
            
        if path.name in self.exclude_files:
            return False
            
        # 중요 파일이거나 제외 확장자가 아닌 경우 처리
        return path.name in important_files or path.suffix.lower() not in self.exclude_extensions
    
    def read_file(self, source, path):
        """파일 읽기 및 기본 정보 추출"""
        relative_path = path.relative_to(source)
        content = path.read_text(encoding='utf-8', errors='ignore')
        
        file_info = {
            'path': str(relative_path),
            'package': '/'.join(relative_path.parts[:-1]),
            'content': content,
            'file_type': self.determine_file_type(path.name, content)
        }
        
        return file_info
    
    def find_readme(self, source):
        """README 파일 찾기"""
        for readme_file in ['README.md', 'README.txt', 'readme.md']:
            readme_path = source / readme_file
            if readme_path.exists():
                try:
                    return readme_path.read_text(encoding='utf-8', errors='ignore')
                except:
                    pass
        return None
    
    def determine_file_type(self, filename, content):
        """파일 유형 결정"""
        if filename in ['build.gradle', 'build.gradle.kts', 'settings.gradle', 'settings.gradle.kts', 'pom.xml']:
            return 'build'
        elif filename in ['application.yml', 'application.yaml', 'application.properties']:
            return 'config'
        elif filename.endswith('.java'):
            return None  # 자바 파일은 추가 분석 필요
        elif filename.endswith(('.yml', '.yaml', '.properties')):
            return 'config'
        else:
            return 'resource'