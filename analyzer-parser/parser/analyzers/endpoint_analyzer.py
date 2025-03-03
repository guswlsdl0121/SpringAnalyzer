"""
API 엔드포인트를 분석하기 위한 모듈
"""
import re

def analyze_endpoints(files_info):
    """
    컨트롤러에서 요청/응답 모델과 함께 API 엔드포인트 추출
    """
    endpoints = []
    
    for file_info in files_info:
        if file_info.get('file_type') == 'controller':
            content = file_info['content']
            
            # 클래스 레벨 매핑 검색
            class_mapping = re.search(r'@RequestMapping\(["\']([^"\']+)["\']\)', content)
            base_path = class_mapping.group(1) if class_mapping else ''
            
            # 메서드 레벨 매핑 검색
            method_patterns = [
                (r'@GetMapping\(["\']([^"\']+)["\']\)', 'GET'),
                (r'@PostMapping\(["\']([^"\']+)["\']\)', 'POST'),
                (r'@PutMapping\(["\']([^"\']+)["\']\)', 'PUT'),
                (r'@DeleteMapping\(["\']([^"\']+)["\']\)', 'DELETE'),
                (r'@PatchMapping\(["\']([^"\']+)["\']\)', 'PATCH'),
                (r'@RequestMapping\((?:[^)]|value\s*=\s*["\']([^"\']+)["\'])[^)]*method\s*=\s*RequestMethod\.([^)]+)\)', None)
            ]
            
            for pattern, method_type in method_patterns:
                for match in re.finditer(pattern, content):
                    if not method_type:  # RequestMapping 경우
                        path = match.group(1)
                        method_type = match.group(2)
                    else:
                        path = match.group(1)
                    
                    # 메서드 이름 및 시그니처 가져오기
                    method_block = content[match.end():].split("{", 1)[0]
                    method_name_match = re.search(r'(?:public|private|protected)?\s+(?:\w+)(?:<[^>]+>)?\s+(\w+)\s*\(', method_block)
                    method_name = method_name_match.group(1) if method_name_match else "unknown"
                    
                    # 요청 파라미터 및 본문 추출
                    request_params = []
                    for param_match in re.finditer(r'@RequestParam\([^)]*\)\s+\w+\s+(\w+)', method_block):
                        request_params.append(param_match.group(1))
                    
                    request_body = None
                    request_body_match = re.search(r'@RequestBody\s+(\w+(?:<[^>]+>)?)\s+(\w+)', method_block)
                    if request_body_match:
                        request_body = f"{request_body_match.group(1)} {request_body_match.group(2)}"
                    
                    # 응답 유형 추출
                    response_type_match = re.search(r'(?:public|private|protected)?\s+(\w+(?:<[^>]+>)?)\s+\w+\s*\(', method_block)
                    response_type = response_type_match.group(1) if response_type_match else "void"
                    
                    # Swagger/OpenAPI 어노테이션 검색
                    operation_summary = None
                    operation_match = re.search(r'@Operation\([^)]*summary\s*=\s*["\']([^"\']+)["\']', content[:match.start()])
                    if operation_match:
                        operation_summary = operation_match.group(1)
                    
                    full_path = f"{base_path}{path}".replace("//", "/")
                    
                    endpoint_info = {
                        "method": method_type.upper(),
                        "path": full_path,
                        "handler": method_name,
                        "requestParams": request_params,
                        "requestBody": request_body,
                        "responseType": response_type,
                        "description": operation_summary
                    }
                    
                    endpoints.append(endpoint_info)
    
    return endpoints