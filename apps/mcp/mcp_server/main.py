from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from datetime import date

# MCP가 사용할 각 API 클라이언트를 임포트합니다.
from .clients.booking_client import BookingClient
# from .clients.flight_client import FlightClient # 항공권 클라이언트 (별도 구현 필요)
# from .clients.weather_client import WeatherClient # 날씨 클라이언트 (별도 구현 필요)
# from .clients.poi_client import PoiClient # POI 클라이언트 (별도 구현 필요)

app = FastAPI(title="TripMind MCP - Multi-Content Provider")

class TripDataIn(BaseModel):
    """백엔드로부터 여행 계획에 필요한 모든 정보를 받는 모델"""
    origin: str
    destination: str
    is_domestic: bool
    start_date: date
    end_date: date
    party_size: int
    preferred_style: str = "관광"

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/gather-all")
async def gather_all_trip_data(body: TripDataIn):
    """
    여행에 필요한 항공, 숙소, 날씨, POI 등 모든 정보를
    비동기적으로 동시에 수집하여 반환합니다.
    """
    # 각 클라이언트 인스턴스 생성
    booking_client = BookingClient()
    # flight_client = FlightClient()
    # ... other clients

    # --- 비동기 동시 호출 ---
    # 각 API를 호출하는 작업(Task) 목록을 만듭니다.
    tasks = [
        booking_client.search_hotels(body.destination, body.start_date, body.end_date, body.party_size),
        # flight_client.search_flights(body.origin, body.destination, body.start_date, body.end_date, body.party_size),
        # weather_client.get_weather(body.destination),
        # poi_client.search_pois(body.destination, body.is_domestic)
    ]
    
    # asyncio.gather를 사용하여 모든 작업을 동시에 실행하고 결과를 기다립니다.
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # --- 결과 취합 ---
    # 각 작업의 결과를 분리합니다. (실패한 경우 에러 처리 포함)
    hotel_results = results[0] if not isinstance(results[0], Exception) else []
    # flight_results = results[1] if not isinstance(results[1], Exception) else []
    
    # TODO: 항공권 클라이언트가 아직 없으므로, 임시 Mock 데이터로 대체합니다.
    flight_results = [{
        "id": "F1_REAL", "vendor": "RealAir", "price": 380000, "currency": "KRW"
    }]

    return {
        "flight_quote": flight_results[0] if flight_results else None,
        "hotel_quote": hotel_results[0] if hotel_results else None,
        # "weather_info": weather_results,
        # "poi_list": poi_results
    }
