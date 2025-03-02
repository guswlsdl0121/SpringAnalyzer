import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # Flask 설정
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    
    # RabbitMQ 설정
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
    
    # Exchange 및 Queue 설정
    EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "analyzer.exchange")
    ANALYSIS_QUEUE = os.getenv("ANALYSIS_QUEUE", "analysis.queue")
    RESULT_QUEUE = os.getenv("RESULT_QUEUE", "result.queue")
    
    # 라우팅 키
    ROUTING_ANALYSIS_UPLOAD = os.getenv("ROUTING_ANALYSIS_UPLOAD", "analysis.upload")
    ROUTING_RESULT_COMPLETED = os.getenv("ROUTING_RESULT_COMPLETED", "result.completed")
    ROUTING_RESULT_ERROR = os.getenv("ROUTING_RESULT_ERROR", "result.error")
    
    # 임시 파일 저장 경로
    VENV_PATH = os.getenv("VIRTUAL_ENV", ".venv")
    TEMP_DIR = os.path.join(VENV_PATH, "temp")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# 환경에 따른 설정 선택
config_by_name = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig
}

# 기본 설정
default_config = config_by_name[os.getenv("FLASK_ENV", "dev")]