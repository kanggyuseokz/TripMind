import re
import httpx
import json
import asyncio
import google.generativeai as genai
from datetime import date
from ..config import settings


class AgodaClientError(Exception):
    """Agoda API 클라이언트 관련 에러 정의"""
    pass


class AgodaClient:
    """RapidAPI Agoda API 통합 클라이언트"""

    def __init__(self):
        self.base_url = "https://agoda-com.p.rapidapi.com"
        self.api_key = settings.RAPID_API_KEY
        self.host = "agoda-com.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }
        
        # Gemini 초기화
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.llm_model = genai.GenerativeModel('gemini-2.5-flash')
            self.use_llm = True
        except Exception as e:
            print(f"[AgodaClient] Gemini Init Failed: {e}")
            self.use_llm = False

    async def _ask_llm_for_iata(self, location: str) -> str | None:
        """LLM에게 도시 이름을 주고 IATA 코드를 물어봅니다."""
        if not self.use_llm:
            return None
        try:
            prompt = f"""
            Identify the 3-letter IATA airport code for: "{location}".
            Return ONLY the code (e.g., NRT). No extra text.
            If multiple airports, choose the main international one.
            """
            response = await self.llm_model.generate_content_async(prompt)
            code = response.text.strip().upper()
            if re.match(r'^[A-Z]{3}$', code):
                return code
            return None
        except:
            return None

    async def _get_iata_code(self, client: httpx.AsyncClient, city_name: str) -> str | None:
        """도시 이름을 IATA 코드로 변환"""
        if not city_name:
            return None

        # 1. 입력값이 이미 IATA 코드인 경우
        if re.match(r'^[A-Z]{3}$', city_name):
            return city_name

        # 2. 괄호 안에 있는 코드 추출
        iata_match = re.search(r'\(([A-Z]{3})\)', city_name)
        if iata_match:
            return iata_match.group(1)

        # 3. LLM에게 물어보기
        llm_code = await self._ask_llm_for_iata(city_name)
        if llm_code:
            return llm_code

        # 4. API 검색 (Fallback)
        try:
            clean_query = re.sub(r'\([^)]*\)', '', city_name).strip()
            clean_query = re.split(r'[/,]', clean_query)[0].strip()
            
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
                        return code
            return None
        except:
            return None

    async def search_flights(self, origin: str, destination: str, start_date: date, end_date: date, pax: int = 1):
        """항공편 검색 (비동기 폴링 지원)"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            origin_code = await self._get_iata_code(client, origin)
            dest_code = await self._get_iata_code(client, destination)

            if not origin_code or not dest_code:
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

            try:
                # 비동기 검색 처리 - 최대 5번 재시도
                max_retries = 5
                retry_count = 0
                
                while retry_count < max_retries:
                    response = await client.get(
                        f"{self.base_url}/flights/search-roundtrip",
                        headers=self.headers,
                        params=params
                    )
                    
                    if response.status_code != 200:
                        return []
                    
                    json_data = response.json()
                    retry_info = json_data.get("retry", {})
                    next_retry_ms = retry_info.get("next", 0)
                    
                    trips = json_data.get("trips", [])
                    if trips:
                        trip = trips[0]
                        is_completed = trip.get("isCompleted", False)
                        bundles = trip.get("bundles", [])
                        
                        # 검색 완료된 경우
                        if is_completed or len(bundles) > 0:
                            if not bundles:
                                return []
                            
                            # ✅ 결과 파싱 (디버깅 포함)
                            results = []
                            for idx, item in enumerate(bundles[:10]):
                                # ✅ 첫 번째 항목만 전체 구조 출력
                                if idx == 0:
                                    print(f"\n[DEBUG] ===== FIRST BUNDLE STRUCTURE =====")
                                    print(json.dumps(item, indent=2, ensure_ascii=False)[:2000])
                                    print(f"[DEBUG] ===== END =====\n")
                                
                                info = item.get("itineraries", [{}])[0].get("itineraryInfo", {})
                                
                                # 시간 추출
                                arrival_time = None
                                departure_time = None
                                duration_str = "정보 없음"
                                sectors = item.get("itineraries", [{}])[0].get("sectors", [])
                                
                                # ✅ sectors 디버깅
                                if idx == 0:
                                    print(f"[DEBUG] sectors 존재: {len(sectors) if sectors else 0}개")
                                    if sectors:
                                        print(f"[DEBUG] sectors[0] keys: {list(sectors[0].keys())}")
                                
                                if sectors:
                                    outbound = sectors[0]
                                    segments = outbound.get("sectorSegments", [])
                                    
                                    # ✅ segments 디버깅
                                    if idx == 0:
                                        print(f"[DEBUG] sectorSegments 존재: {len(segments) if segments else 0}개")
                                        if segments:
                                            print(f"[DEBUG] segments[0] keys: {list(segments[0].keys())}")
                                            print(f"[DEBUG] segments[0]: {json.dumps(segments[0], indent=2, ensure_ascii=False)[:500]}")
                                    
                                    if segments:
                                        first_seg = segments[0].get("segment", {})
                                        last_seg = segments[-1].get("segment", {})
                                        
                                        # ✅ segment 내용 디버깅
                                        if idx == 0:
                                            print(f"[DEBUG] first_seg keys: {list(first_seg.keys()) if first_seg else 'None'}")
                                            if first_seg:
                                                print(f"[DEBUG] first_seg sample: {json.dumps(first_seg, indent=2, ensure_ascii=False)[:500]}")
                                        
                                        departure_time = first_seg.get("departureDateTime")
                                        arrival_time = last_seg.get("arrivalDateTime")
                                        
                                        # ✅ 추출된 시간 확인
                                        if idx == 0:
                                            print(f"[DEBUG] ✈️ departure_time: {departure_time}")
                                            print(f"[DEBUG] 🛬 arrival_time: {arrival_time}")
                                        
                                        if "duration" in info:
                                            duration_val = info["duration"]
                                            duration_str = f"{duration_val // 60}시간 {duration_val % 60}분" if isinstance(duration_val, int) else str(duration_val)

                                # 가격 파싱
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
                                    except:
                                        price_val = 0

                                results.append({
                                    "id": info.get("id"),
                                    "vendor": "Agoda Flights",
                                    "airline": "추천 항공편",
                                    "route": f"{origin} - {destination}",
                                    "price_total": price_val,
                                    "price": price_val,
                                    "currency": currency,
                                    "arrival_time": arrival_time,
                                    "departure_time": departure_time,
                                    "duration": duration_str,
                                    "deeplink_url": None
                                })
                            
                            return results
                        
                        # 아직 검색 중인 경우 - 대기 후 재시도
                        if next_retry_ms > 0:
                            wait_seconds = next_retry_ms / 1000
                            await asyncio.sleep(wait_seconds)
                            retry_count += 1
                            continue
                    
                    break
                
                return []
                
            except Exception as e:
                print(f"[AgodaClient] search_flights error: {e}")
                return []

    async def _get_place_id(self, client: httpx.AsyncClient, query: str) -> str | None:
        """도시 이름을 Agoda Place ID로 변환"""
        clean_query = re.split(r'[/,]', query)[0].strip()
        
        try:
            response = await client.get(
                f"{self.base_url}/hotels/auto-complete",
                headers=self.headers,
                params={"query": clean_query, "language": "en-us"}
            )
            
            if response.status_code != 200:
                return None
            
            full_response = response.json()
            
            # places가 최상위에 있는 경우 처리
            if "places" in full_response and full_response["places"]:
                places_list = full_response["places"]
                if isinstance(places_list, list) and places_list:
                    first_place = places_list[0]
                    place_id = first_place.get("id")
                    type_id = first_place.get("typeId")
                    
                    # API 형식: "typeId_id" (예: "1_5085")
                    if type_id is not None and place_id is not None:
                        return f"{type_id}_{place_id}"
                    elif place_id:
                        return str(place_id)
            
            # data 필드 확인 (Fallback)
            data = full_response.get("data", [])
            if isinstance(data, list) and data:
                for item in data:
                    if item.get("id"):
                        return str(item["id"])
                    if "places" in item and item["places"]:
                        return str(item["places"][0].get("id"))
            
            return None
            
        except:
            return None

    async def search_hotels(self, destination: str, start_date: date, end_date: date, pax: int = 2):
        """호텔 검색"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            place_id = await self._get_place_id(client, destination)
            
            if not place_id:
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

            try:
                response = await client.get(
                    f"{self.base_url}/hotels/search-overnight",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code != 200:
                    return []
                
                response_data = response.json()
                
                # 에러 체크
                if response_data.get("status") == False or response_data.get("errors"):
                    return []
                
                data = response_data.get("data")
                if data is None:
                    return []
                
                # Agoda API 응답 구조 파싱
                hotels = []
                if "citySearch" in data:
                    city_search = data["citySearch"]
                    search_result = city_search.get("searchResult", {})
                    hotels = search_result.get("properties") or city_search.get("properties") or []
                elif "hotels" in data:
                    hotels = data["hotels"]
                elif "properties" in data:
                    hotels = data["properties"]
                
                if not hotels:
                    return []
                
                # 호텔 정보 파싱
                parsed_hotels = []
                for hotel in hotels:
                    property_id = hotel.get("propertyId")
                    content = hotel.get("content", {})
                    info = content.get("informationSummary", {})
                    pricing = hotel.get("pricing", {})
                    
                    # 호텔 이름
                    name = info.get("localeName") or info.get("defaultName") or "이름 없음"
                    
                    # 가격 추출
                    price_val = 0
                    try:
                        if "offers" in pricing and pricing["offers"]:
                            first_offer = pricing["offers"][0]
                            if "price" in first_offer:
                                price_info = first_offer["price"]
                                price_val = (price_info.get("perRoomPerNight") or
                                           price_info.get("perBook") or
                                           price_info.get("amount") or 0)
                        
                        if not price_val and "price" in pricing:
                            price_val = pricing["price"]
                    except:
                        pass
                    
                    # 별점
                    rating = info.get("rating", 0)
                    
                    # 위치
                    address = info.get("address", {})
                    area = address.get("area", {})
                    area_name = area.get("name", destination)
                    
                    # 좌표
                    geo = info.get("geoInfo", {})
                    latitude = geo.get("latitude")
                    longitude = geo.get("longitude")
                    
                    # 이미지
                    img_url = None
                    if "images" in content:
                        images = content["images"]
                        if isinstance(images, list) and images:
                            img_url = images[0].get("url") or images[0].get("source")
                    
                    parsed_hotels.append({
                        "id": property_id,
                        "vendor": "Agoda Hotels",
                        "name": name,
                        "location": area_name,
                        "price": price_val,
                        "currency": "KRW",
                        "rating": rating,
                        "image": img_url,
                        "latitude": latitude,
                        "longitude": longitude,
                        "has_details": True
                    })
                
                return parsed_hotels
                
            except:
                return []

    async def get_hotel_details(self, hotel_id: str, start_date: date, end_date: date, pax: int = 2):
        """호텔 상세 정보 조회"""
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
                
                if response.status_code != 200:
                    return None
                
                data = response.json().get("data", {})
                
                # 이미지 처리
                raw_images = data.get("images", [])
                processed_images = []
                for img in raw_images:
                    if isinstance(img, str):
                        processed_images.append(img)
                    elif isinstance(img, dict):
                        img_url = img.get("url") or img.get("original") or img.get("link")
                        if img_url:
                            processed_images.append(img_url)

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