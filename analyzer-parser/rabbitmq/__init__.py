import logging
import threading
from .connection import RabbitMQAsyncConnection
from .consumer import RabbitMQAsyncConsumer
from .publisher import RabbitMQAsyncPublisher
from config import Config
from message import message_processor

logger = logging.getLogger('rabbitmq')

# RabbitMQ 연결 설정
connection = RabbitMQAsyncConnection(
    Config.RABBITMQ_HOST,
    Config.RABBITMQ_PORT,
    Config.RABBITMQ_USER,
    Config.RABBITMQ_PASS
)

# 전역 변수로 사용할 객체들
publisher = None
analysis_consumer = None
connection_thread = None

def setup_rabbitmq(channel):
    """채널이 준비되면 호출되는 설정 함수"""
    global publisher, analysis_consumer
    
    # Publisher 초기화
    publisher = RabbitMQAsyncPublisher(
        exchange_name=Config.EXCHANGE_NAME
    )
    publisher.setup(channel)
    
    # Consumer 초기화
    analysis_consumer = RabbitMQAsyncConsumer(
        exchange_name=Config.EXCHANGE_NAME,
        queue_name=Config.ANALYSIS_QUEUE,
        routing_key=Config.ROUTING_ANALYSIS_UPLOAD,
        callback_function=message_processor.on_message
    )
    analysis_consumer.setup(channel)

def init_rabbitmq():
    """RabbitMQ 초기화 및 소비자 시작"""
    global connection_thread
    
    try:
        # 비동기 연결 시작
        if not connection.connect(on_channel_callback=setup_rabbitmq):
            logger.error("RabbitMQ 연결 실패")
            return False
        
        # 별도 스레드에서 이벤트 루프 실행
        connection_thread = threading.Thread(
            target=connection.run,
            daemon=True
        )
        connection_thread.start()
        
        logger.info("RabbitMQ 비동기 연결 시작됨")
        return True
        
    except Exception as e:
        logger.error(f"RabbitMQ 초기화 중 오류: {str(e)}", exc_info=True)
        return False

def publish_result(routing_key, message):
    """결과 메시지 발행 헬퍼 함수"""
    if publisher:
        return publisher.publish(routing_key, message)
    return False

def close_connections():
    """모든 RabbitMQ 연결 종료"""
    if analysis_consumer:
        analysis_consumer.stop()
    
    connection.stop()
    
    # 연결 스레드 종료 대기
    if connection_thread and connection_thread.is_alive():
        connection_thread.join(timeout=5.0)
        
    logger.info("RabbitMQ 연결 종료됨")

# 이 함수들을 외부로 노출
__all__ = ['init_rabbitmq', 'publish_result', 'close_connections']