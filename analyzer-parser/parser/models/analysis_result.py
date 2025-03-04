from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class BasicInfo:
    group: str = "N/A"
    version: str = "N/A"
    springBootVersion: str = "N/A"
    javaVersion: str = "N/A"

@dataclass
class Architecture:
    typicalFlows: List[str] = field(default_factory=list)
    componentCounts: Dict[str, int] = field(default_factory=dict)

@dataclass
class ProjectSummaryData:
    name: str
    generated: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    basicInfo: BasicInfo = field(default_factory=BasicInfo)
    architecture: Architecture = field(default_factory=Architecture)
    readme: Optional[str] = None

@dataclass
class EndpointData:
    method: str
    path: str
    handler: str
    description: Optional[str] = None
    requestParams: List[str] = field(default_factory=list)
    requestBody: Optional[str] = None
    responseType: Optional[str] = None

@dataclass
class ApiData:
    endpoints: List[EndpointData] = field(default_factory=list)

@dataclass
class FieldData:
    name: str
    type: str
    annotations: List[str] = field(default_factory=list)

@dataclass
class RelationshipData:
    fromClass: str
    toClass: str
    type: str
    field: Optional[str] = None

@dataclass
class BusinessObjectData:
    name: str
    type: str
    fields: List[FieldData] = field(default_factory=list)
    relationships: List[RelationshipData] = field(default_factory=list)

@dataclass
class DomainData:
    businessObjects: List[BusinessObjectData] = field(default_factory=list)

@dataclass
class BusinessLogicMethod:
    name: str
    summary: str

@dataclass
class EndpointFlow:
    method: str
    flow: str

@dataclass
class DataFlow:
    controller: str
    endpoints: List[EndpointFlow] = field(default_factory=list)

@dataclass
class SourceFile:
    path: str
    package: str
    content: str
    fileType: Optional[str] = None
    className: Optional[str] = None
    complexity: Optional[Dict[str, Any]] = None
    javadocs: List[str] = field(default_factory=list)
    todos: List[str] = field(default_factory=list)

@dataclass
class ProjectAnalysisResult:
    projectSummary: ProjectSummaryData
    api: ApiData = field(default_factory=ApiData)
    domain: DomainData = field(default_factory=DomainData)
    projectStructure: Dict[str, List[str]] = field(default_factory=dict)
    relationships: List[Dict[str, str]] = field(default_factory=list)
    businessLogic: Dict[str, List[BusinessLogicMethod]] = field(default_factory=dict)
    dataFlows: List[DataFlow] = field(default_factory=list)
    springFeatures: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, str] = field(default_factory=dict)
    sourceFiles: List[SourceFile] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """객체를 사전 형태로 변환"""
        return asdict(self)
    
    def to_json(self, indent=2) -> str:
        """객체를 JSON 문자열로 변환"""
        import json
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save_to_file(self, file_path):
        """분석 결과를 JSON 파일로 저장"""
        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)