import asyncio
from datetime import date
from ..schemas.plan import PlanRequest
from typing import Dict, Any

# --- 모든 클라이언트 임포트 ---
# (파일 경로는 실제 위치에 맞게 조정 필요)
from ..clients.poi_client import PoiClient
from ..clients.weather_client import WeatherClient
from ..clients.flight_client import FlightClient
from ..clients.agoda_client import AgodaClient

class TripService: # 👈 이름 변경 (PlanService -> TripService)
    def __init__(self):
        # --- 모든 클라이언트 인스턴스 생성 ---
        # (참고: 실제 운영 환경에서는 싱글톤이나 DI 프레임워크를 통해 관리하는 것이 좋습니다)
        self.poi_client = PoiClient()
        self.weather_client = WeatherClient()
        self.flight_client = FlightClient()
        self.agoda_client = AgodaClient()

    async def generate_trip_plan(self, request: PlanRequest) -> Dict[str, Any]:
        """
        여행 계획 생성을 위해 모든 API 클라이언트를 동시에 호출하고 결과를 취합합니다.
        """
        
        # --- 1. 모든 API 호출 작업을 태스크로 정의 ---
        # POI 검색 태스크 (기존 로직)
        poi_task = self.poi_client.search_pois(
            query=request.destination,
            language="ko" # 필요시 request에서 받도록 수정
        )
        
        # 👈 날씨 검색 태스크 (실제 코드로 변경)
        weather_task = self.weather_client.get_weather_forecast(
            destination=request.destination, # 'city' -> 'destination'
            start_date=request.start_date,
            end_date=request.end_date
        )
        # (날씨 클라이언트가 아직 준비되지 않았다면 임시 데이터로 대체)
        # weather_task = asyncio.create_task(asyncio.sleep(0, result={"temp": "25C", "condition": "맑음"})) # 👈 임시 코드 삭제


        # 👈 항공권 검색 태스크 (신규)
        flight_task = self.flight_client.search_flights(
            origin=request.origin,
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            pax=request.pax
        )
        
        # 👈 호텔 검색 태스크 (신규)
        hotel_task = self.agoda_client.search_hotels(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            pax=request.pax
        )

        # --- 2. 모든 태스크를 동시에 실행 (Non-blocking) ---
        print(f"[{request.request_id}] MCP: 모든 API 동시 호출 시작...")
        try:
            results = await asyncio.gather(
                poi_task,
                weather_task,
                flight_task,
                hotel_task,
                return_exceptions=True # 👈 하나의 API가 실패해도 나머지는 계속 진행
            )
        except Exception as e:
            print(f"[{request.request_id}] MCP: asyncio.gather 중 심각한 오류 발생: {e}")
            raise

        # --- 3. 결과 처리 ---
        # 예외가 발생했는지 확인하고 데이터를 분리합니다.
        poi_data = results[0] if not isinstance(results[0], Exception) else []
        weather_data = results[1] if not isinstance(results[1], Exception) else {}
        flight_data_list = results[2] if not isinstance(results[2], Exception) else []
        hotel_data = results[3] if not isinstance(results[3], Exception) else {}

        # 오류 로그 출력 (실제 운영 시에는 더 정교한 로깅 필요)
        if isinstance(results[0], Exception): print(f"[{request.request_id}] POI Error: {results[0]}")
        if isinstance(results[1], Exception): print(f"[{request.request_id}] Weather Error: {results[1]}")
        if isinstance(results[2], Exception): print(f"[{request.request_id}] Flight Error: {results[2]}")
        if isinstance(results[3], Exception): print(f"[{request.request_id}] Hotel Error: {results[3]}")

        # 항공권/호텔 클라이언트는 추천 항목 1개(또는 빈 객체)를 반환하도록 설계됨
        # flight_client는 리스트를 반환하므로 첫 번째 항목을 선택
        final_flight_quote = flight_data_list[0] if flight_data_list else {}
        final_hotel_quote = hotel_data # agoda_client는 이미 dict 또는 빈 dict를 반환

        # --- 4. 최종 응답 데이터 구성 ---
        response_data = {
            "destination": request.destination,
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat(),
            "trip_duration_nights": (request.end_date - request.start_date).days, # 👈 변수명 명확화
            "poi_quote": poi_data,
            "weather_quote": weather_data,
            "flight_quote": final_flight_quote, # 👈 이제 null 대신 데이터(또는 빈 dict)가 들어감
            "hotel_quote": final_hotel_quote     # 👈 이제 null 대신 데이터(또는 빈 dict)가 들어감
        }
        
        print(f"[{request.request_id}] MCP: 데이터 취합 완료. 메인 백엔드로 응답 전송.")
        return response_data

# FastAPI 의존성 주입(Dependency Injection)을 위한 함수
trip_service_instance = TripService() # 👈 이름 변경

def get_trip_service(): # 👈 이름 변경
    return trip_service_instance


