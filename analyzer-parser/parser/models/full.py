from datetime import datetime
import json

class FullData:
    def __init__(self, project_name):
        self.project_summary = {
            "name": project_name,
            "generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "basicInfo": {
                "group": "N/A",
                "version": "N/A",
                "springBootVersion": "N/A",
                "javaVersion": "N/A"
            },
            "architecture": {
                "typicalFlows": [],
                "componentCounts": {}
            },
            "readme": None
        }
        
        self.api = {
            "endpoints": []
        }
        
        self.domain = {
            "businessObjects": []
        }
        
        self.project_structure = {}
        self.relationships = []
        self.business_logic = {}
        self.data_flows = []
        self.spring_features = {
            "auto_configuration": [],
            "dependency_injection_patterns": [],
            "profiles": [],
            "properties_usage": [],
            "exception_handling": []
        }
        self.configuration = {}
        self.source_files = []
    
    def update_basic_info(self, group, version, spring_boot_version, java_version):
        """기본 프로젝트 정보 업데이트"""
        self.project_summary["basicInfo"]["group"] = group or self.project_summary["basicInfo"]["group"]
        self.project_summary["basicInfo"]["version"] = version or self.project_summary["basicInfo"]["version"]
        self.project_summary["basicInfo"]["springBootVersion"] = spring_boot_version or self.project_summary["basicInfo"]["springBootVersion"]
        self.project_summary["basicInfo"]["javaVersion"] = java_version or self.project_summary["basicInfo"]["javaVersion"]
    
    def update_architecture(self, typical_flows, component_counts):
        """아키텍처 정보 업데이트"""
        self.project_summary["architecture"]["typicalFlows"] = typical_flows
        self.project_summary["architecture"]["componentCounts"] = component_counts
    
    def set_readme(self, readme_content):
        """README 내용 설정"""
        self.project_summary["readme"] = readme_content
    
    def set_project_structure(self, structure):
        """프로젝트 구조 설정"""
        self.project_structure = structure
    
    def add_endpoint(self, method, path, handler, description=None, request_params=None, request_body=None, response_type=None):
        """API 엔드포인트 추가"""
        endpoint = {
            "method": method,
            "path": path,
            "handler": handler,
            "description": description,
            "requestParams": request_params or [],
            "requestBody": request_body,
            "responseType": response_type
        }
        self.api["endpoints"].append(endpoint)
    
    def add_business_object(self, name, type_name, fields=None, relationships=None):
        """비즈니스 객체 추가"""
        business_object = {
            "name": name,
            "type": type_name,
            "fields": fields or [],
            "relationships": relationships or []
        }
        self.domain["businessObjects"].append(business_object)
    
    def add_field(self, business_object_index, name, type_name, annotations=None):
        """비즈니스 객체에 필드 추가"""
        field = {
            "name": name, 
            "type": type_name,
            "annotations": annotations or []
        }
        self.domain["businessObjects"][business_object_index]["fields"].append(field)
    
    def add_relationship(self, business_object_index, from_class, to_class, type_name, field=None):
        """비즈니스 객체 관계 추가"""
        relationship = {
            "fromClass": from_class,
            "toClass": to_class,
            "type": type_name,
            "field": field
        }
        self.domain["businessObjects"][business_object_index]["relationships"].append(relationship)
    
    def set_relationships(self, relationships):
        """클래스 관계 설정"""
        self.relationships = relationships
    
    def add_business_logic(self, service_name, methods):
        """비즈니스 로직 추가"""
        self.business_logic[service_name] = [
            {"name": method["name"], "summary": method["summary"]} 
            for method in methods
        ]
    
    def add_data_flow(self, controller, endpoints):
        """데이터 흐름 추가"""
        data_flow = {
            "controller": controller,
            "endpoints": [
                {"method": endpoint["method"], "flow": endpoint["flow"]} 
                for endpoint in endpoints
            ]
        }
        self.data_flows.append(data_flow)
    
    def set_spring_features(self, features):
        """Spring Boot 특성 설정"""
        self.spring_features = features
    
    def update_configuration(self, config):
        """설정 정보 업데이트"""
        self.configuration.update(config)
    
    def add_source_file(self, path, package, content, file_type=None, class_name=None, complexity=None, javadocs=None, todos=None):
        """소스 파일 추가"""
        source_file = {
            "path": path,
            "package": package,
            "content": content,
            "fileType": file_type,
            "className": class_name,
            "complexity": complexity,
            "javadocs": javadocs or [],
            "todos": todos or []
        }
        self.source_files.append(source_file)
    
    def to_dict(self):
        """객체를 사전 형태로 변환"""
        return {
            "projectSummary": self.project_summary,
            "api": self.api,
            "domain": self.domain,
            "projectStructure": self.project_structure,
            "relationships": self.relationships,
            "businessLogic": self.business_logic,
            "dataFlows": self.data_flows,
            "springFeatures": self.spring_features,
            "configuration": self.configuration,
            "sourceFiles": self.source_files
        }
    
    def save_to_file(self, file_path):
        """분석 결과를 JSON 파일로 저장"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# parser/models/summary.py
from datetime import datetime
import json

class SummaryData:
    def __init__(self, project_name):
        self.project_name = project_name
        self.generated = datetime.now().isoformat()
        self.build_info = {
            "group": "N/A",
            "version": "N/A",
            "springBootVersion": "N/A",
            "javaVersion": "N/A"
        }
        self.components = {}
        self.api_endpoints = {
            "count": 0,
            "routes": []
        }
        self.business_objects = {
            "count": 0,
            "names": []
        }
        self.complexity_metrics = {
            "avg_method_count": 0,
            "avg_complexity": 0,
            "max_complexity": 0,
            "complex_files": ""
        }
        self.dependencies = {
            "count": 0,
            "topDeps": []
        }
        
        # 메서드 카운팅을 위한 통계 정보
        self._java_file_count = 0
        self._total_methods = 0
        self._total_complexity = 0
    
    def update_build_info(self, group, version, spring_boot_version, java_version):
        """빌드 정보 업데이트"""
        self.build_info["group"] = group or self.build_info["group"]
        self.build_info["version"] = version or self.build_info["version"]
        self.build_info["springBootVersion"] = spring_boot_version or self.build_info["springBootVersion"]
        self.build_info["javaVersion"] = java_version or self.build_info["javaVersion"]
    
    def update_component_counts(self, components):
        """컴포넌트 수 업데이트"""
        self.components = components
    
    def add_api_endpoint(self, method, path):
        """API 엔드포인트 추가"""
        self.api_endpoints["count"] += 1
        route = f"{method} {path}"
        if len(self.api_endpoints["routes"]) < 5:  # 최대 5개까지 저장
            self.api_endpoints["routes"].append(route)
    
    def add_business_object(self, name):
        """비즈니스 객체 추가"""
        self.business_objects["count"] += 1
        if len(self.business_objects["names"]) < 5:  # 최대 5개까지 저장
            self.business_objects["names"].append(name)
    
    def update_dependencies(self, dependencies):
        """의존성 정보 업데이트"""
        self.dependencies["count"] = len(dependencies)
        self.dependencies["topDeps"] = dependencies[:7] if dependencies else []  # 상위 7개
    
    def add_java_file_metrics(self, method_count, cyclomatic_complexity, file_path):
        """Java 파일 메트릭 추가"""
        self._java_file_count += 1
        self._total_methods += method_count
        self._total_complexity += cyclomatic_complexity
        
        # 최대 복잡도 갱신
        if cyclomatic_complexity > self.complexity_metrics["max_complexity"]:
            self.complexity_metrics["max_complexity"] = cyclomatic_complexity
            self.complexity_metrics["complex_files"] = file_path
        
        # 평균 메트릭 업데이트
        if self._java_file_count > 0:
            self.complexity_metrics["avg_method_count"] = round(self._total_methods / self._java_file_count, 2)
            self.complexity_metrics["avg_complexity"] = round(self._total_complexity / self._java_file_count, 2)
    
    def to_dict(self):
        """객체를 사전 형태로 변환"""
        return {
            "projectName": self.project_name,
            "generated": self.generated,
            "buildInfo": self.build_info,
            "components": self.components,
            "apiEndpoints": self.api_endpoints,
            "businessObjects": self.business_objects,
            "complexityMetrics": self.complexity_metrics,
            "dependencies": self.dependencies
        }
    
    def save_to_file(self, file_path):
        """요약 정보를 JSON 파일로 저장"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)