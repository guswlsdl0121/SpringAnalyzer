from dataclasses import dataclass

@dataclass
class ExtractionResult:
    success: bool
    project_id: str
    project_dir: str = None
    error: str = None