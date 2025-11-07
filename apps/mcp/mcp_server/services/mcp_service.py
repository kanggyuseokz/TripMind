# mcp/mcp_server/services/mcp_service.py
import asyncio
from datetime import date, datetime
from typing import Dict, Any

# --- 모든 클라이언트 임포트 ---
from ..clients.poi_client import PoiClient
from ..clients.weather_client import WeatherClient
from ..clients.flight_client import FlightClient
from ..clients.agoda_client import AgodaClient

# 💡 1. 라우터가 기대하는 'MCPService'로 클래스 이름 수정
class MCPService:
    def __init__(self):
        # --- 모든 클라이언트 인스턴스 생성 ---
        self.poi_client = PoiClient()
        self.weather_client = WeatherClient()
        self.flight_client = FlightClient()
        self.agoda_client = AgodaClient()

    async def _safe_api_call(self, coro, default_value=None):
        """
        API 호출을 안전하게 실행하고, 실패 시 기본값(None 또는 {})을 반환하는 래퍼 함수
        """
        try:
            return await coro
        except Exception as e:
            # API 호출 실패 시 에러 로그 출력 (나중에 logging 모듈로 대체)
            print(f"[MCPService] API 호출 실패: {e}")
            # flight_quote, hotel_quote 등은 빈 딕셔너리 반환, 나머지는 None 반환
            return default_value if default_value is not None else {}

    # 💡 2. 라우터가 호출하는 'generate_trip_data'로 함수 이름 수정
    # 💡 3. 라우터가 request.dict()를 통째로 넘기므로, 매개변수 수정
    async def generate_trip_data(self, request_data: dict) -> Dict[str, Any]:
        """
        여행 계획 생성을 위해 모든 API 클라이언트를 동시에 호출하고 결과를 취합합니다.
        """
        
        # --- 1. 라우터에서 받은 request_data(dict) 파싱 ---
        try:
            llm_data = request_data.get("llm_parsed_data", {})
            style = request_data.get("user_preferred_style", "관광")

            destination = llm_data.get("destination")
            origin = llm_data.get("origin")
            start_date_str = llm_data.get("start_date")
            end_date_str = llm_data.get("end_date")
            pax = llm_data.get("party_size", 1)

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            trip_duration_nights = (end_date - start_date).days
            
            if not all([destination, origin, start_date, end_date]):
                 raise ValueError("필수 파라미터(destination, origin, dates)가 누락되었습니다.")

        except Exception as e:
            print(f"[MCPService] 요청 데이터 파싱 오류: {e}")
            return {"error": f"Invalid request data: {e}"}

        # --- 2. 모든 API 호출 작업을 태스크로 정의 ---
        # 💡 4. 파싱한 변수(destination, style 등)를 사용하여 태스크 생성
        poi_task = self._safe_api_call(
            self.poi_client.search_pois(
                destination=destination,
                category=style
            ),
            default_value=[]
        )
        
        weather_task = self._safe_api_call(
            self.weather_client.get_weather_forecast(
                destination=destination,
                start_date=start_date,
                end_date=end_date
            ),
            default_value=None
        )

        flight_task = self._safe_api_call(
            self.flight_client.search_flights(
                origin=origin,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                pax=pax
            ),
            default_value=[]
        )
        
        hotel_task = self._safe_api_call(
            self.agoda_client.search_hotels(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                pax=pax,
                nights=trip_duration_nights
            ),
            default_value={}
        )

        # --- 3. 모든 태스크를 동시에 실행 (Non-blocking) ---
        # 💡 5. request_id가 없으므로 print문 수정
        print(f"[MCPService] MCP: 모든 API 동시 호출 시작... (대상: {destination})")
        
        results = await asyncio.gather(
            poi_task,
            weather_task,
            flight_task,
            hotel_task,
            return_exceptions=True # 👈 하나의 API가 실패해도 나머지는 계속 진행
        )
        
        print(f"[MCPService] MCP: 데이터 취합 완료. (대상: {destination})")

        # --- 4. 결과 처리 ---
        poi_data = results[0] if not isinstance(results[0], Exception) else []
        weather_data = results[1] if not isinstance(results[1], Exception) else {}
        flight_data_list = results[2] if not isinstance(results[2], Exception) else []
        hotel_data = results[3] if not isinstance(results[3], Exception) else {}

        # 오류 로그 출력 (라우터의 print문과 겹치지 않게 간단히)
        if isinstance(results[0], Exception): print(f"[MCPService] POI Error: {results[0]}")
        if isinstance(results[1], Exception): print(f"[MCPService] Weather Error: {results[1]}")
        if isinstance(results[2], Exception): print(f"[MCPService] Flight Error: {results[2]}")
        if isinstance(results[3], Exception): print(f"[MCPService] Hotel Error: {results[3]}")

        final_flight_quote = flight_data_list[0] if flight_data_list else {}
        final_hotel_quote = hotel_data

        # --- 5. 최종 응답 데이터 구성 ---
        response_data = {
            "destination": destination,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "trip_duration_nights": trip_duration_nights,
            "poi_list": poi_data,          # 💡 poi_quote -> poi_list 이름 변경 (백엔드와 일치)
            "weather_info": weather_data,  # 💡 weather_quote -> weather_info 이름 변경 (백엔드와 일치)
            "flight_quote": final_flight_quote,
            "hotel_quote": final_hotel_quote
        }
        
        return response_data

# 💡 6. 라우터가 기대하는 'mcp_service_instance'로 인스턴스 이름 수정
mcp_service_instance = MCPService()