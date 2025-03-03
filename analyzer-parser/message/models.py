from dataclasses import dataclass
from typing import Optional

@dataclass
class AnalysisResult:
    project_id: str
    success: bool
    summary_file: Optional[str] = None
    analysis_file: Optional[str] = None
    files_processed: Optional[int] = None
    error: Optional[str] = None