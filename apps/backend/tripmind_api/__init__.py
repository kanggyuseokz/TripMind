# backend/tripmind_api/__init__.py

from flask import Flask
from flask_cors import CORS
# 💡 1. extensions.py에서 'db' 인스턴스를 임포트합니다.
from .extensions import db
from .config import settings

def create_app():
    """
    Flask 애플리케이션을 생성하고 설정하는 팩토리 함수입니다.
    """
    app = Flask(__name__)
    
    # 2. config.py의 settings 객체로부터 모든 설정을 로드합니다.
    app.config.from_object(settings)
    
    # 💡 3. .env 파일의 DB_URL로 SQLAlchemy를 설정합니다.
    # (settings.DB_URL이 "mysql+pymysql://user:pass@host/dbname" 형식이어야 함)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 권장 옵션

    # --- Extensions 초기화 ---
    # 4. 'db' 인스턴스를 Flask 앱과 연결합니다.
    db.init_app(app)
    
    # 5. CORS 설정
    CORS(app, supports_credentials=True, origins=settings.CORS_ORIGINS or "*")

    # --- Blueprint 등록 ---
    # 6. routes 디렉토리에서 사용할 Blueprint들을 import 합니다.
    # (llm_route가 누락되어 추가합니다)
    from .routes import trip_route, rates, map_route, llm_route 

    app.register_blueprint(trip_route.bp, url_prefix="/api/trip")
    app.register_blueprint(rates.bp, url_prefix="/api/rates")
    app.register_blueprint(map_route.bp, url_prefix="/api/map")
    app.register_blueprint(llm_route.bp, url_prefix="/api/llm") # 👈 llm_route 등록

    # --- 💡 7. (매우 중요) DB 테이블 생성 ---
    # app 컨텍스트 내에서 models.py에 정의된 모든 테이블을 생성합니다.
    with app.app_context():
        # (models.py 파일이 import 되어 있어야 db.create_all()이 인식합니다)
        from . import models 
        db.create_all()

    @app.route("/health")
    def health_check():
        """애플리케이션이 정상적으로 실행 중인지 확인하는 간단한 엔드포인트."""
        return {"status": "ok", "message": "TripMind backend is running"}

    return app