"""
소스 코드에서 TODO 및 FIXME 주석을 추출하기 위한 모듈
"""
import re

def extract_todos(content):
    """
    코드에서 TODO 및 FIXME 주석 추출
    """
    todo_pattern = r'(?://|/\*|^\s*\*)\s*(TODO|FIXME):\s*(.*?)(?:\*/|\n)'
    todos = []
    
    for match in re.finditer(todo_pattern, content, re.MULTILINE):
        todo_type = match.group(1)
        todo_text = match.group(2).strip()
        todos.append(f"{todo_type}: {todo_text}")
    
    return todos