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