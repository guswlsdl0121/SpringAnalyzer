import logging
import re
from ..extractors.class_extractor import ClassInfoExtractor
from ..extractors.javadoc_extractor import JavadocExtractor
from ..extractors.todo_extractor import TodoExtractor

logger = logging.getLogger("analyzer.parser.java_analyzer")

class CodeComplexityAnalyzer:
    """코드 복잡도 분석기"""
    
    def calculate_complexity(self, content):
        """코드 복잡성 지표 계산"""
        complexity = {
            'lines': len(content.splitlines()),
            'methods': len(re.findall(r'\b(public|private|protected)\s+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*(\{|throws)', content)),
            'conditional_branches': len(re.findall(r'\b(if|else if|case)\b', content)),
            'loops': len(re.findall(r'\b(for|while|do)\b', content)),
            'try_catch': len(re.findall(r'\btry\b', content))
        }
        
        # 사이클로매틱 복잡도 근사값 계산
        complexity['cyclomatic'] = (
            complexity['conditional_branches'] + 
            complexity['loops'] + 
            complexity['try_catch'] + 1  # 기본 복잡도
        )
        
        return complexity
    
    def remove_imports(self, content):
        """Java 파일에서 import 문 제거"""
        # import 블록 제거 (패키지 문부터 첫 클래스/인터페이스 선언까지)
        cleaned_content = re.sub(r'(package\s+[\w.]+;)\s*(import\s+[\w.*]+;\s*)*', r'\1\n\n', content)
        return cleaned_content


class JavaAnalyzer:
    """Java 파일 분석 전담 클래스"""
    
    def __init__(self):
        self.class_extractor = ClassInfoExtractor()
        self.code_analyzer = CodeComplexityAnalyzer()
        self.javadoc_extractor = JavadocExtractor()
        self.todo_extractor = TodoExtractor()
    
    def analyze_all(self, java_files):
        """모든 Java 파일 분석"""
        analyzed_files = []
        
        for file_info in java_files:
            analyzed = self.analyze_file(file_info)
            analyzed_files.append(analyzed)
            
        return analyzed_files
    
    def analyze_file(self, file_info):
        """단일 Java 파일 분석"""
        content = file_info['content']
        
        # 임포트 제거
        cleaned_content = self.code_analyzer.remove_imports(content)
        
        # 파일 유형 판별
        file_type = self.determine_file_type(file_info['path'], content)
        
        # 클래스 정보 추출
        class_info = self.class_extractor.extract(cleaned_content)
        
        # 코드 복잡도 계산
        complexity = self.code_analyzer.calculate_complexity(cleaned_content)
        
        # JavaDoc 및 TODO 추출
        javadocs = self.javadoc_extractor.extract(content)
        todos = self.todo_extractor.extract(content)
        
        # 결과 병합
        result = dict(file_info)
        result['content'] = cleaned_content
        result['file_type'] = file_type
        result['class_info'] = class_info
        result['complexity'] = complexity
        result['javadocs'] = javadocs
        result['todos'] = todos
        
        return result
    
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