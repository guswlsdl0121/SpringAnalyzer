"""
코드 복잡성과 코드 특성을 분석하기 위한 모듈
"""
import re

def calculate_code_complexity(content):
    """
    간단한 코드 복잡성 지표 계산
    """
    complexity = {
        'lines': len(content.splitlines()),
        'methods': len(re.findall(r'\b(public|private|protected)\s+\w+\s+\w+\s*\(', content)),
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

def remove_imports(content):
    """
    Java 파일에서 import 문 제거
    """
    # import 블록 제거 (패키지 문부터 첫 클래스/인터페이스 선언까지)
    cleaned_content = re.sub(r'(package\s+[\w.]+;)\s*(import\s+[\w.*]+;\s*)*', r'\1\n\n', content)
    return cleaned_content