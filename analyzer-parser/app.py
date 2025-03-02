from __init__ import create_app

if __name__ == "__main__":
    app = create_app()

    # RabbitMQ 소비자 시작
    app.rabbitmq_service.start_all_consumers()

    # Flask 애플리케이션 실행
    app.run(host="0.0.0.0", port=5000)
