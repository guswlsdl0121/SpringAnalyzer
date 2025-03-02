# rabbitmq/connection.py
import logging
import pika

logger = logging.getLogger("rabbitmq.connection")

class RabbitMQConnection:
    """RabbitMQ 서버와의 연결을 관리하는 클래스"""
    
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        
    def connect(self):
        """RabbitMQ 서버에 연결하고 채널을 생성합니다."""
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
            return True
            
        except Exception as e:
            logger.error(f"RabbitMQ 연결 실패: {str(e)}", exc_info=True)
            return False
    
    def get_channel(self):
        """연결된 채널을 반환합니다."""
        if not self.channel or self.connection.is_closed:
            if not self.connect():
                return None
        return self.channel
    
    def close(self):
        """연결을 종료합니다."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ 연결이 종료되었습니다.")