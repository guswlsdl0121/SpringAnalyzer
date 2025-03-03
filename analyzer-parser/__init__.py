from flask import Flask
from config import Config
from rabbitmq import init_rabbitmq, close_connections
from worker import worker_pool

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 작업자 풀 시작
    worker_pool.start()
    
    # RabbitMQ 초기화
    init_success = init_rabbitmq()
    if not init_success:
        app.logger.error("RabbitMQ 초기화 실패")
    
    @app.teardown_appcontext
    def cleanup(exception=None):
        close_connections()
        worker_pool.stop()

    return app