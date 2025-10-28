import httpx
from datetime import date
# pprint는 더 이상 사용하지 않으므로 임포트 제거
# import pprint
from ..config import settings

class AgodaClientError(Exception):
    """Agoda API 클라이언트 관련 에러"""
    pass

class AgodaClient:
    """RapidAPI의 Agoda API (Worldwide Hotels)를 사용하여 호텔 데이터를 가져오는 클라이언트"""

    def __init__(self):
        self.base_url = settings.RAPID_BASE
        self.headers = {
            "X-RapidAPI-Key": settings.RAPID_API_KEY,
            "X-RapidAPI-Host": settings.RAPID_HOST
        }

    async def _get_location_id(self, client: httpx.AsyncClient, destination: str) -> str | None:
        """도시 이름을 기반으로 Agoda에서 사용하는 고유 Location ID를 찾습니다."""
        url = f"{self.base_url}/hotels/auto-complete"
        params = {"query": destination, "language": "ko-kr"}
        try:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            result = response.json()

            if result and result.get("data") and isinstance(result["data"], list) and len(result["data"]) > 0:
                 first_place = result["data"][0]
                 if first_place and isinstance(first_place, dict):
                      # 'id' 키가 지역 ID를 포함하고 있음 (예: '1_5085')
                      return first_place.get("id")
            return None

        except httpx.HTTPStatusError as e:
            # 에러 발생 시 간단한 로그 출력 (나중에 로깅 시스템으로 대체 고려)
            print(f"Error fetching location ID for '{destination}': {e} - Response: {e.response.text}")
            return None
        except (KeyError, IndexError, TypeError) as e:
             # 파싱 에러 시 간단한 로그 출력
             print(f"Error parsing location ID response for '{destination}': {e}")
             return None

    async def search_hotels(self, destination: str, start_date: date, end_date: date, pax: int) -> dict: # 반환 타입을 dict로 명시
        """
        주어진 조건으로 호텔을 검색하고, 가장 적합한 추천 호텔 하나를 딕셔너리 형태로 반환합니다.
        (/hotels/search-overnight 엔드포인트 사용)
        호텔을 찾지 못하면 빈 딕셔너리를 반환합니다.
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            location_id = await self._get_location_id(client, destination)
            if not location_id:
                raise AgodaClientError(f"Could not find a location ID for '{destination}'")

            url = f"{self.base_url}/hotels/search-overnight"

            params = {
                "id": location_id,
                "checkinDate": start_date.isoformat(),
                "checkoutDate": end_date.isoformat(),
                "adult": str(pax),
                "room": "1",
                "currency": "KRW",
                "language": "ko-kr",
                "sort": "Ranking,Desc" # 파라미터 문서 기준
            }

            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                search_result = response.json()

                # 정상 파싱 로직 시작
                if search_result and search_result.get("data") and search_result["data"].get("properties"):
                    properties = search_result["data"]["properties"]
                    if properties:
                        top_hotel = properties[0]
                        nights = (end_date - start_date).days

                        content = top_hotel.get("content", {})
                        enrichment = top_hotel.get("enrichment", {})
                        pricing = top_hotel.get("pricing", {})

                        hotel_name = content.get("informationSummary", {}).get("localeName") or content.get("informationSummary", {}).get("defaultName")

                        price_info = {}
                        currency_code = "KRW" # 기본값 설정
                        # 중첩된 구조에서 안전하게 가격 정보 접근
                        try:
                            room_pricing_info = pricing['offers'][0]['roomOffers'][0]['room']['pricing'][0]
                            price_info = room_pricing_info.get('price', {})
                            currency_code = room_pricing_info.get('currency', "KRW")
                        except (IndexError, KeyError, TypeError):
                             pass # 가격 정보가 없는 경우 기본값 사용

                        price_total = price_info.get('perBook', {}).get('inclusive', {}).get('chargeTotal')
                        price_per_night = price_info.get('perNight', {}).get('inclusive', {}).get('display')

                        rating = content.get("informationSummary", {}).get("rating")
                        review_count = content.get("reviews", {}).get("cumulative", {}).get("reviewCount")

                        photo_url = None
                        try:
                            if content.get("images", {}).get("hotelImages"):
                                photo_url = content["images"]["hotelImages"][0].get("urls", [{}])[0].get("value")
                        except (IndexError, KeyError, TypeError):
                             pass # 이미지 정보가 없는 경우 None 유지

                        deeplink_url = None # 상세 URL은 search-overnight 응답에 없음

                        # 1박당 가격 재계산 (displayPrice가 없을 경우 대비)
                        if price_per_night is None and price_total is not None and nights > 0:
                             price_per_night = round(price_total / nights)

                        return {
                            "id": top_hotel.get("propertyId"),
                            "vendor": "Agoda Hotels",
                            "name": hotel_name,
                            "nights": nights,
                            "pricePerNight": price_per_night,
                            "priceTotal": price_total,
                            "currency": currency_code,
                            "rating": rating,
                            "review_count": review_count,
                            "photo_url": photo_url,
                            "deeplink_url": deeplink_url
                        }
                    else: # properties 리스트가 비어있는 경우
                        return {} # 👈 None 대신 빈 딕셔너리 반환
                else: # 'data' 또는 'properties' 키가 없는 경우
                    return {} # 👈 None 대신 빈 딕셔너리 반환

            except httpx.HTTPStatusError as e:
                # 실제 운영 환경에서는 로깅 프레임워크 사용 권장
                print(f"HTTP Error during hotel search: {e.response.status_code} - {e.response.text}")
                raise AgodaClientError(f"Failed to search hotels: {e.response.text}")
            except (KeyError, IndexError, TypeError) as e:
                # 파싱 중 예외 발생 시 로깅
                # print(f"Error during hotel search parsing: {type(e).__name__} at line {e.__traceback__.tb_lineno}: {e}")
                # 파싱 에러 시에도 빈 딕셔너리 반환 (또는 필요시 에러 발생)
                print(f"Parsing error, returning empty dict: {e}")
                return {} # 👈 파싱 에러 시 빈 딕셔너리 반환 (필요시 AgodaClientError 발생 고려)

