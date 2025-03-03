"""
Java 소스 코드에서 JavaDoc 주석을 추출하기 위한 모듈
"""
import re

def extract_javadoc(content):
    """
    Java 코드에서 JavaDoc 주석 추출
    """
    javadoc_pattern = r'/\*\*\s*(.*?)\s*\*/'
    javadocs = []
    
    for match in re.finditer(javadoc_pattern, content, re.DOTALL):
        javadoc = match.group(1)
        # 자바독 정리
        javadoc = re.sub(r'\n\s*\*\s*', '\n', javadoc).strip()
        javadocs.append(javadoc)
    
    return javadocs