from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from tripmind_api.config import settings

# SQLAlchemy 인스턴스를 생성합니다.
db = SQLAlchemy()

def create_app():
    """
    Flask 애플리케이션을 생성하고 설정하는 팩토리 함수입니다.
    """
    app = Flask(__name__)
    
    # config.py의 settings 객체로부터 모든 설정을 로드합니다.
    app.config.from_object(settings)

    # --- Extensions 초기화 ---
    # 데이터베이스를 Flask 앱과 연결합니다.
    db.init_app(app)
    
    # CORS(Cross-Origin Resource Sharing) 설정
    # 프론트엔드(예: React, Vue)와의 API 통신을 허용합니다.
    CORS(app, supports_credentials=True, origins=settings.CORS_ORIGINS or "*")

    # --- Blueprint 등록 ---
    # routes 디렉토리에서 사용할 Blueprint들을 import 합니다.
    from .routes import trip_route, rates_route, map_route

    # URL Prefix를 사용하여 각 API 그룹을 구분합니다.
    # 1. 메인 여행 계획 API
    app.register_blueprint(trip_route.bp, url_prefix="/api/trip")
    
    # 2. 유틸리티 API (환율, 지도)
    app.register_blueprint(rates_route.bp, url_prefix="/api/rates")
    app.register_blueprint(map_route.bp, url_prefix="/api/map")


    @app.route("/health")
    def health_check():
        """애플리케이션이 정상적으로 실행 중인지 확인하는 간단한 엔드포인트."""
        return {"status": "ok", "message": "TripMind backend is running"}

    return app

