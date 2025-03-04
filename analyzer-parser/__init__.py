from flask import Flask
from flask_cors import CORS
from config import Config
from rabbitmq import init_rabbitmq, close_connections
from worker import worker_pool

def create_app():
    app = Flask(__name__)
    
    # CORS 설정을 앱 생성 직후에 적용
    CORS(app, resources={r"/*": {"origins": "*"}})
    
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

    @app.after_request
    def add_headers(response):
        # CORS 헤더 추가
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        
        # 캐싱 방지 헤더 추가
        response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        response.headers.add('Pragma', 'no-cache')
        response.headers.add('Expires', '0')
        
        return response

    # OPTIONS 요청에 대한 처리 추가
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        return '', 200
    return app