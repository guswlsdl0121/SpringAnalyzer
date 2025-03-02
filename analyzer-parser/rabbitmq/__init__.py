from .connection import RabbitMQConnection
from .consumer import RabbitMQConsumer
from .service import RabbitMQService
from config import Config
from handler import message_handler

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
            message_handler.handle_analysis_message
        )
        # RabbitMQService 초기화
        rabbitmq_service = RabbitMQService(
            connection=rabbit_connection,
            config=Config,
            consumers=[analysis_consumer]
        )
    else:
        raise RuntimeError("Failed to get RabbitMQ channel.")
else:
    raise ConnectionError("Failed to connect to RabbitMQ.")

__all__ = ['rabbitmq_service']
