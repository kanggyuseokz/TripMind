import os
from dotenv import load_dotenv, find_dotenv

# TripMind/ 디렉토리의 최상위 .env 파일을 찾아 환경 변수를 로드합니다.
load_dotenv(find_dotenv())

class Settings:
    """MCP 서버가 사용하는 모든 환경 변수를 관리하는 클래스입니다."""
    
    # Weather API (OpenWeatherMap)
    OWM_API_KEY: str = os.getenv("OWM_API_KEY")

    # Map APIs
    GOOGLE_MAP_API_KEY: str = os.getenv("GOOGLE_MAP_API_KEY")
    KAKAO_REST_API_KEY: str = os.getenv("KAKAO_REST_API_KEY")
    
    # Booking API (RapidAPI)
    RAPID_API_KEY: str = os.getenv("RAPID_API_KEY")
    BOOKING_RAPID_HOST: str = os.getenv("BOOKING_RAPID_HOST")
    BOOKING_RAPID_BASE: str = os.getenv("BOOKING_RAPID_BASE")

# 다른 파일에서 from .config import settings 로 참조할 수 있도록 인스턴스를 생성합니다.
settings = Settings()

