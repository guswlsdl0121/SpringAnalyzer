import logging

logger = logging.getLogger("rabbitmq.callback")

class RabbitMQCallback:
    """RabbitMQ 메시지 콜백 처리를 담당하는 클래스"""
    
    def __init__(self, business_logic):
        self.business_logic = business_logic
    
    def on_message(self, ch, method, body):
        """RabbitMQ 메시지 콜백 핸들러"""
        try:
            logger.info(f"메시지 수신: routing_key={method.routing_key}")
            
            success = self.business_logic(body)
            
            if success:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info("메시지 처리 성공, ACK 전송")
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                logger.warning("메시지 처리 실패, NACK 전송 (requeue=True)")
                
        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)