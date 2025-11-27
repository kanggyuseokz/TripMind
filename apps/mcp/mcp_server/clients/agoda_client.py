import re
import httpx
from datetime import date
from ..config import settings

class AgodaClientError(Exception):
    """Agoda API 클라이언트 관련 에러 정의"""
    pass

# 🚀 [핵심] 주요 도시 매핑 데이터
# 한글 도시명이 들어오면 API가 알아들을 수 있는 영어 이름이나 IATA 코드로 즉시 변환합니다.
CITY_MAPPING = {
    # 일본
    "도쿄": {"iata": "TYO", "en": "Tokyo"},
    "오사카": {"iata": "OSA", "en": "Osaka"},
    "후쿠오카": {"iata": "FUK", "en": "Fukuoka"},
    "삿포로": {"iata": "SPK", "en": "Sapporo"},
    "오키나와": {"iata": "OKA", "en": "Okinawa"},
    "교토": {"iata": "UKY", "en": "Kyoto"}, 
    
    # 한국
    "서울": {"iata": "SEL", "en": "Seoul"},
    "인천": {"iata": "ICN", "en": "Incheon"},
    "김포": {"iata": "GMP", "en": "Gimpo"},
    "부산": {"iata": "PUS", "en": "Busan"},
    "제주": {"iata": "CJU", "en": "Jeju"},
    
    # 동남아/기타
    "방콕": {"iata": "BKK", "en": "Bangkok"},
    "다낭": {"iata": "DAD", "en": "Da Nang"},
    "나트랑": {"iata": "CXR", "en": "Nha Trang"},
    "싱가포르": {"iata": "SIN", "en": "Singapore"},
    "홍콩": {"iata": "HKG", "en": "Hong Kong"},
    "타이베이": {"iata": "TPE", "en": "Taipei"},
    
    # 유럽/미주
    "파리": {"iata": "PAR", "en": "Paris"},
    "런던": {"iata": "LON", "en": "London"},
    "로마": {"iata": "ROM", "en": "Rome"},
    "뉴욕": {"iata": "NYC", "en": "New York"},
    "로스앤젤레스": {"iata": "LAX", "en": "Los Angeles"},
}

class AgodaClient:
    """
    RapidAPI Agoda API 통합 클라이언트 (Real Data Fetcher)
    """

    def __init__(self):
        self.base_url = settings.RAPID_BASE
        self.api_key = settings.RAPID_API_KEY
        self.host = settings.RAPID_HOST
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }

    def _sanitize_query(self, query: str) -> str:
        if not query: return ""
        query = re.sub(r'\([^)]*\)', '', query) # 괄호 제거
        query = re.split(r'[/,]', query)[0]     # 슬래시 앞부분만 사용
        return query.strip()

    def _get_mapped_info(self, city_name: str):
        """매핑된 도시 정보가 있는지 확인합니다."""
        sanitized_name = self._sanitize_query(city_name)
        # 1. 한글 이름 직접 매칭 (예: "오사카")
        if sanitized_name in CITY_MAPPING:
            return CITY_MAPPING[sanitized_name]
        # 2. 매핑 키에 포함된 경우 (예: "오사카시" -> "오사카")
        for key, val in CITY_MAPPING.items():
            if key in sanitized_name:
                return val
        return None

    # ==========================================
    # [Flight] 항공권 관련 메서드
    # ==========================================

    async def _get_iata_code(self, client: httpx.AsyncClient, city_name: str) -> str | None:
        if not city_name: return None

        # 1. IATA 코드 직접 입력 시 (예: ICN)
        iata_match = re.search(r'\b([A-Z]{3})\b', city_name)
        if iata_match:
            return iata_match.group(1)

        # 2. 매핑 데이터 사용 (가장 확실한 방법)
        mapped = self._get_mapped_info(city_name)
        if mapped:
            print(f"[AgodaClient] ✈️ Mapped IATA Code: '{city_name}' -> '{mapped['iata']}'")
            return mapped["iata"]

        # 3. API 검색 (Fallback)
        search_query = self._sanitize_query(city_name)
        url = f"{self.base_url}/flights/auto-complete"
        params = {"query": search_query}
        
        try:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code != 200: return None
            data_list = response.json().get("data", [])
            
            if data_list:
                first = data_list[0]
                if first.get("tripLocations"): return first["tripLocations"][0].get("code")
                if first.get("code"): return first.get("code")
                if first.get("airports"): return first["airports"][0].get("code")
            return None
        except:
            return None

    async def search_flights(self, origin: str, destination: str, start_date: date, end_date: date, pax: int = 1):
        print(f"[AgodaClient] ✈️ search_flights called: {origin} -> {destination}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            origin_code = await self._get_iata_code(client, origin)
            dest_code = await self._get_iata_code(client, destination)

            if not origin_code or not dest_code:
                print(f"[AgodaClient] ❌ Missing Flight Codes: {origin_code} -> {dest_code}")
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
                if response.status_code != 200: return []

                data = response.json().get("data", {})
                results = data.get("bundles", [])
                
                if not results: return []

                # 최저가 항공권 추출
                top_flight = results[0]
                itinerary = top_flight.get("itineraries", [{}])[0]
                itinerary_info = itinerary.get("itineraryInfo", {})
                
                price_info = itinerary_info.get("price", {})
                currency = next(iter(price_info), "KRW").upper()
                price_val = price_info.get(currency.lower(), {}).get("display", {}).get("perBook", {}).get("allInclusive")
                
                return [{
                    "id": itinerary_info.get("id"),
                    "vendor": "Agoda Flights", 
                    "airline": "추천 항공편", 
                    "route": f"{origin} - {destination}",
                    "price_total": price_val, 
                    "currency": currency,
                    "deeplink_url": None 
                }]
            except Exception as e:
                print(f"[AgodaClient] Flight Search Error: {e}")
                return []

    # ==========================================
    # [Hotel] 호텔 관련 메서드
    # ==========================================

    async def _get_city_id(self, client: httpx.AsyncClient, query: str) -> str | None:
        # 1. 매핑된 영어 이름 사용 (호텔 검색은 영어 도시명이 훨씬 정확함)
        mapped = self._get_mapped_info(query)
        search_query = mapped["en"] if mapped else self._sanitize_query(query)
        
        print(f"[AgodaClient] 🏨 Search City ID for: '{search_query}'")
        
        url = f"{self.base_url}/hotels/auto-complete"
        params = {"query": search_query, "language": "ko-kr"}
        
        try:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code != 200: return None
            data_list = response.json().get("data", [])
            
            if not data_list: return None

            for item in data_list:
                # 'city' 타입의 ID를 우선적으로 찾음
                if item.get("type", "").lower() == "city" and item.get("id"):
                    return str(item.get("id"))
            
            if data_list[0].get("id"):
                return str(data_list[0].get("id"))
            return None
        except:
            return None

    async def search_hotels(self, destination: str, start_date: date, end_date: date, pax: int = 2):
        print(f"[AgodaClient] 🏨 search_hotels called: {destination}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            city_id = await self._get_city_id(client, destination)
            if not city_id: 
                print(f"[AgodaClient] ❌ City ID not found for hotel: {destination}")
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
                if response.status_code != 200: return []
                    
                hotels = response.json().get("data", {}).get("hotels", [])
                if not hotels: return []

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
                print(f"[AgodaClient] Hotel Search Error: {e}")
                return []

    async def get_hotel_details(self, hotel_id: str, start_date: date, end_date: date, pax: int = 2):
        # 상세 조회 로직 (생략 없이 유지)
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
                data = response.json().get("data", {})
                
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