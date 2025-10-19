import httpx
from datetime import date
import pprint # 👈 디버깅을 위해 pprint를 임포트합니다.
from ..config import settings

class AgodaClientError(Exception):
    """Agoda API 클라이언트 관련 에러"""
    pass

class AgodaClient:
    """RapidAPI의 Agoda API (Worldwide Hotels)를 사용하여 호텔 데이터를 가져오는 클라이언트"""
    
    def __init__(self):
        self.base_url = settings.BOOKING_RAPID_BASE
        self.headers = {
            "X-RapidAPI-Key": settings.RAPID_API_KEY,
            "X-RapidAPI-Host": settings.BOOKING_RAPID_HOST
        }

    async def _get_location_id(self, client: httpx.AsyncClient, destination: str) -> str | None:
        """도시 이름을 기반으로 Agoda에서 사용하는 고유 Location ID를 찾습니다."""
        url = f"{self.base_url}/hotels/auto-complete"
        params = {"query": destination, "language": "ko-kr"}
        try:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            result = response.json()
            
            # --- 💡 디버깅 코드 추가 ---
            # Agoda 서버로부터 받은 원본 응답을 터미널에 출력합니다.
            print("\n--- [DEBUG] Agoda 'auto-complete' API 응답 ---")
            pprint.pprint(result)
            print("-------------------------------------------------")
            # --------------------------
            
            if result and isinstance(result, list) and len(result) > 0:
                # API 응답에서 cityId를 찾아 반환
                return result[0].get("cityId")
        except httpx.HTTPStatusError as e:
            print(f"Error fetching location ID for '{destination}': {e} - Response: {e.response.text}")
            return None
        return None

    async def search_hotels(self, destination: str, start_date: date, end_date: date, pax: int):
        """
        주어진 조건으로 호텔을 검색하고, 가장 적합한 추천 호텔 하나를 반환합니다.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            location_id = await self._get_location_id(client, destination)
            if not location_id:
                raise AgodaClientError(f"Could not find a location ID for '{destination}'")

            url = f"{self.base_url}/hotels/search-overnight"
            params = {
                "city_id": location_id,
                "checkin": start_date.isoformat(),
                "checkout": end_date.isoformat(),
                "adults": str(pax),
                "rooms": "1",
                "currency": "KRW",
                "language": "ko-kr",
                "sort_type": "POPULAR"
            }
            
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                search_result = response.json()
                
                if search_result and search_result.get("results"):
                    top_hotel = search_result["results"][0]
                    price_info = top_hotel.get("price", {})
                    nights = (end_date - start_date).days

                    return {
                        "id": top_hotel.get("hotel_id"),
                        "name": top_hotel.get("hotel_name"),
                        "nights": nights,
                        "pricePerNight": round(price_info.get("total", 0) / nights) if nights > 0 and price_info.get("total") else price_info.get("total", 0),
                        "priceTotal": price_info.get("total"),
                        "currency": price_info.get("currency"),
                        "rating": top_hotel.get("rating"),
                        "review_count": top_hotel.get("reviews"),
                        "photo_url": top_hotel.get("image_url"),
                        "deeplink_url": top_hotel.get("url")
                    }
                else:
                     return None

            except httpx.HTTPStatusError as e:
                raise AgodaClientError(f"Failed to search hotels: {e.response.text}")
            except (KeyError, IndexError) as e:
                raise AgodaClientError(f"Failed to parse hotel search response: {e}")

