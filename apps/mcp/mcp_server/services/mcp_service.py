import asyncio
from datetime import date
from typing import Dict, Any

# 스키마 임포트 (경로에 맞게 사용, 실패 시 pass)
try:
    from ..schemas.plan import PlanRequest
except ImportError:
    pass

# 클라이언트 임포트
from ..clients.poi_client import PoiClient
from ..clients.weather_client import WeatherClient
# 통합된 AgodaClient 임포트
from ..clients.agoda_client import AgodaClient

class MCPService:
    def __init__(self):
        # 각 API 클라이언트 초기화
        self.poi_client = PoiClient()
        self.weather_client = WeatherClient()
        self.agoda_client = AgodaClient()

    def _get_safe_value(self, obj: Any, key: str, default: Any = None) -> Any:
        """
        [헬퍼 함수] 데이터가 '딕셔너리(dict)'인지 '객체(Pydantic Model)'인지 확인하여
        에러 없이 안전하게 값을 추출합니다.
        """
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    async def generate_trip_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        여행 계획 생성을 위해 모든 API 클라이언트를 동시에 호출하고 결과를 취합합니다.
        asyncio.gather를 사용하여 병렬 처리를 수행합니다.
        """
        
        # --- 1. 입력 데이터 파싱 ---
        try:
            if 'llm_parsed_data' in request_data:
                request_model = PlanRequest(**request_data)
                llm_data = request_model.llm_parsed_data
                user_style = request_model.user_preferred_style
                request_id = request_data.get("request_id", "mcp-request")
            else:
                llm_data = request_data
                user_style = request_data.get("user_preferred_style", [])
                request_id = "mcp-request"
            
            # 헬퍼 함수를 사용하여 안전하게 값 추출
            destination = self._get_safe_value(llm_data, 'destination')
            origin = self._get_safe_value(llm_data, 'origin')
            
            start_date_val = self._get_safe_value(llm_data, 'start_date')
            end_date_val = self._get_safe_value(llm_data, 'end_date')
            
            # 날짜 문자열 -> date 객체 변환
            if isinstance(start_date_val, str):
                start_date_obj = date.fromisoformat(start_date_val)
            else:
                start_date_obj = start_date_val
                
            if isinstance(end_date_val, str):
                end_date_obj = date.fromisoformat(end_date_val)
            else:
                end_date_obj = end_date_val
            
            pax = self._get_safe_value(llm_data, 'party_size', 1)
            is_domestic = self._get_safe_value(llm_data, 'is_domestic', False)
            
        except Exception as e:
            print(f"[MCPService] 입력 데이터 파싱 오류: {e}")
            return {"error": f"Invalid input data: {e}"}

        # --- 2. 비동기 작업(Task) 정의 ---
        # 실제 API 호출은 아직 실행되지 않음 (coroutine 생성 단계)
        
        # [POI] 관광지 검색 Task
        # poi_client.py의 search_pois(destination, is_domestic, category) 호출
        poi_task = self.poi_client.search_pois(
            destination=destination,
            is_domestic=is_domestic,
            category=user_style
        )
        
        # [Weather] 날씨 정보 조회 Task
        # weather_client.py의 get_weather_forecast(destination, start_date, end_date) 호출
        # (이전 대화에서 city -> destination으로 수정 완료)
        weather_task = self.weather_client.get_weather_forecast(
            destination=destination, 
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        
        # [Flight] 항공권 검색 Task (AgodaClient 사용)
        flight_task = self.agoda_client.search_flights(
            origin=origin,
            destination=destination,
            start_date=start_date_obj,
            end_date=end_date_obj,
            pax=pax
        )
        
        # [Hotel] 호텔 검색 Task (AgodaClient 사용)
        hotel_task = self.agoda_client.search_hotels(
            destination=destination,
            start_date=start_date_obj,
            end_date=end_date_obj,
            pax=pax
        )

        # --- 3. 동시 실행 (Parallel Execution) ---
        print(f"[{request_id}] MCP: 모든 API 동시 호출 시작...")
        
        try:
            # await asyncio.gather: 모든 Task를 동시에 실행하고 기다립니다.
            results = await asyncio.gather(
                poi_task,
                weather_task,
                flight_task,
                hotel_task,
                return_exceptions=True
            )
        except Exception as e:
            print(f"[{request_id}] MCP: asyncio.gather 중 심각한 오류 발생: {e}")
            raise e

        # --- 4. 결과 분류 ---
        poi_data = results[0] if not isinstance(results[0], Exception) else []
        weather_data = results[1] if not isinstance(results[1], Exception) else {}
        flight_data_list = results[2] if not isinstance(results[2], Exception) else []
        hotel_data = results[3] if not isinstance(results[3], Exception) else []

        # 에러 로깅
        if isinstance(results[0], Exception): print(f"POI Error: {results[0]}")
        if isinstance(results[1], Exception): print(f"Weather Error: {results[1]}")
        if isinstance(results[2], Exception): print(f"Flight Error: {results[2]}")
        if isinstance(results[3], Exception): print(f"Hotel Error: {results[3]}")

        final_flight_quote = flight_data_list[0] if flight_data_list else {}
        final_hotel_quote = hotel_data

        # --- 5. 최종 응답 ---
        response_data = {
            "destination": destination,
            "dates": {
                "start": start_date_obj.isoformat(),
                "end": end_date_obj.isoformat()
            },
            "trip_duration_nights": (end_date_obj - start_date_obj).days,
            "poi_list": poi_data,
            "weather_info": weather_data,
            "flight_quote": final_flight_quote,
            "hotel_quote": final_hotel_quote
        }
        
        print(f"[{request_id}] MCP: 데이터 취합 완료.")
        return response_data

mcp_service_instance = MCPService()

def get_mcp_service():
    return mcp_service_instance