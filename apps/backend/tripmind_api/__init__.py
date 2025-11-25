# backend/tripmind_api/__init__.py
from flask import Flask
from flask_cors import CORS
from .config import settings
from .extensions import db, migrate, jwt, cors

def create_app():
    """
    Flask 애플리케이션을 생성하고 설정하는 팩토리 함수입니다.
    """
    app = Flask(__name__)
    
    # 1. 설정 로드
    app.config.from_object(settings)
    
    # 2. DB 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3. 확장 도구 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # 4. 라우터(Blueprint) 등록
    # 💡 map_route를 포함하여 모든 라우터를 import 합니다.
    from .routes import trip_route, llm_route, auth_route, map_route
    
    app.register_blueprint(trip_route.bp, url_prefix="/api/trip")
    app.register_blueprint(llm_route.bp, url_prefix="/api/llm")
    app.register_blueprint(auth_route.bp, url_prefix="/api/auth")
    app.register_blueprint(map_route.bp, url_prefix="/api/map")

    # 5. DB 테이블 생성
    with app.app_context():
        from . import models
        db.create_all()

    @app.route("/health")
    def health_check():
        return {"status": "ok", "message": "TripMind backend is running"}

    return app