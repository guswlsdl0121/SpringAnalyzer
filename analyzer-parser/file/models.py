from dataclasses import dataclass

@dataclass
class ExtractionResult:
    """압축 파일 해제 처리 결과 모델"""
    success: bool
    project_id: str
    project_dir: str = None
    error: str = None