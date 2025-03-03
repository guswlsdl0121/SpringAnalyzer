# app.py
from __init__ import create_app

if __name__ == "__main__":
    app = create_app()
    
    # Flask 애플리케이션 실행
    app.run(host="0.0.0.0", port=5000)