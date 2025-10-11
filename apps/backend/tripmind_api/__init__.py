from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 내부 모듈
from .config import SQLALCHEMY_DATABASE_URI
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    # ✅ .env 로드 (환경 변수)
    load_dotenv()

    # ✅ Flask 앱 생성
    app = Flask(__name__)

    # ✅ Flask Config 적용
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ✅ DB 초기화
    db.init_app(app)

    # ✅ CORS 설정 (프론트엔드 통신 허용)
    CORS(
        app,
        supports_credentials=True,
        origins=os.getenv("CORS_ORIGINS", "*"),  # 필요 시 도메인 제한
    )

    # ✅ Blueprint 등록
    from .routes.llm import bp as llm_bp
    from .routes.planner import bp as planner_bp
    from .routes.quotes import bp as quotes_bp
    from .routes.cost import bp as cost_bp

    app.register_blueprint(llm_bp,     url_prefix="/llm")
    app.register_blueprint(planner_bp, url_prefix="/planner")
    app.register_blueprint(quotes_bp,  url_prefix="/quotes")
    app.register_blueprint(cost_bp,    url_prefix="/cost")

    # ✅ 헬스체크
    @app.get("/health")
    def health():
        return {"ok": True, "status": "TripMind backend running"}

    return app