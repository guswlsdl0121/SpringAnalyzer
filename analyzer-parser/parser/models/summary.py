# parser/models/summary.py
from datetime import datetime

class ProjectSummary:
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
        self.build_info["group"] = group or self.build_info["group"]
        self.build_info["version"] = version or self.build_info["version"]
        self.build_info["springBootVersion"] = spring_boot_version or self.build_info["springBootVersion"]
        self.build_info["javaVersion"] = java_version or self.build_info["javaVersion"]
    
    def update_component_counts(self, components):
        self.components = components
    
    def add_api_endpoint(self, method, path):
        self.api_endpoints["count"] += 1
        route = f"{method} {path}"
        if len(self.api_endpoints["routes"]) < 5:  # 최대 5개까지 저장
            self.api_endpoints["routes"].append(route)
    
    def add_business_object(self, name):
        self.business_objects["count"] += 1
        if len(self.business_objects["names"]) < 5:  # 최대 5개까지 저장
            self.business_objects["names"].append(name)
    
    def update_dependencies(self, dependencies):
        self.dependencies["count"] = len(dependencies)
        self.dependencies["topDeps"] = dependencies[:7] if dependencies else []  # 상위 7개
    
    def add_java_file_metrics(self, method_count, cyclomatic_complexity, file_path):
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