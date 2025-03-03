from .connection import RabbitMQConnection
from .consumer import RabbitMQConsumer
from .publisher import RabbitMQPublisher
from .service import RabbitMQService
from config import Config
from message import message_processor

# RabbitMQConnection 초기화
rabbit_connection = RabbitMQConnection(
    Config.RABBITMQ_HOST,
    Config.RABBITMQ_PORT,
    Config.RABBITMQ_USER,
    Config.RABBITMQ_PASS
)

# RabbitMQConsumer 초기화
if rabbit_connection.connect():
    channel = rabbit_connection.get_channel()
    if channel:
        analysis_consumer = RabbitMQConsumer(
            channel,
            Config.EXCHANGE_NAME,
            Config.ANALYSIS_QUEUE,
            Config.ROUTING_ANALYSIS_UPLOAD,
            message_processor.process
        )
        
        # Publisher 객체 생성
        publisher = RabbitMQPublisher(
            channel,
            Config.EXCHANGE_NAME
        )
        
        # RabbitMQService 초기화 (publisher 포함)
        rabbitmq_service = RabbitMQService(
            connection=rabbit_connection,
            config=Config,
            consumers=[analysis_consumer],
            publisher=publisher
        )
        
        # 순환 참조 방지를 위해 message_processor에 rabbitmq_service 설정
        message_processor.set_rabbitmq_service(rabbitmq_service)
    else:
        raise RuntimeError("Failed to get RabbitMQ channel.")
else:
    raise ConnectionError("Failed to connect to RabbitMQ.")

__all__ = ['rabbitmq_service']