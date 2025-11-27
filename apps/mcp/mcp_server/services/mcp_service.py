import asyncio
import json
import re
from datetime import date
from typing import Dict, Any

# 클라이언트 임포트
from ..clients.poi_client import PoiClient
from ..clients.weather_client import WeatherClient
from ..clients.agoda_client import AgodaClient

class MCPService:
    def __init__(self):
        self.poi_client = PoiClient()
        self.weather_client = WeatherClient()
        self.agoda_client = AgodaClient()

    def _get_safe_value(self, obj: Any, key: str, default: Any = None) -> Any:
        """헬퍼 함수: 안전하게 값 추출"""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def _sanitize_price(self, price_raw: Any) -> int:
        """
        [프론트엔드 호환성] 가격 데이터를 안전한 정수형(Integer)으로 변환합니다.
        "150,000" -> 150000
        120.50 -> 120
        """
        if not price_raw:
            return 0
        try:
            # 문자열인 경우 쉼표 제거
            if isinstance(price_raw, str):
                clean_str = re.sub(r'[^\d.]', '', price_raw) # 숫자와 점만 남김
                return int(float(clean_str))
            return int(price_raw)
        except:
            return 0

    async def generate_trip_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[MCP] generate_trip_data 진입.")
        
        # --- 1. 입력 데이터 파싱 ---
        try:
            if 'llm_parsed_data' in request_data:
                llm_data = request_data['llm_parsed_data'] if isinstance(request_data, dict) else getattr(request_data, 'llm_parsed_data')
                
                if isinstance(request_data, dict):
                    user_style = request_data.get("user_preferred_style", [])
                    request_id = request_data.get("request_id", "mcp-request")
                else:
                    user_style = getattr(request_data, "user_preferred_style", [])
                    request_id = getattr(request_data, "request_id", "mcp-request")
            else:
                llm_data = request_data
                if isinstance(request_data, dict):
                    user_style = request_data.get("user_preferred_style", [])
                else:
                    user_style = getattr(request_data, "user_preferred_style", [])
                request_id = "mcp-request"
            
            destination = self._get_safe_value(llm_data, 'destination')
            origin_raw = self._get_safe_value(llm_data, 'origin')
            origin = origin_raw if origin_raw else "Seoul"
            
            start_date_val = self._get_safe_value(llm_data, 'start_date')
            end_date_val = self._get_safe_value(llm_data, 'end_date')
            
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
        poi_task = self.poi_client.search_pois(
            destination=destination,
            is_domestic=is_domestic,
            category=user_style
        )
        
        weather_task = self.weather_client.get_weather_forecast(
            destination=destination, 
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        
        flight_task = self.agoda_client.search_flights(
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

        # --- 3. 동시 실행 ---
        print(f"[{request_id}] MCP: 모든 API 동시 호출 시작...")
        
        try:
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

        # --- 4. 결과 분류 및 정제 ---
        poi_data = results[0] if not isinstance(results[0], Exception) else []
        weather_data = results[1] if not isinstance(results[1], Exception) else {}
        flight_data_list = results[2] if not isinstance(results[2], Exception) else []
        hotel_data = results[3] if not isinstance(results[3], Exception) else []

        # [POI] 지도 호환성 패치 (lat/lng, latitude/longitude 모두 제공)
        normalized_poi_list = []
        for poi in poi_data:
            if isinstance(poi, dict):
                new_poi = poi.copy()
                # 프론트가 뭘 좋아할지 몰라 다 준비했습니다
                if 'lat' in new_poi: new_poi['latitude'] = new_poi['lat']
                if 'lng' in new_poi: new_poi['longitude'] = new_poi['lng']
                if 'latitude' in new_poi: new_poi['lat'] = new_poi['latitude']
                if 'longitude' in new_poi: new_poi['lng'] = new_poi['longitude']
                normalized_poi_list.append(new_poi)

        # [Flight] 가격 정수 변환 및 단일 객체 선택
        final_flight_quote = {}
        if flight_data_list:
            final_flight_quote = flight_data_list[0]
            # price_total을 숫자로 변환 (예: "550,000" -> 550000)
            if 'price_total' in final_flight_quote:
                final_flight_quote['price_total'] = self._sanitize_price(final_flight_quote['price_total'])
                # 혹시 프론트가 'price'라는 키를 찾을까봐 추가
                final_flight_quote['price'] = final_flight_quote['price_total']

        # [Hotel] 가격 정수 변환
        final_hotel_quote = []
        for hotel in hotel_data:
            clean_hotel = hotel.copy()
            if 'price' in clean_hotel:
                clean_hotel['price'] = self._sanitize_price(clean_hotel['price'])
            final_hotel_quote.append(clean_hotel)

        # --- 5. 최종 응답 ---
        response_data = {
            "destination": destination,
            "dates": {
                "start": start_date_obj.isoformat(),
                "end": end_date_obj.isoformat()
            },
            "trip_duration_nights": (end_date_obj - start_date_obj).days,
            "poi_list": normalized_poi_list,
            "weather_info": weather_data,
            "flight_quote": final_flight_quote,
            "hotel_quote": final_hotel_quote
        }
        
        # [디버그] 최종적으로 프론트엔드에 보내는 데이터 구조 확인
        # 이 로그를 복사해서 프론트엔드 코드와 비교해보세요!
        print(f"[{request_id}] MCP Final Response Keys: {list(response_data.keys())}")
        if final_flight_quote:
            print(f"[{request_id}] Flight Data Sample: {final_flight_quote}")
        else:
            print(f"[{request_id}] Flight Data is EMPTY!")
            
        if final_hotel_quote:
            print(f"[{request_id}] Hotel Data Sample (First): {final_hotel_quote[0]}")
        else:
            print(f"[{request_id}] Hotel Data is EMPTY!")
            
        return response_data

mcp_service_instance = MCPService()

def get_mcp_service():
    return mcp_service_instance