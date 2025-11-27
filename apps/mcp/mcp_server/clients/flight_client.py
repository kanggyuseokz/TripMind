import httpx
from datetime import date
from ..config import settings

class FlightClientError(Exception):
    """항공권 API 클라이언트 관련 에러"""
    pass

class FlightClient:
    """
    RapidAPI Agoda API를 통해 항공권 데이터를 가져오는 클라이언트
    API 문서: /flights/search-roundtrip 및 /flights/auto-complete 명세 기반
    """

    def __init__(self):
        self.base_url = settings.RAPID_BASE
        self.headers = {
            "X-RapidAPI-Key": settings.RAPID_API_KEY,
            "X-RapidAPI-Host": settings.RAPID_HOST
        }

    async def _get_iata_code(self, client: httpx.AsyncClient, city_name: str) -> str | None:
        """
        도시 이름을 기반으로 Agoda API에서 IATA 공항/도시 코드를 찾습니다.
        Retrieval Path: /flights/auto-complete
        Path 1: data -> tripLocations -> code
        Path 2: data -> airports -> nearByAirports -> tripLocations -> code
        """
        url = f"{self.base_url}/flights/auto-complete"
        params = {"query": city_name}
        
        try:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            result = response.json()
            
            data_list = result.get("data", [])
            
            if isinstance(data_list, list) and len(data_list) > 0:
                first_match = data_list[0]
                
                # Path 1: data -> tripLocations -> code
                # tripLocations가 리스트인 경우와 딕셔너리인 경우를 모두 방어적으로 처리
                trip_locs = first_match.get("tripLocations")
                if trip_locs:
                    if isinstance(trip_locs, list) and len(trip_locs) > 0:
                        return trip_locs[0].get("code")
                    elif isinstance(trip_locs, dict):
                        return trip_locs.get("code")
                
                # Path 2: 기존 로직 유지 (fallback) - data -> code
                if first_match.get("code"):
                    return first_match.get("code")

                # Path 3: data -> airports -> nearByAirports ... (명세에 언급됨)
                # 복잡하므로 airports 리스트의 첫 번째 코드 사용 시도
                airports = first_match.get("airports")
                if airports and isinstance(airports, list) and len(airports) > 0:
                    return airports[0].get("code")
            
            return None
            
        except httpx.HTTPStatusError as e:
            print(f"Error fetching IATA code for '{city_name}': {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in IATA fetch: {e}")
            return None

    async def search_flights(self, origin: str, destination: str, start_date: date, end_date: date, pax: int):
        """
        왕복 항공권을 검색하고 결과를 반환합니다.
        Endpoint: /flights/search-roundtrip
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 1. IATA 코드 조회
            origin_code = await self._get_iata_code(client, origin)
            dest_code = await self._get_iata_code(client, destination)

            if not origin_code or not dest_code:
                print(f"IATA code not found: {origin}({origin_code}) -> {destination}({dest_code})")
                return [] 

            # 2. 항공권 검색
            url = f"{self.base_url}/flights/search-roundtrip"

            # 명세에 따른 파라미터 구성
            params = {
                "origin": origin_code,          # Required
                "destination": dest_code,       # Required
                "departureDate": start_date.isoformat(), # Required: YYYY-MM-DD
                "returnDate": end_date.isoformat(),      # Required: YYYY-MM-DD
                "adults": str(pax),             # Optional: Default 1
                "currency": "KRW",              # Optional: Default USD
                "language": "ko-kr",            # Optional: Default en-us
                "sort": "Best",                 # Optional: Default Best
                "limit": "20",                  # Optional: Default 20
                "page": "1"                     # Optional: Default 1
            }

            try:
                # 참고: 명세에 따르면 'meta->isCompleted=false'인 경우 폴링이 필요할 수 있으나,
                # 기본 요청으로 1차 시도합니다.
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                search_result = response.json()

                data = search_result.get("data", {})
                
                # 결과 파싱
                if data and data.get("bundles"):
                    results = data.get("bundles", [])
                    if not results:
                        return []

                    # 첫 번째 결과(Best flight) 선택
                    top_flight = results[0]
                    itinerary = top_flight.get("itineraries", [{}])[0]
                    itinerary_info = itinerary.get("itineraryInfo", {})

                    # 가격 정보 추출
                    price_data_currency = itinerary_info.get("price", {})
                    # 응답에 포함된 통화 코드를 동적으로 찾거나 기본값 KRW 사용
                    currency_code = next(iter(price_data_currency), "KRW").upper()
                    
                    price_data_display = price_data_currency.get(currency_code.lower(), {}).get("display", {})

                    # 총 가격 (모든 승객 포함)
                    price_total_info = price_data_display.get("perBook", {}).get("allInclusive")
                    
                    # 결과 반환용 객체 생성
                    return [{
                        "id": itinerary_info.get("id"),
                        "vendor": "Agoda Flights", 
                        "airline": "추천 항공편", 
                        "route": f"{origin} - {destination}",
                        "price_total": price_total_info, 
                        "currency": currency_code,
                        # 딥링크 URL이 API 응답에 명확치 않으므로 검색 결과 ID 포함
                        "deeplink_url": None 
                    }]
                else:
                    # 데이터가 없거나 아직 로딩 중일 수 있음 (meta check 생략)
                    return []

            except httpx.HTTPStatusError as e:
                print(f"Flight Search API Error: {e.response.text}")
                raise FlightClientError(f"Failed to search flights: {e}")
            except (KeyError, IndexError, TypeError, StopIteration) as e:
                print(f"Flight Parse Error: {e}")
                return []