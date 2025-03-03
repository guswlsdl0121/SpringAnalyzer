import logging
from flask import Flask
from config import Config
from rabbitmq import init_rabbitmq, close_connections

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_success = init_rabbitmq()
    if not init_success:
        app.logger.error("RabbitMQ 초기화 실패")
    
    @app.teardown_appcontext
    def close_rabbitmq_connections(exception=None):
        close_connections()

    return app

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

setup_logging()