# analyzer/rabbitmq/consumer.py

import logging
import threading

logger = logging.getLogger('rabbitmq.consumer')

class RabbitMQConsumer:
    def __init__(self, channel, exchange_name, queue_name, routing_key, message_handler):
        self.channel = channel
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.message_handler = message_handler
        
        self.is_consuming = False
        self.consume_thread = None

    def setup(self):
        try:
            self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic', durable=True)
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=self.routing_key)
            
            logger.info(f"Exchange '{self.exchange_name}'와 Queue '{self.queue_name}' 설정 완료")
            
            return True
        
        except Exception as e:
            logger.error(f"Exchange/Queue 설정 중 오류 발생: {str(e)}", exc_info=True)
            return False

    def consume_loop(self):
        try:
            self.is_consuming = True
            
            def callback(ch, method, body):
                success = self.message_handler(body)
                
                if success:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"ACK 전달 완료")
                else:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    logger.warning(f"NACK 전달 (재큐)")
            
            self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=False)
            
            logger.info(f"Queue '{self.queue_name}' 소비 시작")
            
            self.channel.start_consuming()
        
        except Exception as e:
            logger.error(f"소비 중 예외 발생: {str(e)}", exc_info=True)
        
        finally:
            self.is_consuming = False

    def start(self):
        if not self.setup():
            return False
        
        self.consume_thread = threading.Thread(target=self.consume_loop, daemon=True)
        self.consume_thread.start()
        
        return True

    def stop(self):
        if not self.is_consuming:
            return False
        
        try:
            self.channel.stop_consuming()
            
            logger.info("소비 중단 완료")
            
            return True
        
        except Exception as e:
            logger.error(f"소비 중단 중 오류 발생: {str(e)}", exc_info=True)
            
            return False
