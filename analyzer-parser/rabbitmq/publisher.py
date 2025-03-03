import logging
import pika

logger = logging.getLogger("rabbitmq.publisher")

class RabbitMQPublisher:
    def __init__(self, channel, exchange_name):
        self.channel = channel
        self.exchange_name = exchange_name
    
    def publish(self, routing_key: str, message: str, content_type: str = "application/json") -> bool:
        """
        메시지를 지정된 라우팅 키로 발행
        
        Args:
            routing_key: 메시지 라우팅 키
            message: 발행할 메시지 내용 (JSON 문자열)
            content_type: 메시지 콘텐츠 타입
            
        Returns:
            bool: 발행 성공 여부
        """
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
    
    def publish_result(self, routing_key, message):
        """분석 결과 메시지 발행"""
        return self.publish(routing_key, message)