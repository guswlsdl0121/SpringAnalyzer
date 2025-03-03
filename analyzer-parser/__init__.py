import os
import logging
from flask import Flask
from config import Config
from file import file_service
from rabbitmq import rabbitmq_service

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.file_service = file_service
    app.rabbitmq_service = rabbitmq_service

    @app.teardown_appcontext
    def close_rabbitmq_connections(exception=None):
        app.rabbitmq_service.close()

    return app

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

setup_logging()