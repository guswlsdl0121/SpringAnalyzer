import logging
from .connection import RabbitMQConnection
from .consumer import RabbitMQConsumer
from .publisher import RabbitMQPublisher
from config import Config
from message import message_processor

logger = logging.getLogger('rabbitmq')

# RabbitMQ 연결 설정
connection = RabbitMQConnection(
    Config.RABBITMQ_HOST,
    Config.RABBITMQ_PORT,
    Config.RABBITMQ_USER,
    Config.RABBITMQ_PASS
)

# 전역 변수로 사용할 객체들
channel = None
publisher = None
analysis_consumer = None

def init_rabbitmq():
    """RabbitMQ 초기화 및 소비자 시작"""
    global channel, publisher, analysis_consumer
    
    try:
        # 채널 연결
        channel = connection.connect()
        if not channel:
            logger.error("RabbitMQ 채널 연결 실패")
            return False
            
        # Publisher 초기화
        publisher = RabbitMQPublisher(
            channel=channel,
            exchange_name=Config.EXCHANGE_NAME
        )
        
        # Consumer 초기화 및 시작
        analysis_consumer = RabbitMQConsumer(
            channel=channel,
            exchange_name=Config.EXCHANGE_NAME,
            queue_name=Config.ANALYSIS_QUEUE,
            routing_key=Config.ROUTING_ANALYSIS_UPLOAD,
            callback_function=message_processor.on_message  # message_processor 인스턴스의 메서드 사용
        )
        
        # 소비자 시작
        if not analysis_consumer.start():
            logger.error("분석 소비자 시작 실패")
            return False
            
        logger.info("RabbitMQ 초기화 및 소비자 시작 완료")
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
    connection.close()
    logger.info("RabbitMQ 연결 종료됨")

# 이 함수들을 외부로 노출
__all__ = ['init_rabbitmq', 'publish_result', 'close_connections']