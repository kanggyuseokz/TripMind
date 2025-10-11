# backend/app.py
import os
import logging
from dotenv import load_dotenv

# 1. .env 로드는 그대로 유지 (배포 환경에서 환경 변수 설정을 돕기 위함)
load_dotenv()

# 2. Flask 앱 팩토리를 정확한 내부 경로에서 가져옵니다.
# (이전 아키텍처의 main.py 또는 __init__.py에 create_app이 정의되어 있어야 함)
# 예: from apps.backend import create_app 
# 현재 구조에서는 'tripmind_api'가 앱 패키지 이름인 것으로 추정됩니다.
from tripmind_api import create_app 

# 로그 레벨을 환경 변수에서 가져와 설정
def configure_logging():
    # 로그 설정은 config.py에서 처리되는 것이 일반적이지만, 
    # __init__.py를 건드리기 싫다면 여기에 두어도 무방합니다.
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    # werkzeug 로깅 레벨 설정은 유지
    logging.getLogger("werkzeug").setLevel(os.getenv("WERKZEUG_LOG_LEVEL", level))

def build_app():
    """WSGI 서버(gunicorn/uwsgi)에서 import 하는 진입점."""
    configure_logging()
    
    # create_app() 호출 전에 설정 클래스를 명시적으로 로드하도록 수정할 필요는 없습니다.
    # create_app() 내부에서 config.py를 통해 환경 변수를 자동으로 로드하는 것이 일반적입니다.
    app = create_app() 

    # 한글 JSON 깨짐 방지 설정은 유지 (좋은 관례입니다)
    app.config.setdefault("JSON_AS_ASCII", False)

    return app

# WSGI 호환을 위해 모듈 레벨에 app 노출
app = build_app()

if __name__ == "__main__":
    # 로컬 실행용 코드는 유지
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"

    logging.getLogger(__name__).info(
        "Starting TripMind backend on http://%s:%s (debug=%s)", host, port, debug
    )
    app.run(host=host, port=port, debug=debug)