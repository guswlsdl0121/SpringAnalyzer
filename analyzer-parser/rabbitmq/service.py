import logging

logger = logging.getLogger('rabbitmq.service')

class RabbitMQService:
    def __init__(self, connection, config, consumers):
        self.connection = connection
        self.config = config
        self.consumers = consumers

    def start_all_consumers(self):
        for consumer in self.consumers:
            if consumer.start():
                logger.info(f"소비자 {consumer.queue_name}가 성공적으로 시작되었습니다.")
            else:
                logger.error(f"소비자 {consumer.queue_name} 시작에 실패했습니다.")

    def stop_all_consumers(self):
        for consumer in self.consumers:
            consumer.stop()
        logger.info("모든 소비자가 중지되었습니다.")

    def close(self):
        self.stop_all_consumers()
        self.connection.close()
        logger.info("RabbitMQ 서비스가 종료되었습니다.")
