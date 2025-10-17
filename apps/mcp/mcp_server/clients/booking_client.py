import httpx
from datetime import date
from ..config import settings

class BookingClientError(Exception):
    """Booking.com API 클라이언트 관련 에러"""
    pass

class BookingClient:
    """RapidAPI를 통해 Booking.com 데이터를 가져오는 클라이언트"""
    
    def __init__(self):
        self.base_url = settings.BOOKING_RAPID_BASE
        self.headers = {
            "X-RapidAPI-Key": settings.RAPID_API_KEY,
            "X-RapidAPI-Host": settings.BOOKING_RAPID_HOST
        }

    async def _get_destination_id(self, client: httpx.AsyncClient, destination: str) -> str | None:
        """도시 이름을 기반으로 Booking.com에서 사용하는 고유 dest_id를 찾습니다."""
        url = f"{self.base_url}/v1/hotels/locations"
        params = {"name": destination, "locale": "ko"}
        try:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            locations = response.json()
            # 가장 관련성 높은 첫 번째 결과의 dest_id를 반환
            if locations:
                return locations[0].get("dest_id")
        except httpx.HTTPStatusError as e:
            print(f"Error fetching destination ID for '{destination}': {e}")
            return None
        return None

    async def search_hotels(self, destination: str, start_date: date, end_date: date, pax: int):
        """
        주어진 조건으로 호텔을 검색하고, 가장 적합한 추천 호텔 하나를 반환합니다.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            dest_id = await self._get_destination_id(client, destination)
            if not dest_id:
                raise BookingClientError(f"Could not find a destination ID for '{destination}'")

            url = f"{self.base_url}/v1/hotels/search"
            params = {
                "dest_id": dest_id,
                "order_by": "popularity",
                "filter_by_currency": "KRW",
                "locale": "ko",
                "checkin_date": start_date.isoformat(),
                "checkout_date": end_date.isoformat(),
                "adults_number": pax,
                "room_number": 1, # 간단한 검색을 위해 룸 1개로 고정
                "units": "metric",
                "dest_type": "city"
            }
            
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                search_result = response.json()
                
                # 검색 결과가 있고, 그 안에 호텔 목록이 있는지 확인
                if search_result and search_result.get("result"):
                    # 가장 인기 있는 호텔 (첫 번째 결과) 정보를 가공하여 반환
                    top_hotel = search_result["result"][0]
                    price_info = top_hotel.get("composite_price_breakdown", {})
                    total_price = price_info.get("gross_amount", {}).get("value")
                    nights = (end_date - start_date).days

                    return {
                        "id": top_hotel.get("hotel_id"),
                        "name": top_hotel.get("hotel_name"),
                        "nights": nights,
                        "pricePerNight": round(total_price / nights) if nights > 0 else total_price,
                        "priceTotal": total_price,
                        "currency": price_info.get("gross_amount", {}).get("currency", "KRW"),
                        "rating": top_hotel.get("review_score"),
                        "review_count": top_hotel.get("review_nr"),
                        "photo_url": top_hotel.get("max_photo_url"),
                        "deeplink_url": top_hotel.get("url")
                    }
                else:
                     return None # 검색 결과가 없는 경우

            except httpx.HTTPStatusError as e:
                raise BookingClientError(f"Failed to search hotels: {e.response.text}")
            except (KeyError, IndexError) as e:
                raise BookingClientError(f"Failed to parse hotel search response: {e}")

