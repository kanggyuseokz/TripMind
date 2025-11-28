import re
import httpx
import json
import google.generativeai as genai  # 🚀 직접 import
from datetime import date
from ..config import settings

# ⚠️ 외부 LLMService import 제거 (경로 문제 해결)
# from backend.tripmind_api.services.llm_service import LLMService (X)

class AgodaClientError(Exception):
    """Agoda API 클라이언트 관련 에러 정의"""
    pass

class AgodaClient:
    """
    RapidAPI Agoda API 통합 클라이언트 (Standalone LLM Version)
    """

    def __init__(self):
        # Base URL 및 헤더 설정
        self.base_url = "https://agoda-com.p.rapidapi.com"
        self.api_key = settings.RAPID_API_KEY
        self.host = "agoda-com.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }
        
        # 🚀 [핵심] AgodaClient 내부에서 Gemini 직접 초기화
        # 백엔드 서비스를 import하는 대신 직접 기능을 구현하여 의존성 제거
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.llm_model = genai.GenerativeModel('gemini-2.5-flash')
            self.use_llm = True
            print("[AgodaClient] ✅ Gemini Model Initialized")
        except Exception as e:
            print(f"[AgodaClient] ⚠️ Gemini Init Failed: {e}")
            self.use_llm = False
        
        masked_key = f"{self.api_key[:4]}****" if self.api_key else "None"
        print(f"[AgodaClient] Init - Host: {self.host}, Base URL: {self.base_url}")

    async def _ask_llm_for_iata(self, location: str) -> str | None:
        """
        [내부 함수] LLM에게 도시 이름을 주고 IATA 코드를 물어봅니다.
        """
        if not self.use_llm: return None
        try:
            prompt = f"""
            Identify the 3-letter IATA airport code for: "{location}".
            Return ONLY the code (e.g., NRT). No extra text.
            If multiple airports, choose the main international one.
            """
            response = await self.llm_model.generate_content_async(prompt)
            code = response.text.strip().upper()
            # 정규식으로 3글자 알파벳인지 검증
            if re.match(r'^[A-Z]{3}$', code):
                return code
            return None
        except: return None

    async def _get_iata_code(self, client: httpx.AsyncClient, city_name: str) -> str | None:
        if not city_name: return None
        
        print(f"[AgodaClient] 🔎 Resolving IATA Code for: '{city_name}'")

        # 1. 입력값이 이미 IATA 코드인 경우 (예: ICN)
        if re.match(r'^[A-Z]{3}$', city_name):
            print(f"[AgodaClient] ⚡ Direct IATA Code: '{city_name}'")
            return city_name

        # 2. 괄호 안에 있는 코드 추출 (예: "서울/인천 (ICN)")
        iata_match = re.search(r'\(([A-Z]{3})\)', city_name)
        if iata_match:
            code = iata_match.group(1)
            print(f"[AgodaClient] ⚡ Extracted from parens: '{code}'")
            return code

        # 3. [NEW] 내장된 LLM에게 물어보기
        llm_code = await self._ask_llm_for_iata(city_name)
        if llm_code:
            print(f"[AgodaClient] 🤖 LLM Extracted IATA: '{city_name}' -> '{llm_code}'")
            return llm_code

        # 4. API 검색 (Fallback)
        try:
            clean_query = re.sub(r'\([^)]*\)', '', city_name).strip() # 괄호 제거
            clean_query = re.split(r'[/,]', clean_query)[0].strip()   # 슬래시 앞부분
            
            print(f"[AgodaClient] 🌐 API Fallback Search: '{clean_query}'")
            
            response = await client.get(
                f"{self.base_url}/flights/auto-complete", 
                headers=self.headers, 
                params={"query": clean_query}
            )
            
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    first = data[0]
                    code = first.get("code") or \
                           (first.get("tripLocations") and first["tripLocations"][0].get("code")) or \
                           (first.get("airports") and first["airports"][0].get("code"))
                    if code:
                        print(f"[AgodaClient] 🌐 API Found Code: '{code}'")
                        return code
            return None
        except Exception as e:
            print(f"[AgodaClient] Auto-complete Error: {e}")
            return None

    async def search_flights(self, origin: str, destination: str, start_date: date, end_date: date, pax: int = 1):
        print(f"\n[AgodaClient] ✈️ search_flights START: {origin} -> {destination}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            origin_code = await self._get_iata_code(client, origin)
            dest_code = await self._get_iata_code(client, destination)
            
            print(f"[AgodaClient] 🎯 Final Flight Codes: Origin={origin_code}, Dest={dest_code}")

            if not origin_code or not dest_code:
                print(f"[AgodaClient] ❌ Missing Flight Codes. Search Aborted.")
                return []

            params = {
                "origin": origin_code, 
                "destination": dest_code,
                "departureDate": start_date.strftime("%Y-%m-%d"), 
                "returnDate": end_date.strftime("%Y-%m-%d"),
                "adults": pax, 
                "currency": "KRW", 
                "language": "en-us", 
                "sort": "Best",
                "limit": 20, 
                "page": 1
            }
            print(f"[AgodaClient] 🚀 Sending Flight Request: {json.dumps(params)}")

            try:
                response = await client.get(f"{self.base_url}/flights/search-roundtrip", headers=self.headers, params=params)
                print(f"[AgodaClient] 📡 Flight API Status: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"[AgodaClient] ❌ API Error Response: {response.text}") 
                    return []
                
                bundles = response.json().get("data", {}).get("bundles", [])
                print(f"[AgodaClient] ✅ Flight Bundles Count: {len(bundles)}")
                
                if not bundles: return []

                results = []
                for item in bundles[:10]:
                    info = item.get("itineraries", [{}])[0].get("itineraryInfo", {})
                    
                    # 시간 추출
                    arrival_time = None
                    departure_time = None
                    duration_str = "정보 없음"
                    sectors = item.get("itineraries", [{}])[0].get("sectors", [])
                    if sectors:
                        outbound = sectors[0]
                        segments = outbound.get("sectorSegments", [])
                        if segments:
                            departure_time = segments[0].get("segment", {}).get("departureDateTime")
                            arrival_time = segments[-1].get("segment", {}).get("arrivalDateTime")
                            if "duration" in info:
                                duration_val = info["duration"]
                                duration_str = f"{duration_val // 60}시간 {duration_val % 60}분" if isinstance(duration_val, int) else str(duration_val)

                    # 가격 파싱 (안전장치)
                    price_val = 0
                    currency = "KRW"
                    price_info = info.get("price", {})
                    if price_info:
                        currency = next(iter(price_info), "KRW").upper()
                        try:
                            curr_data = price_info.get(currency.lower()) or {}
                            display_data = curr_data.get("display") or {}
                            per_book = display_data.get("perBook") or {}
                            price_val = per_book.get("allInclusive") or 0
                        except: price_val = 0

                    results.append({
                        "id": info.get("id"),
                        "vendor": "Agoda Flights",
                        "airline": "추천 항공편", 
                        "route": f"{origin} - {destination}",
                        "price_total": price_val,
                        "currency": currency,
                        "arrival_time": arrival_time,
                        "departure_time": departure_time,
                        "duration": duration_str,
                        "deeplink_url": None 
                    })
                return results
            except Exception as e:
                print(f"[AgodaClient] Flight Search Exception: {e}")
                return []

    # [Hotel] 호텔 (ID 검색 로직)
    async def _get_place_id(self, client: httpx.AsyncClient, query: str) -> str | None:
        clean_query = re.split(r'[/,]', query)[0].strip() 
        print(f"[AgodaClient] 🏨 Search Place ID for: '{clean_query}'")
        
        try:
            response = await client.get(
                f"{self.base_url}/hotels/auto-complete", 
                headers=self.headers, 
                params={"query": clean_query, "language": "en-us"}
            )
            if response.status_code != 200: return None
            data = response.json().get("data", [])
            
            if isinstance(data, list) and data:
                for item in data:
                    if "places" in item and item["places"]: 
                        return str(item["places"][0].get("id"))
                    if item.get("type", "").lower() == "city" and item.get("id"): 
                        return str(item.get("id"))
                if data[0].get("id"): return str(data[0].get("id"))
            return None
        except Exception as e:
            print(f"[AgodaClient] Place ID Logic Error: {e}")
            return None

    async def search_hotels(self, destination: str, start_date: date, end_date: date, pax: int = 2):
        print(f"\n[AgodaClient] 🏨 search_hotels START: {destination}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            place_id = await self._get_place_id(client, destination)
            if not place_id: 
                print(f"[AgodaClient] ❌ Place ID not found. Search Aborted.")
                return []

            params = {
                "id": place_id, 
                "checkinDate": start_date.strftime("%Y-%m-%d"), 
                "checkoutDate": end_date.strftime("%Y-%m-%d"),
                "adult": str(pax), 
                "currency": "KRW", 
                "language": "en-us", 
                "sort": "Ranking,Desc", 
                "limit": 20,
                "page": 1
            }
            print(f"[AgodaClient] 🚀 Sending Hotel Request: {json.dumps(params)}")

            try:
                response = await client.get(f"{self.base_url}/hotels/search-overnight", headers=self.headers, params=params)
                print(f"[AgodaClient] 📡 Hotel API Status: {response.status_code}")
                
                if response.status_code != 200: 
                    print(f"[AgodaClient] ❌ Hotel API Error Response: {response.text}")
                    return []
                
                data = response.json().get("data", {})
                hotels = data.get("hotels") or data.get("properties") or data.get("result") or []
                print(f"[AgodaClient] ✅ Hotels Found: {len(hotels)}")
                
                parsed_hotels = []
                for hotel in hotels:
                    price_val = 0
                    try:
                        p = hotel.get("price")
                        if isinstance(p, dict): price_val = p.get("total") or p.get("amount") or 0
                        elif isinstance(p, (int, float)): price_val = p
                        elif hotel.get("prices"): price_val = hotel["prices"][0]
                    except: pass
                    
                    if not price_val: price_val = hotel.get("dailyRate") or 0

                    img_url = hotel.get("image")
                    if not img_url and hotel.get("images"): img_url = hotel["images"][0]
                    name = hotel.get("name") or hotel.get("propertyName") or "이름 없음"

                    parsed_hotels.append({
                        "id": hotel.get("id") or hotel.get("hotelId"),
                        "vendor": "Agoda Hotels",
                        "name": name,
                        "location": destination,
                        "price": price_val,
                        "currency": "KRW",
                        "rating": hotel.get("starRating") or hotel.get("rating") or 4.5,
                        "image": img_url,
                        "has_details": True
                    })
                return parsed_hotels
            except Exception as e:
                print(f"[AgodaClient] Hotel Search Exception: {e}")
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