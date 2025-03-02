import logging
from flask import Flask
from config import Config
from file import file_service
from rabbitmq import rabbitmq_service

# 전역 로깅 설정
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # 로그 수준을 INFO로 설정 (DEBUG보다 적은 로그 출력)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

setup_logging()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 서비스 초기화 및 Flask 애플리케이션에 연결
    app.file_service = file_service
    app.rabbitmq_service = rabbitmq_service

    @app.teardown_appcontext
    def close_rabbitmq_connections(exception=None):
        app.rabbitmq_service.close()

    return app
