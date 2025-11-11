import httpx
from datetime import date
# pprint는 더 이상 사용하지 않으므로 임포트 제거
# import pprint
from ..config import settings

class FlightClientError(Exception):
    """항공권 API 클라이언트 관련 에러"""
    pass

class FlightClient:
    """RapidAPI의 Agoda API (Worldwide Hotels)를 사용하여 항공권 데이터를 가져오는 클라이언트"""

    def __init__(self):
        self.base_url = settings.RAPID_BASE
        self.headers = {
            "X-RapidAPI-Key": settings.RAPID_API_KEY,
            "X-RapidAPI-Host": settings.RAPID_HOST # RAPID_HOST -> BOOKING_RAPID_HOST 로 수정 (설정값 일치 확인 필요)
        }

    async def _get_iata_code(self, client: httpx.AsyncClient, city_name: str) -> str | None:
        """도시 이름을 기반으로 항공에서 사용하는 IATA 공항 코드를 찾습니다."""
        url = f"{self.base_url}/flights/auto-complete"
        params = {"query": city_name, "language": "ko-kr"}
        try:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            result = response.json()

            # --- 💡 디버깅 코드 제거 ---
            # print(f"\n--- [DEBUG] Agoda Flights 'auto-complete' API 응답 (Query: {city_name}) ---")
            # pprint.pprint(result)
            # print("-----------------------------------------------------------------")
            # --------------------------

            # 실제 응답 데이터 구조에 맞춰 IATA 코드를 정확히 추출합니다.
            if result and result.get("data"):
                data_list = result["data"]
                # 데이터가 비어있지 않고 리스트 형태인지 확인
                if data_list and isinstance(data_list, list):
                    # 첫 번째 항목에서 코드 추출 시도 (없으면 None 반환)
                    return data_list[0].get("code")
        except httpx.HTTPStatusError as e:
            # 에러 발생 시 로그는 남기는 것이 좋습니다. (print -> 로깅 시스템으로 변경 고려)
            print(f"Error fetching IATA code for '{city_name}': {e} - Response: {e.response.text}")
            return None
        # 정상 처리되었으나 코드를 찾지 못한 경우
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

            # API 서버가 요구하는 정확한 파라미터 이름으로 변경합니다.
            params = {
                "origin": origin_code,
                "destination": dest_code,
                "departureDate": start_date.isoformat(),
                "returnDate": end_date.isoformat(),
                "adults": str(pax),
                "currency": "KRW",
                "countryCode": "KR", # country_code -> countryCode (API 문서 재확인 필요)
                "language": "ko-kr",
                "sort": "Best"
            }

            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                search_result = response.json()

                # --- 💡 디버깅 코드 제거 ---
                # print("\n--- [DEBUG] Agoda Flights 'search-roundtrip' API 응답 (depth=3) ---")
                # pprint.pprint(search_result, depth=3)
                # print("---------------------------------------------------------")
                # print("\n--- [DEBUG] 'search-roundtrip' data.bundles[0]의 전체 구조 ---")
                # try:
                #     first_bundle = search_result.get("data", {}).get("bundles", [])[0]
                #     pprint.pprint(first_bundle)
                # except (IndexError, TypeError):
                #     print("ERROR: data.bundles[0]를 찾을 수 없습니다. 응답 구조를 확인하세요.")
                # print("----------------------------------------------------------------")
                # --------------------------

                # API 응답 구조에 맞게 데이터 추출
                data = search_result.get("data", {})
                if data and data.get("bundles"):
                    results = data.get("bundles", [])
                    if not results:
                        return [] # 검색 결과가 없으면 빈 리스트 반환

                    top_flight = results[0] # 가장 첫 번째 결과(bundle) 사용

                    # data.bundles[0].itineraries[0].itineraryInfo 경로에서 데이터 추출
                    # itineraries 리스트가 비어있을 경우를 대비하여 기본값 {} 제공
                    itinerary = top_flight.get("itineraries", [{}])[0]
                    itinerary_info = itinerary.get("itineraryInfo", {})

                    # 가격 정보 추출
                    price_data_currency = itinerary_info.get("price", {})
                    # 통화 코드는 price 객체의 키 (예: 'krw')
                    currency_code = next(iter(price_data_currency), "KRW").upper()
                    price_data_display = price_data_currency.get(currency_code.lower(), {}).get("display", {})

                    # 1인당 가격
                    price_data_avg_pax = price_data_display.get("averagePerPax", {})
                    price_per_person_info = price_data_avg_pax.get("allInclusive")

                    # 총 가격
                    price_data_per_book = price_data_display.get("perBook", {})
                    price_total_info = price_data_per_book.get("allInclusive")

                    # ID 추출
                    flight_id = itinerary_info.get("id")

                    # Deeplink URL (API 응답에 없으므로 None)
                    deeplink_url = None

                    # 결과 반환 (딕셔너리 리스트 형태)
                    return [{
                        "id": flight_id,
                        "vendor": "Agoda Flights",
                        "route": f"{origin} - {destination}",
                        "price_per_person": price_per_person_info,
                        "price_total": price_total_info,
                        "currency": currency_code,
                        "deeplink_url": deeplink_url
                    }]
                else:
                    # 데이터 구조가 예상과 다르거나 bundles가 없는 경우
                    return []

            except httpx.HTTPStatusError as e:
                # API 호출 자체가 실패한 경우 에러 발생
                raise FlightClientError(f"Failed to search flights: {e.response.text}")
            except (KeyError, IndexError, TypeError, StopIteration) as e: # StopIteration 추가 (next(iter(...)) 대비)
                # 응답 데이터 파싱 중 에러 발생 시
                raise FlightClientError(f"Failed to parse flight search response: {e}")

