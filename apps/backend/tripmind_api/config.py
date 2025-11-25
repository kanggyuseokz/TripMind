# backend/tripmind_api/config.py

import os
# find_dotenv를 import하여 .env 파일의 위치를 자동으로 찾도록 합니다.
from dotenv import load_dotenv, find_dotenv

# 현재 파일 위치에서부터 상위 디렉토리로 올라가며 .env 파일을 찾아 로드합니다.
# 이렇게 하면 최상위 TripMind/.env 파일을 읽을 수 있습니다.
load_dotenv(find_dotenv())

# 환경 변수 직접 로드 (클래스 내에서 사용하기 위함)
_DB_USER = os.getenv("DB_USER")
# ... (이하 나머지 코드는 이전과 동일합니다)
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
    
    # JWT 시크릿 키를 추가합니다. (.env 파일에서 JWT_SECURITY 또는 JWT_SECRET_KEY 값을 읽어옵니다)
    JWT_SECRET_KEY = os.getenv("JWT_SECURITY") or os.getenv("JWT_SECRET_KEY")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*") # 값이 없으면 모든 출처(*)를 허용

    # 디버그 모드는 .env에서 설정하거나 기본값 False를 사용합니다.
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ('true', '1', 't')
    
    # JSON 응답 시 한글 깨짐 방지
    JSON_AS_ASCII = False
    
    # =================================================================
    # 2. 데이터베이스 설정 (MySQL)
    # =================================================================
    # SQLAlchemy가 사용할 DB 연결 URI를 클래스 속성으로 정의합니다.
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{_DB_USER}:{_DB_PWD}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}?charset=utf8mb4"
    )

    DB_URL = os.getenv("DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 리소스를 절약하기 위해 권장되는 설정

    # =================================================================
    # 3. LLM 및 MCP 서버 설정
    # =================================================================
    # Gemini LLM API
    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
    
    # MCP 서버의 기본 URL (services/mcp_service.py에서 사용)
    MCP_PORT = os.getenv("MCP_PORT", "7000")
    MCP_BASE_URL = os.getenv("MCP_BASE_URL", f"http://localhost:{MCP_PORT}")

    # =================================================================
    # 4. 외부 API 설정
    # =================================================================
    # Exchange Rate API (한국수출입은행)
    EXCHANGE_BASE = os.getenv("EXCHANGE_BASE", "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON")
    EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")
    EXCHANGE_DATA_CODE = os.getenv("EXCHANGE_DATA_CODE", "AP01")

    # Map APIs
    GOOGLE_MAP_API_KEY = os.getenv("GOOGLE_MAP_API_KEY")
    KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
    
    # Weather API (OpenWeatherMap)
    OWM_API_KEY = os.getenv("OWM_API_KEY")

    # Booking API (RapidAPI)
    RAPID_API_KEY = os.getenv("RAPID_API_KEY")
    BOOKING_RAPID_HOST = os.getenv("BOOKING_RAPID_HOST")
    BOOKING_RAPID_BASE = os.getenv("BOOKING_RAPID_BASE")


# --- 환경별 설정 클래스 ---

class DevelopmentConfig(Config):
    """개발 환경 설정: 디버그 모드 활성화"""
    DEBUG = True
    # 로컬 DB나 테스트용 LLM 설정 등 개발 환경에 맞는 설정을 재정의할 수 있습니다.

class ProductionConfig(Config):
    """배포 환경 설정: 디버그 모드 비활성화 및 보안 강화"""
    DEBUG = False
    # 로깅 레벨 조정, SSL 적용 등 배포 환경에 필요한 설정을 추가합니다.


# --- settings 객체 생성 ---

# APP_ENV 환경 변수를 읽어 적절한 설정을 로드합니다.
# .env 파일에 APP_ENV=development 또는 APP_ENV=production 를 설정하세요.
# 설정하지 않으면 기본값으로 'development'를 사용합니다.
env = os.getenv('APP_ENV', 'development').lower()

if env == 'production':
    settings = ProductionConfig()
else:
    settings = DevelopmentConfig()

