import logging

logger = logging.getLogger('rabbitmq.consumer')

class RabbitMQAsyncConsumer:
    def __init__(self, exchange_name, queue_name, routing_key, callback_function):
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.callback_function = callback_function
        self.channel = None
        self.consumer_tag = None
        
    def setup(self, channel):
        """채널이 준비되면 Exchange와 Queue 설정"""
        self.channel = channel
        
        # Exchange 선언
        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type='topic',
            durable=True,
            callback=self._on_exchange_declareok
        )
    
    def _on_exchange_declareok(self, _unused_frame):
        """Exchange 선언 성공 시 Queue 선언"""
        logger.info(f"Exchange '{self.exchange_name}' 선언 완료")
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            callback=self._on_queue_declareok
        )
    
    def _on_queue_declareok(self, _unused_frame):
        """Queue 선언 성공 시 바인딩 실행"""
        logger.info(f"Queue '{self.queue_name}' 선언 완료")
        self.channel.queue_bind(
            queue=self.queue_name,
            exchange=self.exchange_name,
            routing_key=self.routing_key,
            callback=self._on_bindok
        )
    
    def _on_bindok(self, _unused_frame):
        """바인딩 성공 시 메시지 소비 시작"""
        logger.info(f"Queue '{self.queue_name}'가 Exchange '{self.exchange_name}'에 바인딩됨")
        
        # QoS 설정 - 한 번에 하나의 메시지만 처리
        self.channel.basic_qos(
            prefetch_count=1,
            callback=self._on_qos_set
        )
    
    def _on_qos_set(self, _unused_frame):
        """QoS 설정 완료 시 소비 시작"""
        logger.info("QoS 설정 완료")
        self.consumer_tag = self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self._on_message,
            auto_ack=False
        )
        logger.info(f"Consumer '{self.consumer_tag}' 시작됨")
    
    def _on_message(self, channel, method, properties, body):
        """메시지 수신 시 처리 핸들러"""
        logger.info(f"메시지 수신: routing_key={method.routing_key}")
        
        try:
            # 메시지 처리
            success = self.callback_function(body)
            
            if success:
                channel.basic_ack(delivery_tag=method.delivery_tag)
                logger.info("메시지 처리 성공, ACK 전송")
            else:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                logger.warning("메시지 처리 실패, NACK 전송 (requeue=True)")
        except Exception as e:
            logger.error(f"메시지 처리 오류: {str(e)}", exc_info=True)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def stop(self):
        """소비 중지"""
        if self.channel and self.consumer_tag:
            self.channel.basic_cancel(self.consumer_tag)
            logger.info(f"Consumer '{self.consumer_tag}' 중지됨")