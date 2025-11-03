from pydantic import BaseModel
from datetime import date
from typing import List, Dict, Any, Optional

class PlanRequest(BaseModel):
    """
    여행 계획 생성을 요청할 때 MCP 서버로 전달되는 데이터 스키마입니다.
    """
    request_id: str # 메인 백엔드에서 생성한 고유 요청 ID
    destination: str # 목적지 (도시 이름, 예: "도쿄")
    origin: str      # 👈 항공권 검색을 위한 출발지 (예: "서울")
    start_date: date # 여행 시작일
    end_date: date   # 여행 종료일
    pax: int = 1     # 인원 수 (기본값 1명)
    # (추후 관심사, 예산 등 추가 가능)

# --- 참고용 응답 스키마 ---
# (실제로는 서비스 레이어에서 유연하게 dict로 반환합니다)

class FlightQuote(BaseModel):
    id: Optional[str] = None
    vendor: Optional[str] = None
    route: Optional[str] = None
    price_per_person: Optional[float] = None
    price_total: Optional[float] = None
    currency: Optional[str] = None
    deeplink_url: Optional[str] = None

class HotelQuote(BaseModel):
    id: Optional[int] = None
    vendor: Optional[str] = None
    name: Optional[str] = None
    nights: Optional[int] = None
    pricePerNight: Optional[float] = None
    priceTotal: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    photo_url: Optional[str] = None
    deeplink_url: Optional[str] = None

class PlanResponse(BaseModel):
    """
    MCP 서버가 모든 API 조회를 마친 후 메인 백엔드로 반환하는 데이터 스키마입니다.
    """
    destination: str
    start_date: date
    end_date: date
    trip_duration: int
    poi_quote: List[Dict[str, Any]]   # POI 정보 리스트
    weather_quote: Dict[str, Any] # 날씨 정보
    flight_quote: Optional[FlightQuote] = None # 👈 항공권 정보
    hotel_quote: Optional[HotelQuote] = None   # 👈 호텔 정보
