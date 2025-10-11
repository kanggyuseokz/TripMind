# backend/tripmind_api/config.py

import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 메모리에 로드합니다.
# 이 코드가 Flask 앱 초기화 전에 실행되도록 보장해야 합니다.
load_dotenv()

# 환경 변수 직접 로드 (클래스 내에서 사용하기 위함)
_DB_USER = os.getenv("DB_USER")
_DB_PWD = os.getenv("DB_PASSWORD")
_DB_HOST = os.getenv("DB_HOST")
_DB_PORT = os.getenv("DB_PORT", "3306")
_DB_NAME = os.getenv("DB_NAME")


class Config:
    """
    모든 Flask 설정 및 프로젝트 전역 변수를 관리하는 기본 클래스입니다.
    """
    # =================================================================
    # 1. Flask 기본 및 보안 설정
    # =================================================================
    SECRET_KEY = os.getenv("SECRET_KEY", "A_SUPER_SECRET_FALLBACK_KEY")
    
    # 디버그 모드는 .env에서 설정하거나 기본값 False를 사용합니다.
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ('true', '1', 't')
    
    # JSON 응답 시 한글 깨짐 방지 (app.py에도 있지만 여기에 두는 것이 관례)
    JSON_AS_ASCII = False
    
    # =================================================================
    # 2. 데이터베이스 설정 (MySQL)
    # =================================================================
    # SQLAlchemy가 사용할 DB 연결 URI를 클래스 속성으로 정의합니다.
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{_DB_USER}:{_DB_PWD}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 리소스를 절약하기 위해 권장되는 설정

    # =================================================================
    # 3. LLM 및 MCP 서버 설정
    # =================================================================
    # Hugging Face Router 설정
    HF_TOKEN = os.getenv("HF_TOKEN")
    HF_BASE_URL = os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1")
    HF_MODEL = os.getenv("HF_MODEL", "openai/gpt-oss-20b:nebius")
    
    # MCP 서버의 기본 URL (services/mcp_service.py에서 사용)
    MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://localhost:8000")

    # =================================================================
    # 4. 기타 API 키 (필요에 따라 추가)
    # =================================================================
    # EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY") 
    # WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# --- 환경별 설정 클래스 (선택 사항이지만 권장) ---

class DevelopmentConfig(Config):
    """개발 환경 설정: 디버그 모드 활성화"""
    DEBUG = True
    # 로컬 DB나 테스트용 LLM 설정 등 개발 환경에 맞는 설정을 재정의할 수 있습니다.

class ProductionConfig(Config):
    """배포 환경 설정: 디버그 모드 비활성화 및 보안 강화"""
    DEBUG = False
    # 로깅 레벨 조정, SSL 적용 등 배포 환경에 필요한 설정을 추가합니다.