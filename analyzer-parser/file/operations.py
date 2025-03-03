import zipfile
import logging
import shutil
from datetime import datetime
from pathlib import Path

class FileOperations:    
    def __init__(self, temp_dir):
        self.temp_dir = Path(temp_dir)
        self.projects_dir = self.temp_dir / 'projects'
        self.logger = logging.getLogger("analyzer.file.operations")
    
    def create_project_structure(self, project_id):
        """프로젝트 작업을 위한 디렉토리 구조 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 프로젝트별 디렉토리 구조 생성
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / 'source'
        output_dir = project_dir / 'output'
        archive_dir = project_dir / 'archive'
        
        # 디렉토리 생성
        project_dir.mkdir(exist_ok=True)
        source_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        archive_dir.mkdir(exist_ok=True)
        
        self.logger.debug(f"프로젝트 디렉토리 구조 생성됨: {project_dir}")
        
        # 작업 경로 정보 반환
        return {
            'project_dir': project_dir,
            'source_dir': source_dir,
            'output_dir': output_dir,
            'archive_dir': archive_dir,
            'timestamp': timestamp
        }
    
    def save_zip_file(self, project_paths, project_id, file_data):
        """압축 파일을 아카이브 디렉토리에 저장"""
        timestamp = project_paths['timestamp']
        zip_filename = f"{timestamp}_{project_id}_raw.zip"
        zip_path = project_paths['archive_dir'] / zip_filename
        
        with open(zip_path, "wb") as f:
            f.write(file_data)

        self.logger.debug(f"ZIP 파일 저장됨: {zip_path}")
        return zip_path
    
    def extract_zip(self, zip_path, source_dir):
        """ZIP 파일 압축 해제"""
        self.logger.info(f"ZIP 파일 압축 해제: {zip_path}")
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(source_dir)
        
        self.logger.info(f"압축 해제 완료: {source_dir}")
        return source_dir
    
    def cleanup_old_projects(self, days_to_keep=7):
        """오래된 프로젝트 정리 (일정 기간 이상 지난 프로젝트 삭제)"""
        try:
            current_time = datetime.now()
            for project_dir in self.projects_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                    
                # 디렉토리 수정 시간 확인
                dir_modified_time = datetime.fromtimestamp(project_dir.stat().st_mtime)
                days_old = (current_time - dir_modified_time).days
                
                if days_old > days_to_keep:
                    self.logger.info(f"{days_old}일 지난 프로젝트 정리: {project_dir}")
                    shutil.rmtree(project_dir)
        except Exception as e:
            self.logger.error(f"프로젝트 정리 중 오류: {str(e)}")