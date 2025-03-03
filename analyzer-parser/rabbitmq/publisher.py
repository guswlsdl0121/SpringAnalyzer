import logging
import pika

logger = logging.getLogger("rabbitmq.publisher")

class RabbitMQAsyncPublisher:
    def __init__(self, exchange_name):
        self.exchange_name = exchange_name
        self.channel = None
        self.is_ready = False
        self.message_queue = []  # 채널이 준비되기 전 메시지 저장용
    
    def setup(self, channel):
        """채널이 준비되면 Exchange 설정"""
        self.channel = channel
        
        # Exchange 선언
        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type='topic',
            durable=True,
            callback=self._on_exchange_declareok
        )
    
    def _on_exchange_declareok(self, _unused_frame):
        """Exchange 선언 성공 시 준비 완료 표시"""
        logger.info(f"Exchange '{self.exchange_name}' 선언 완료")
        self.is_ready = True
        
        # 대기 중인 메시지 발행
        if self.message_queue:
            logger.info(f"{len(self.message_queue)}개의 대기 메시지 발행 시작")
            for routing_key, message, content_type in self.message_queue:
                self.publish(routing_key, message, content_type)
            self.message_queue.clear()
    
    def publish(self, routing_key, message, content_type="application/json"):
        """메시지 발행"""
        if not self.is_ready or not self.channel:
            # 아직 준비되지 않았으면 대기열에 추가
            self.message_queue.append((routing_key, message, content_type))
            logger.info(f"채널 준비 전 메시지 대기: routing_key={routing_key}")
            return False
        
        try:
            properties = pika.BasicProperties(
                content_type=content_type,
                delivery_mode=2  # 메시지 지속성 설정
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