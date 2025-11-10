# mcp/mcp_server/services/mcp_service.py
import asyncio
from datetime import date
from ..schemas.plan import PlanRequest, LLMParsedData
from typing import Dict, Any

# --- 모든 클라이언트 임포트 ---
from ..clients.poi_client import PoiClient
from ..clients.weather_client import WeatherClient
from ..clients.flight_client import FlightClient
from ..clients.agoda_client import AgodaClient

class MCPService:
    def __init__(self):
        # --- 모든 클라이언트 인스턴스 생성 ---
        # (FastAPI의 Depends를 사용하면 더 효율적으로 관리할 수 있습니다)
        self.poi_client = PoiClient()
        self.weather_client = WeatherClient()
        self.flight_client = FlightClient()
        self.agoda_client = AgodaClient()

    async def generate_trip_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        여행 계획 생성을 위해 모든 API 클라이언트를 동시에 호출하고 결과를 취합합니다.
        메인 백엔드로부터 받은 딕셔너리(parsed_data)를 기반으로 작동합니다.
        """
        
        # --- 1. 입력 데이터 파싱 ---
        try:
            # Pydantic 모델을 사용하여 딕셔너리 유효성 검사 및 객체 변환
            # (plan_router.py에서 이미 1차 검증을 했지만, 서비스 단에서 명확히 함)
            request_model = PlanRequest(**request_data)
            llm_data = request_model.llm_parsed_data
            user_style = request_model.user_preferred_style
            
            # 클라이언트 호출에 필요한 변수 추출
            destination = llm_data.destination
            origin = llm_data.origin
            start_date_obj = date.fromisoformat(llm_data.start_date)
            end_date_obj = date.fromisoformat(llm_data.end_date)
            pax = llm_data.party_size
            is_domestic = llm_data.is_domestic
            
            # request_id는 로깅을 위해 사용 (옵션)
            request_id = request_data.get("request_id", "mcp-request")

        except Exception as e:
            print(f"[MCPService] 입력 데이터 파싱 오류: {e}")
            return {"error": f"Invalid input data: {e}"}

        # --- 2. 모든 API 호출 작업을 태스크로 정의 ---
        
        poi_task = self.poi_client.search_pois(
            destination=destination,
            is_domestic=is_domestic, # 👈 빠뜨렸던 인수 추가
            category=user_style
        )
        
        weather_task = self.weather_client.get_weather_forecast(
            destination=destination,
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        
        flight_task = self.flight_client.search_flights(
            origin=origin,
            destination=destination,
            start_date=start_date_obj,
            end_date=end_date_obj,
            pax=pax
        )
        
        hotel_task = self.agoda_client.search_hotels(
            destination=destination,
            start_date=start_date_obj,
            end_date=end_date_obj,
            pax=pax
        )

        # --- 3. 모든 태스크를 동시에 실행 (Non-blocking) ---
        print(f"[{request_id}] MCP: 모든 API 동시 호출 시작...")
        try:
            results = await asyncio.gather(
                poi_task,
                weather_task,
                flight_task,
                hotel_task,
                return_exceptions=True # 👈 하나의 API가 실패해도 나머지는 계속 진행
            )
        except Exception as e:
            print(f"[{request_id}] MCP: asyncio.gather 중 심각한 오류 발생: {e}")
            raise # 라우터에서 처리할 수 있도록 다시 raise

        # --- 4. 결과 처리 ---
        # 예외가 발생했는지 확인하고 데이터를 분리합니다.
        poi_data = results[0] if not isinstance(results[0], Exception) else []
        weather_data = results[1] if not isinstance(results[1], Exception) else {}
        flight_data_list = results[2] if not isinstance(results[2], Exception) else []
        hotel_data = results[3] if not isinstance(results[3], Exception) else {}

        # 오류 로그 출력
        if isinstance(results[0], Exception): print(f"[{request_id}] POI Error: {results[0]}")
        if isinstance(results[1], Exception): print(f"[{request_id}] Weather Error: {results[1]}")
        if isinstance(results[2], Exception): print(f"[{request_id}] Flight Error: {results[2]}")
        if isinstance(results[3], Exception): print(f"[{request_id}] Hotel Error: {results[3]}")

        final_flight_quote = flight_data_list[0] if flight_data_list else {}
        final_hotel_quote = hotel_data

        # --- 5. 최종 응답 데이터 구성 ---
        response_data = {
            "destination": destination,
            "start_date": start_date_obj.isoformat(),
            "end_date": end_date_obj.isoformat(),
            "trip_duration_nights": (end_date_obj - start_date_obj).days,
            "poi_list": poi_data,
            "weather_info": weather_data,
            "flight_quote": final_flight_quote,
            "hotel_quote": final_hotel_quote
        }
        
        print(f"[{request_id}] MCP: 데이터 취합 완료. 메인 백엔드로 응답 전송.")
        return response_data

# FastAPI 의존성 주입(Dependency Injection)을 위한 싱글톤 인스턴스
mcp_service_instance = MCPService()

def get_mcp_service():
    return mcp_service_instance