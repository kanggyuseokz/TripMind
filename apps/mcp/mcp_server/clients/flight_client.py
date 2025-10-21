import httpx
from datetime import date
import pprint
from ..config import settings

class FlightClientError(Exception):
    """항공권 API 클라이언트 관련 에러"""
    pass

class FlightClient:
    """RapidAPI의 Agoda API (Worldwide Hotels)를 사용하여 항공권 데이터를 가져오는 클라이언트"""
    
    def __init__(self):
        self.base_url = settings.BOOKING_RAPID_BASE
        self.headers = {
            "X-RapidAPI-Key": settings.RAPID_API_KEY,
            "X-RapidAPI-Host": settings.BOOKING_RAPID_HOST
        }

    async def _get_iata_code(self, client: httpx.AsyncClient, city_name: str) -> str | None:
        """도시 이름을 기반으로 항공에서 사용하는 IATA 공항 코드를 찾습니다."""
        url = f"{self.base_url}/flights/auto-complete"
        params = {"query": city_name, "language": "ko-kr"} # 'keyword' -> 'query' 수정
        try:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            result = response.json()
            
            # --- 💡 여기를 수정합니다 ---
            # 실제 응답 데이터 구조에 맞춰 IATA 코드를 정확히 추출합니다.
            if result and result.get("data"):
                data_list = result["data"]
                if data_list and isinstance(data_list, list):
                    # 리스트의 첫 번째 항목에서 도시의 대표 IATA 코드('code')를 반환합니다.
                    return data_list[0].get("code")
        except httpx.HTTPStatusError as e:
            print(f"Error fetching IATA code for '{city_name}': {e} - Response: {e.response.text}")
            return None
        return None

    async def search_flights(self, origin: str, destination: str, start_date: date, end_date: date, pax: int):
        """
        주어진 조건으로 왕복 항공권을 검색하고, 가장 적합한 추천 항공권 하나를 반환합니다.
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            origin_code = await self._get_iata_code(client, origin)
            dest_code = await self._get_iata_code(client, destination)

            if not origin_code or not dest_code:
                raise FlightClientError(f"Could not find IATA code for '{origin}' or '{destination}'")

            url = f"{self.base_url}/flights/search-roundtrip"
            params = {
                "origin_airport_iata": origin_code,
                "destination_airport_iata": dest_code,
                "outbound_date": start_date.isoformat(),
                "inbound_date": end_date.isoformat(),
                "adults": str(pax),
                "currency": "KRW",
                "country_code": "KR",
                "language": "ko-kr"
            }
            
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                search_result = response.json()
                
                # 디버깅을 위해 항공권 검색 결과도 출력해봅니다.
                print("\n--- [DEBUG] Agoda Flights 'search-roundtrip' API 응답 ---")
                pprint.pprint(search_result)
                print("---------------------------------------------------------")

                if search_result and search_result.get("results"):
                    top_flight = search_result["results"][0]
                    price_info = top_flight.get("price", {})

                    return [{
                        "id": top_flight.get("id"),
                        "vendor": "Agoda Flights",
                        "route": f"{origin} - {destination}",
                        "price_per_person": price_info.get("per_person"),
                        "price_total": price_info.get("total"),
                        "currency": "KRW",
                        "deeplink_url": top_flight.get("url")
                    }]
                else:
                     return []

            except httpx.HTTPStatusError as e:
                raise FlightClientError(f"Failed to search flights: {e.response.text}")
            except (KeyError, IndexError) as e:
                raise FlightClientError(f"Failed to parse flight search response: {e}")

