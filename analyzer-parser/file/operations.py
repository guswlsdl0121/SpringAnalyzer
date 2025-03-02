import os
import zipfile
import logging

class FileOperations:
    """파일 시스템 작업을 담당하는 클래스"""
    
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir
        self.logger = logging.getLogger("analyzer.file.operations")
    
    def create_project_dir(self, project_id):
        project_dir = os.path.join(self.temp_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)

        self.logger.debug(f"프로젝트 디렉토리 생성됨: {project_dir}")        
        return project_dir
    
    def save_zip_file(self, project_dir, project_id, file_data):
        zip_path = os.path.join(project_dir, f"{project_id}.zip")
        
        with open(zip_path, "wb") as f:
            f.write(file_data)

        self.logger.debug(f"ZIP 파일 저장됨: {zip_path}")
        return zip_path
    
    def extract_zip(self, zip_path, extract_dir):
        self.logger.info(f"ZIP 파일 압축 해제: {zip_path}")
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        
        self.logger.info(f"압축 해제 완료: {extract_dir}")
        return extract_dir