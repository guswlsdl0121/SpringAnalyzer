import logging
from file.operations import FileOperations
from file.models import ExtractionResult

class FileService:
    """파일 처리를 담당하는 서비스 클래스"""
    
    def __init__(self, temp_dir):
        self.file_ops = FileOperations(temp_dir)
        self.logger = logging.getLogger("analyzer.file.service")
    
    def extract_project(self, project_id, file_data):
        try:
            self.logger.info(f"프로젝트 처리 시작: {project_id}")
            
            # 프로젝트 디렉토리 구조 생성
            project_paths = self.file_ops.create_project_structure(project_id)
            
            # ZIP 파일 저장
            zip_path = self.file_ops.save_zip_file(project_paths, project_id, file_data)
            
            # ZIP 파일 압축 해제
            source_dir = self.file_ops.extract_zip(zip_path, project_paths['source_dir'])
            
            # 압축 해제 결과 생성
            return ExtractionResult(
                success=True,
                project_id=project_id,
                project_dir=str(project_paths['source_dir']),
                output_dir=str(project_paths['output_dir'])
            )
            
        except Exception as e:
            self.logger.error(f"파일 처리 오류: {str(e)}", exc_info=True)
            return ExtractionResult(
                success=False,
                project_id=project_id,
                error=str(e)
            )
    
    def cleanup_old_projects(self, days=7):
        """오래된 프로젝트 파일 정리"""
        self.file_ops.cleanup_old_projects(days_to_keep=days)