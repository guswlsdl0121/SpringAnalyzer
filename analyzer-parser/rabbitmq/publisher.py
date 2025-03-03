import logging
import pika

logger = logging.getLogger("rabbitmq.publisher")

class RabbitMQPublisher:
    def __init__(self, channel, exchange_name):
        self.channel = channel
        self.exchange_name = exchange_name
        
        # exchange 선언
        self.channel.exchange_declare(
            exchange=self.exchange_name, 
            exchange_type='topic', 
            durable=True
        )
    
    def publish(self, routing_key: str, message: str, content_type: str = "application/json") -> bool:
        """메시지를 지정된 라우팅 키로 발행"""
        try:
            properties = pika.BasicProperties(
                content_type=content_type,
                delivery_mode=2  # 메시지 지속성 설정 (디스크에 저장)
            )
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=message,
                properties=properties
            )
            
            logger.info(f"메시지 발행 성공: routing_key={routing_key}")
            return True
            
        except Exception as e:
            logger.error(f"메시지 발행 실패: {str(e)}", exc_info=True)
            return False