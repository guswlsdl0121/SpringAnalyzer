import logging
import pika

logger = logging.getLogger("rabbitmq.connection")

class RabbitMQConnection:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        
    def connect(self):
        try:
            # 연결 파라미터 설정
            credentials = pika.PlainCredentials(self.username, self.password)
            connection_params = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )
            
            # 서버 연결
            logger.info(f"RabbitMQ 서버 {self.host}:{self.port}에 연결 중...")
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            
            logger.info("RabbitMQ 서버에 연결되었습니다.")
            return self.channel
            
        except Exception as e:
            logger.error(f"RabbitMQ 연결 실패: {str(e)}", exc_info=True)
            return None
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ 연결이 종료되었습니다.")