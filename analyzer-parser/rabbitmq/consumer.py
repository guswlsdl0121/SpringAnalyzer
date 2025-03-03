import logging
import threading

logger = logging.getLogger('rabbitmq.consumer')

class RabbitMQConsumer:
    def __init__(self, channel, exchange_name, queue_name, routing_key, callback_function):
        self.channel = channel
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.callback_function = callback_function
        self.is_consuming = False
        self.consume_thread = None
        
        # Exchange와 Queue 설정
        self.setup()

    def setup(self):
        """Exchange와 Queue를 선언하고 바인딩"""
        try:
            self.channel.exchange_declare(
                exchange=self.exchange_name, 
                exchange_type='topic', 
                durable=True
            )
            self.channel.queue_declare(
                queue=self.queue_name, 
                durable=True
            )
            self.channel.queue_bind(
                exchange=self.exchange_name, 
                queue=self.queue_name, 
                routing_key=self.routing_key
            )
            logger.info(f"Queue '{self.queue_name}'가 Exchange '{self.exchange_name}'에 바인딩됨")
        except Exception as e:
            logger.error(f"Queue 설정 실패: {str(e)}", exc_info=True)
            raise

    def message_handler(self, ch, method, properties, body):
        """RabbitMQ로부터 받은 메시지를 처리"""
        try:
            logger.info(f"메시지 수신: routing_key={method.routing_key}")
            success = self.callback_function(body)
            
            if success:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info("메시지 처리 성공, ACK 전송")
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                logger.warning("메시지 처리 실패, NACK 전송 (requeue=True)")
        except Exception as e:
            logger.error(f"메시지 처리 오류: {str(e)}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """메시지 소비 시작"""
        try:
            if self.is_consuming:
                logger.warning("이미 메시지 소비 중입니다")
                return
                
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.message_handler,
                auto_ack=False
            )
            
            # 별도 스레드에서 메시지 소비 시작
            self.consume_thread = threading.Thread(
                target=self._consume_loop,
                daemon=True
            )
            self.consume_thread.start()
            logger.info(f"'{self.queue_name}' 큐에서 메시지 소비 시작")
            
            return True
        except Exception as e:
            logger.error(f"메시지 소비 시작 실패: {str(e)}", exc_info=True)
            return False

    def _consume_loop(self):
        """메시지 소비 루프 실행"""
        self.is_consuming = True
        try:
            self.channel.start_consuming()
        finally:
            self.is_consuming = False

    def stop(self):
        """메시지 소비 중지"""
        if not self.is_consuming:
            return False
            
        try:
            self.channel.stop_consuming()
            if self.consume_thread and self.consume_thread.is_alive():
                self.consume_thread.join(timeout=5.0)
            logger.info(f"'{self.queue_name}' 큐 소비 중지됨")
            return True
        except Exception as e:
            logger.error(f"소비 중지 중 오류: {str(e)}", exc_info=True)
            return False