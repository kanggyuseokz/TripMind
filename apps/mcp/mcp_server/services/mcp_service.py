# mcp/mcp_server/services/mcp_service.py
import asyncio
from datetime import date, datetime

# 💡 모든 비동기(async def) 클라이언트를 임포트합니다.
from ..clients.agoda_client import AgodaClient, AgodaClientError
from ..clients.flight_client import FlightClient, FlightClientError
from ..clients.poi_client import PoiClient, PoiClientError
from ..clients.weather_client import WeatherClient, WeatherClientError

class MCPService:
    """
    MCP 서버의 핵심 로직.
    모든 외부 API(Agoda, Flight, POI, Weather)를 비동기 병렬로 호출하고 데이터를 수집/반환합니다.
    """
    def __init__(self):
        # 각 API 클라이언트의 인스턴스를 생성합니다. (모두 비동기)
        self.agoda_client = AgodaClient()
        self.flight_client = FlightClient()
        self.poi_client = PoiClient()
        self.weather_client = WeatherClient()

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

    async def generate_trip_data(self, request_data: dict) -> dict:
        """
        메인 백엔드로부터 받은 데이터를 기반으로 모든 외부 API를 병렬 호출합니다.
        """
        try:
            # 1. 요청 데이터 파싱
            llm_data = request_data.get("llm_parsed_data", {})
            style = request_data.get("user_preferred_style", "관광")

            destination = llm_data.get("destination")
            origin = llm_data.get("origin")
            start_date_str = llm_data.get("start_date")
            end_date_str = llm_data.get("end_date")
            pax = llm_data.get("party_size", 1)

            # 2. 날짜 객체 변환 (API 호출에 필요)
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            trip_duration_nights = (end_date - start_date).days

            # 3. 비동기 태스크 리스트 생성
            tasks = []

            # 항공권 검색 태스크
            tasks.append(
                self._safe_api_call(
                    self.flight_client.search_flights(
                        origin=origin,
                        destination=destination,
                        start_date=start_date,
                        end_date=end_date,
                        pax=pax
                    ),
                    default_value=[] # 실패 시 빈 리스트
                )
            )

            # 호텔 검색 태스크
            tasks.append(
                self._safe_api_call(
                    self.agoda_client.search_hotels(
                        destination=destination,
                        start_date=start_date,
                        end_date=end_date,
                        pax=pax,
                        nights=trip_duration_nights
                    ),
                    default_value={} # 실패 시 빈 딕셔너리
                )
            )

            # POI 검색 태스크
            tasks.append(
                self._safe_api_call(
                    self.poi_client.search_pois(
                        destination=destination,
                        category=style
                    ),
                    default_value=[] # 실패 시 빈 리스트
                )
            )

            # 날씨 검색 태스크
            tasks.append(
                self._safe_api_call(
                    self.weather_client.get_weather_forecast(
                        destination=destination,
                        start_date=start_date,
                        end_date=end_date
                    ),
                    default_value=None # 실패 시 None
                )
            )

            # 4. 모든 API를 병렬로 동시 실행
            print(f"[MCPService] MCP 데이터 수집 시작... (대상: {destination})")
            results = await asyncio.gather(*tasks)
            print("[MCPService] MCP 데이터 수집 완료.")

            # 5. 결과 매핑
            flight_quote_list = results[0]
            hotel_quote = results[1]
            poi_list = results[2]
            weather_info = results[3]
            
            # 항공권은 리스트 중 첫 번째 항목(가장 저렴한)을 선택
            flight_quote = flight_quote_list[0] if flight_quote_list else {}

            return {
                "flight_quote": flight_quote,
                "hotel_quote": hotel_quote,
                "poi_list": poi_list,
                "weather_info": weather_info,
                "trip_duration_nights": trip_duration_nights
            }

        except Exception as e:
            # 날짜 파싱 실패 등 로직 오류
            print(f"[MCPService] 데이터 생성 중 로직 오류: {e}")
            return {"error": str(e)}

# 서비스 인스턴스 생성 (라우터에서 주입받아 사용)
mcp_service_instance = MCPService()

