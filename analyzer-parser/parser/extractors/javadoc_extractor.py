import logging
import re

logger = logging.getLogger("analyzer.parser.extractors.javadoc")

class JavadocExtractor:
    """JavaDoc 주석 추출 클래스"""
    
    def extract(self, content):
        """Java 코드에서 JavaDoc 주석 추출"""
        javadoc_pattern = r'/\*\*\s*(.*?)\s*\*/'
        javadocs = []
        
        for match in re.finditer(javadoc_pattern, content, re.DOTALL):
            javadoc = match.group(1)
            # 자바독 정리
            javadoc = self.clean_javadoc(javadoc)
            javadocs.append(javadoc)
        
        return javadocs
    
    def clean_javadoc(self, javadoc):
        """JavaDoc 주석 정리"""
        # 각 줄의 앞에 있는 공백과 * 제거
        cleaned = re.sub(r'\n\s*\*\s*', '\n', javadoc).strip()
        return cleaned


class TodoExtractor:
    """TODO 및 FIXME 주석 추출 클래스"""
    
    def extract(self, content):
        """코드에서 TODO 및 FIXME 주석 추출"""
        todo_pattern = r'(?://|/\*|^\s*\*)\s*(TODO|FIXME):\s*(.*?)(?:\*/|\n)'
        todos = []
        
        for match in re.finditer(todo_pattern, content, re.MULTILINE):
            todo_type = match.group(1)
            todo_text = match.group(2).strip()
            todos.append(f"{todo_type}: {todo_text}")
        
        return todos