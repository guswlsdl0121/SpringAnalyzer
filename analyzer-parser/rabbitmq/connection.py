import logging
import pika
from pika.adapters.select_connection import SelectConnection

logger = logging.getLogger("rabbitmq.connection")

class RabbitMQAsyncConnection:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        self.on_channel_callback = None
        self.ioloop = None
        
    def connect(self, on_channel_callback):
        """비동기 연결 수립"""
        try:
            self.on_channel_callback = on_channel_callback
            
            # 연결 파라미터 설정
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            logger.info(f"RabbitMQ 서버 {self.host}:{self.port}에 비동기 연결 시도 중...")
            
            # 비동기 연결 시작
            self.connection = SelectConnection(
                parameters=parameters,
                on_open_callback=self._on_connection_open,
                on_open_error_callback=self._on_connection_open_error,
                on_close_callback=self._on_connection_closed
            )
            
            # 이벤트 루프 시작
            self.ioloop = self.connection.ioloop
            return True
            
        except Exception as e:
            logger.error(f"RabbitMQ 연결 실패: {str(e)}", exc_info=True)
            return False
    
    def _on_connection_open(self, connection):
        """연결이 성공적으로 열렸을 때 호출되는 콜백"""
        logger.info("RabbitMQ 서버에 연결되었습니다.")
        self.connection.channel(on_open_callback=self._on_channel_open)
    
    def _on_connection_open_error(self, connection, error):
        """연결 열기 오류 발생 시 호출되는 콜백"""
        logger.error(f"RabbitMQ 연결 오류: {error}")
        self.reconnect()
    
    def _on_connection_closed(self, connection, reason):
        """연결이 닫힐 때 호출되는 콜백"""
        logger.warning(f"RabbitMQ 연결 종료됨: {reason}")
        self.reconnect()
    
    def _on_channel_open(self, channel):
        """채널이 성공적으로 열렸을 때 호출되는 콜백"""
        logger.info("RabbitMQ 채널이 열렸습니다.")
        self.channel = channel
        channel.add_on_close_callback(self._on_channel_closed)
        
        # 사용자 정의 콜백 실행
        if self.on_channel_callback:
            self.on_channel_callback(channel)
    
    def _on_channel_closed(self, channel, reason):
        """채널이 닫힐 때 호출되는 콜백"""
        logger.warning(f"RabbitMQ 채널 종료됨: {reason}")
        if self.connection and not self.connection.is_closed:
            self.connection.channel(on_open_callback=self._on_channel_open)
    
    def reconnect(self):
        """연결 재시도 로직"""
        if self.ioloop and self.ioloop.is_running:
            self.ioloop.stop()
        
        # 일정 시간 후 재연결 시도
        # 여기서 더 복잡한 백오프 로직을 구현할 수 있음
        import threading
        threading.Timer(5.0, self.connect, [self.on_channel_callback]).start()
    
    def stop(self):
        """연결 종료"""
        if self.connection and not self.connection.is_closed:
            logger.info("RabbitMQ 연결 종료 중...")
            self.connection.close()
            
        # 이벤트 루프 종료
        if self.ioloop and self.ioloop.is_running:
            self.ioloop.stop()
            
        logger.info("RabbitMQ 연결이 정상적으로 종료되었습니다.")

    def run(self):
        """이벤트 루프 시작"""
        if self.ioloop:
            self.ioloop.start()