from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from datetime import date

# 💡 AgodaClient를 포함한 모든 실제/가상 클라이언트를 임포트합니다.
from .clients.agoda_client import AgodaClient
from .clients.flight_client import FlightClient
from .clients.weather_client import WeatherClient
from .clients.poi_client import PoiClient

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
    agoda_client = AgodaClient()
    flight_client = FlightClient() # 현재 Mock
    weather_client = WeatherClient() # 현재 Mock
    poi_client = PoiClient() # 현재 Mock

    # --- 비동기 동시 호출 ---
    # 각 API를 호출하는 작업(Task) 목록을 만듭니다.
    tasks = [
        agoda_client.search_hotels(body.destination, body.start_date, body.end_date, body.party_size),
        flight_client.search_flights(body.origin, body.destination, body.start_date, body.end_date, body.party_size),
        weather_client.get_weather_forecast(body.destination, body.start_date, body.end_date),
        poi_client.search_pois(body.destination, body.is_domestic, body.preferred_style)
    ]
    
    # asyncio.gather를 사용하여 모든 작업을 동시에 실행하고 결과를 기다립니다.
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # --- 결과 취합 ---
    # 각 작업의 결과를 안전하게 분리합니다. (실패한 경우 None)
    hotel_result = results[0] if not isinstance(results[0], Exception) else None
    flight_result = results[1] if not isinstance(results[1], Exception) else None
    weather_result = results[2] if not isinstance(results[2], Exception) else None
    poi_result = results[3] if not isinstance(results[3], Exception) else None

    # 백엔드가 사용하기 좋은 형태로 최종 응답을 구성합니다.
    return {
        "hotel_quote": hotel_result,
        "flight_quote": flight_result[0] if flight_result else None, # 항공권은 리스트의 첫 항목을 반환
        "weather_info": weather_result,
        "poi_list": poi_result
    }

