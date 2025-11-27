import re
import httpx
from datetime import date
from ..config import settings

class AgodaClientError(Exception):
    """Agoda API 클라이언트 관련 에러 정의"""
    pass

class AgodaClient:
    """
    RapidAPI Agoda API 통합 클라이언트 (Final Version)
    - IATA 코드가 발견되면 API 조회를 건너뛰고 즉시 사용합니다.
    """

    def __init__(self):
        self.base_url = settings.RAPID_BASE
        self.api_key = settings.RAPID_API_KEY
        self.host = settings.RAPID_HOST
        
        # 설정 로드 확인용 로그
        masked_key = f"{self.api_key[:4]}****" if self.api_key else "None"
        print(f"[AgodaClient] Init - Host: {self.host}, Key: {masked_key}")

        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }

    def _sanitize_query(self, query: str) -> str:
        """
        검색어 정제: '오사카/간사이' -> '오사카'
        """
        if not query:
            return ""
        query = re.sub(r'\([^)]*\)', '', query) # 괄호 제거
        query = re.split(r'[/,]', query)[0]     # 슬래시 앞부분만 사용
        return query.strip()

    # ==========================================
    # [Flight] 항공권 관련 메서드
    # ==========================================

    async def _get_iata_code(self, client: httpx.AsyncClient, city_name: str) -> str | None:
        if not city_name:
            return None

        # 🚀 [핵심 수정] 입력값에 IATA 코드(3글자 대문자)가 있으면 바로 사용!
        # API 호출 없이 즉시 리턴하므로 'No IATA code found' 에러가 날 틈이 없습니다.
        iata_match = re.search(r'\b([A-Z]{3})\b', city_name)
        if iata_match:
            code = iata_match.group(1)
            print(f"[AgodaClient] ⚡ Using extracted IATA Code directly: '{city_name}' -> '{code}'")
            return code

        # 코드가 없으면 정제 후 API 검색 (기존 로직)
        search_query = self._sanitize_query(city_name)
        print(f"[AgodaClient] 🔍 Searching IATA Code for: '{search_query}'...")
        
        url = f"{self.base_url}/flights/auto-complete"
        params = {"query": search_query}
        
        try:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code != 200:
                print(f"[AgodaClient] IATA Fetch Failed! Status: {response.status_code}")
                return None
                
            result = response.json()
            data_list = result.get("data", [])
            
            if isinstance(data_list, list) and len(data_list) > 0:
                first_match = data_list[0]
                
                # tripLocations -> code
                trip_locs = first_match.get("tripLocations")
                if trip_locs:
                    if isinstance(trip_locs, list) and len(trip_locs) > 0:
                        return trip_locs[0].get("code")
                    elif isinstance(trip_locs, dict):
                        return trip_locs.get("code")
                
                # code fallback
                if first_match.get("code"):
                    return first_match.get("code")

                # airports fallback
                airports = first_match.get("airports")
                if airports and isinstance(airports, list) and len(airports) > 0:
                    return airports[0].get("code")
            
            print(f"[AgodaClient] No IATA code found for {search_query}")
            return None
            
        except Exception as e:
            print(f"[AgodaClient] Error in _get_iata_code: {e}")
            return None

    async def search_flights(self, origin: str, destination: str, start_date: date, end_date: date, pax: int = 1):
        print(f"[AgodaClient] ✈️ search_flights called: {origin} -> {destination}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            origin_code = await self._get_iata_code(client, origin)
            dest_code = await self._get_iata_code(client, destination)

            if not origin_code or not dest_code:
                print(f"[AgodaClient] ❌ Missing Codes! Origin: {origin_code}, Dest: {dest_code}")
                return [] 

            url = f"{self.base_url}/flights/search-roundtrip"
            params = {
                "origin": origin_code,
                "destination": dest_code,
                "departureDate": start_date.isoformat(),
                "returnDate": end_date.isoformat(),
                "adults": str(pax),
                "currency": "KRW",
                "language": "ko-kr",
                "sort": "Best",
                "limit": "20",
                "page": "1"
            }

            try:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code != 200:
                    print(f"[AgodaClient] Flight Search Failed! Status: {response.status_code}")
                    return []

                search_result = response.json()
                data = search_result.get("data", {})
                
                if data and data.get("bundles"):
                    results = data.get("bundles", [])
                    print(f"[AgodaClient] ✅ Flight Search Success! Found {len(results)} bundles.")
                    
                    if not results:
                        return []

                    top_flight = results[0]
                    itinerary = top_flight.get("itineraries", [{}])[0]
                    itinerary_info = itinerary.get("itineraryInfo", {})
                    
                    price_data_currency = itinerary_info.get("price", {})
                    currency_code = next(iter(price_data_currency), "KRW").upper()
                    price_data_display = price_data_currency.get(currency_code.lower(), {}).get("display", {})
                    price_total_info = price_data_display.get("perBook", {}).get("allInclusive")
                    
                    return [{
                        "id": itinerary_info.get("id"),
                        "vendor": "Agoda Flights", 
                        "airline": "추천 항공편", 
                        "route": f"{origin} - {destination}",
                        "price_total": price_total_info, 
                        "currency": currency_code,
                        "deeplink_url": None 
                    }]
                else:
                    return []

            except Exception as e:
                print(f"[AgodaClient] Exception in search_flights: {e}")
                return []

    # ==========================================
    # [Hotel] 호텔 관련 메서드
    # ==========================================

    async def _get_city_id(self, client: httpx.AsyncClient, query: str) -> str | None:
        # 호텔은 City ID(숫자)가 필요하므로 검색이 필수입니다.
        # "오사카/간사이" -> "오사카"로 정제해서 검색
        search_query = self._sanitize_query(query)
        print(f"[AgodaClient] 🏨 Fetching City ID for: '{query}' -> '{search_query}'")
        
        url = f"{self.base_url}/hotels/auto-complete"
        params = {"query": search_query, "language": "ko-kr"}
        
        try:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code != 200:
                print(f"[AgodaClient] City ID Fetch Failed! Status: {response.status_code}")
                return None
                
            result = response.json()
            data_list = result.get("data", [])
            
            if not data_list:
                return None

            for item in data_list:
                if item.get("type", "").lower() == "city" and item.get("id"):
                    cid = str(item.get("id"))
                    print(f"[AgodaClient] ✅ Found City ID: {cid}")
                    return cid
            
            if data_list[0].get("id"):
                cid = str(data_list[0].get("id"))
                return cid
            return None
            
        except Exception as e:
            print(f"[AgodaClient] Error in _get_city_id: {e}")
            return None

    async def search_hotels(self, destination: str, start_date: date, end_date: date, pax: int = 2):
        print(f"[AgodaClient] search_hotels called: {destination}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            city_id = await self._get_city_id(client, destination)
            
            if not city_id:
                print(f"[AgodaClient] City ID not found for: {destination}")
                return []

            url = f"{self.base_url}/hotels/search"
            params = {
                "cityId": city_id,
                "checkIn": start_date.isoformat(),
                "checkOut": end_date.isoformat(),
                "adults": str(pax),
                "currency": "KRW",
                "language": "ko-kr",
                "sort": "bestSeller",
                "page": "1",
                "limit": "20"
            }

            try:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code != 200:
                    return []
                    
                search_result = response.json()
                data = search_result.get("data", {})
                hotels = data.get("hotels", [])
                
                print(f"[AgodaClient] ✅ Found {len(hotels)} hotels.")
                
                if not hotels:
                    return []

                parsed_hotels = []
                for hotel in hotels:
                    parsed_hotels.append({
                        "id": hotel.get("hotelId"),
                        "vendor": "Agoda Hotels",
                        "name": hotel.get("name"),
                        "location": destination,
                        "price": hotel.get("priceDisplay") or hotel.get("dailyRate") or "가격 정보 없음",
                        "currency": hotel.get("currency") or "KRW",
                        "rating": hotel.get("starRating"),
                        "image": hotel.get("image"),
                        "has_details": True
                    })
                    
                return parsed_hotels

            except Exception as e:
                print(f"[AgodaClient] Exception in search_hotels: {e}")
                return []

    async def get_hotel_details(self, hotel_id: str, start_date: date, end_date: date, pax: int = 2):
        # 기존 로직 유지
        url = f"{self.base_url}/hotels/details"
        params = {
            "hotelId": hotel_id,
            "checkIn": start_date.isoformat(),
            "checkOut": end_date.isoformat(),
            "adults": str(pax),
            "currency": "KRW",
            "language": "ko-kr"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code != 200: return None
                result = response.json()
                data = result.get("data", {})
                
                raw_images = data.get("images", [])
                processed_images = []
                for img in raw_images:
                    if isinstance(img, str): processed_images.append(img)
                    elif isinstance(img, dict):
                        img_url = img.get("url") or img.get("original") or img.get("link")
                        if img_url: processed_images.append(img_url)

                return {
                    "id": data.get("hotelId"),
                    "name": data.get("name"),
                    "address": data.get("address"),
                    "description": data.get("shortDescription") or data.get("description"),
                    "amenities": data.get("amenities", []),
                    "images": processed_images,
                    "rating": data.get("starRating"),
                    "reviews_score": data.get("reviewScore"),
                    "review_count": data.get("reviewCount"),
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude")
                }
            except:
                return None