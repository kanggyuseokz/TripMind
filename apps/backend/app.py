# backend/app.py
import os
import logging
from dotenv import load_dotenv, find_dotenv

# 1. 프로젝트 루트의 .env 파일을 찾아 가장 먼저 로드합니다.
load_dotenv(find_dotenv())

# 2. tripmind_api 패키지에서 애플리케이션 팩토리 함수를 가져옵니다.
from tripmind_api import create_app

# 3. 팩토리 함수를 호출하여 Flask app 객체를 생성합니다.
# 모든 설정(CORS, DB, Blueprint 등)은 create_app 내부에서 처리됩니다.
app = create_app()

# 4. `if __name__ == "__main__"` 블록은 로컬 개발 서버를 실행하기 위해 사용됩니다.
if __name__ == "__main__":
    # .env 또는 환경 변수에서 호스트, 포트, 디버그 설정을 읽어옵니다.
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "8080"))
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ('true', '1', 't')

    # Flask에 내장된 개발 서버를 실행합니다.
    app.run(host=host, port=port, debug=debug)