import logging
import javalang
from javalang.tree import ClassDeclaration, MethodDeclaration

logger = logging.getLogger("analyzer.parser.endpoint_analyzer")

class EndpointAnalyzer:
    """API 엔드포인트 분석 클래스"""
    
    def analyze(self, files_info):
        """컨트롤러에서 요청/응답 모델과 함께 API 엔드포인트 추출"""
        endpoints = []
        
        # 컨트롤러 파일 필터링 (더 넓은 범위로 검색)
        controller_files = [f for f in files_info if self._is_controller(f)]
        
        for controller in controller_files:
            extracted_endpoints = self.extract_endpoints_from_controller(controller)
            if extracted_endpoints:
                endpoints.extend(extracted_endpoints)
        
        logger.info(f"총 {len(endpoints)}개의 API 엔드포인트를 발견했습니다.")
        return endpoints
    
    def _is_controller(self, file_info):
        """컨트롤러 파일 여부 확인 (더 넓은 범위로 식별)"""
        # 기존 분류자가 이미 식별한 경우
        if file_info.get('file_type') == 'controller':
            return True
        
        # 파일명이나 경로에 Controller가 포함된 경우
        if 'Controller' in file_info.get('path', ''):
            return True
        
        # 내용에 @Controller 또는 @RestController가 포함된 경우
        content = file_info.get('content', '')
        if '@Controller' in content or '@RestController' in content:
            return True
            
        return False
    
    def extract_endpoints_from_controller(self, controller):
        """JavaParser를 사용하여 컨트롤러에서 엔드포인트 추출"""
        endpoints = []
        
        try:
            # Java 코드 파싱
            tree = javalang.parse.parse(controller['content'])
            
            # 클래스 선언 찾기
            for path, node in tree.filter(ClassDeclaration):
                # 컨트롤러 클래스인지 확인
                if not self._is_controller_class(node):
                    continue
                
                # 클래스 레벨 매핑 가져오기
                base_path = self._get_class_mapping(node)
                
                # 메서드 레벨 엔드포인트 추출
                for _, method_node in tree.filter(MethodDeclaration):
                    endpoint = self._process_method(method_node, base_path)
                    if endpoint:
                        endpoints.append(endpoint)
            
            return endpoints
            
        except Exception as e:
            logger.error(f"컨트롤러 파싱 오류: {controller['path']} - {str(e)}", exc_info=True)
            return []
    
    def _is_controller_class(self, class_node):
        """클래스가 컨트롤러인지 확인"""
        if not hasattr(class_node, 'annotations') or not class_node.annotations:
            return False
            
        for annotation in class_node.annotations:
            if annotation.name in ['Controller', 'RestController']:
                return True
                
        return False
    
    def _get_class_mapping(self, class_node):
        """클래스 레벨 RequestMapping 추출"""
        base_path = ""
        
        if not hasattr(class_node, 'annotations') or not class_node.annotations:
            return base_path
            
        for annotation in class_node.annotations:
            if annotation.name != 'RequestMapping':
                continue
                
            # 어노테이션 요소 추출
            if hasattr(annotation, 'element') and annotation.element:
                for element in annotation.element:
                    # value 또는 path 속성 찾기
                    if element[0] in ['value', 'path']:
                        if isinstance(element[1], list):
                            if element[1] and hasattr(element[1][0], 'value'):
                                base_path = element[1][0].value
                        elif hasattr(element[1], 'value'):
                            base_path = element[1].value
                        break
                        
        return base_path
    
    def _process_method(self, method_node, base_path):
        """메서드 노드에서 엔드포인트 정보 추출"""
        # 메서드에 매핑 어노테이션이 있는지 확인
        mapping_info = self._get_method_mapping(method_node)
        if not mapping_info:
            return None
            
        method_type, path = mapping_info
        
        # 전체 경로 구성
        full_path = self._combine_paths(base_path, path)
        
        # 요청 파라미터 추출
        request_params = self._extract_request_params(method_node)
        
        # 요청 바디 추출
        request_body = self._extract_request_body(method_node)
        
        # 응답 타입 추출
        response_type = method_node.return_type.name if hasattr(method_node, 'return_type') and method_node.return_type else "void"
        
        # 메서드 설명 추출 (Swagger/OpenAPI)
        description = self._extract_description(method_node)
        
        return {
            "method": method_type,
            "path": full_path,
            "handler": method_node.name,
            "requestParams": request_params,
            "requestBody": request_body,
            "responseType": response_type,
            "description": description
        }
    
    def _get_method_mapping(self, method_node):
        """메서드 레벨 매핑 어노테이션 처리"""
        if not hasattr(method_node, 'annotations') or not method_node.annotations:
            return None
            
        mapping_annotations = {
            'GetMapping': 'GET',
            'PostMapping': 'POST',
            'PutMapping': 'PUT',
            'DeleteMapping': 'DELETE',
            'PatchMapping': 'PATCH',
            'RequestMapping': None  # 별도 처리 필요
        }
        
        for annotation in method_node.annotations:
            if annotation.name not in mapping_annotations:
                continue
                
            # 기본 HTTP 메서드가 있는 매핑 처리
            if mapping_annotations[annotation.name]:
                path = self._extract_path_from_annotation(annotation)
                return mapping_annotations[annotation.name], path
                
            # RequestMapping 특별 처리
            elif annotation.name == 'RequestMapping':
                method_type = 'GET'  # 기본값
                
                # method 속성 찾기
                if hasattr(annotation, 'element') and annotation.element:
                    for element in annotation.element:
                        if element[0] == 'method':
                            # RequestMethod 열거형 처리
                            if hasattr(element[1], 'member') and element[1].member:
                                method_type = element[1].member
                            # 배열 형식 처리
                            elif isinstance(element[1], list) and element[1]:
                                if hasattr(element[1][0], 'member'):
                                    method_type = element[1][0].member
                
                path = self._extract_path_from_annotation(annotation)
                return method_type, path
                
        return None
    
    def _extract_path_from_annotation(self, annotation):
        """어노테이션에서 경로 추출"""
        path = ""
        
        if hasattr(annotation, 'element') and annotation.element:
            for element in annotation.element:
                # value, path 속성 탐색
                if element[0] in ['value', 'path']:
                    # 문자열 리터럴 처리
                    if hasattr(element[1], 'value'):
                        path = element[1].value
                    # 배열 처리
                    elif isinstance(element[1], list) and element[1]:
                        if hasattr(element[1][0], 'value'):
                            path = element[1][0].value
        
        return path
    
    def _combine_paths(self, base_path, path):
        """기본 경로와 메서드 경로 결합"""
        if not base_path:
            return path
        if not path:
            return base_path
            
        # 중복 슬래시 방지
        if base_path.endswith('/') and path.startswith('/'):
            return base_path + path[1:]
        elif not base_path.endswith('/') and not path.startswith('/'):
            return base_path + '/' + path
        else:
            return base_path + path
    
    def _extract_request_params(self, method_node):
        """메서드에서 @RequestParam 매개변수 추출"""
        params = []
        
        if not hasattr(method_node, 'parameters') or not method_node.parameters:
            return params
            
        for param in method_node.parameters:
            # 매개변수 어노테이션 확인
            request_param = False
            
            if hasattr(param, 'annotations') and param.annotations:
                for annotation in param.annotations:
                    if annotation.name == 'RequestParam':
                        request_param = True
                        break
            
            if request_param:
                params.append(param.name)
                
        return params
    
    def _extract_request_body(self, method_node):
        """메서드에서 @RequestBody 매개변수 추출"""
        if not hasattr(method_node, 'parameters') or not method_node.parameters:
            return None
            
        for param in method_node.parameters:
            # RequestBody 어노테이션 확인
            if hasattr(param, 'annotations') and param.annotations:
                for annotation in param.annotations:
                    if annotation.name == 'RequestBody':
                        # 타입 정보 포함
                        type_name = "Object"
                        if hasattr(param, 'type') and param.type:
                            if hasattr(param.type, 'name'):
                                type_name = param.type.name
                                
                        return f"{type_name} {param.name}"
                        
        return None
    
    def _extract_description(self, method_node):
        """메서드에서 설명 추출 (OpenAPI/Swagger)"""
        if not hasattr(method_node, 'annotations') or not method_node.annotations:
            return None
            
        for annotation in method_node.annotations:
            if annotation.name in ['Operation', 'ApiOperation']:
                if hasattr(annotation, 'element') and annotation.element:
                    for element in annotation.element:
                        if element[0] in ['summary', 'value'] and hasattr(element[1], 'value'):
                            return element[1].value
                            
        return None