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
    """
    RapidAPI Agoda API 통합 클라이언트 (디버깅 강화 버전)
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
        
        # 🔍 [디버깅] API 키 및 호스트 검증
        print("=" * 60)
        print("[AgodaClient] 초기화 디버깅 정보")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Host: {self.host}")
        print(f"API Key 존재: {'✅ Yes' if self.api_key else '❌ No'}")
        if self.api_key:
            print(f"API Key 앞 8자: {self.api_key[:8]}...")
        print("=" * 60)
        
        # Gemini 초기화
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.llm_model = genai.GenerativeModel('gemini-2.5-flash')
            self.use_llm = True
            print("[AgodaClient] ✅ Gemini Model Initialized")
        except Exception as e:
            print(f"[AgodaClient] ⚠️ Gemini Init Failed: {e}")
            self.use_llm = False

    async def _test_api_connection(self):
        """
        🧪 [디버깅 전용] API 연결 테스트
        """
        print("\n" + "=" * 60)
        print("[테스트] RapidAPI 연결 확인 중...")
        print("=" * 60)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 가장 간단한 엔드포인트로 테스트
            test_endpoints = [
                "/flights/auto-complete?query=Seoul",
                "/hotels/auto-complete?query=Seoul"
            ]
            
            for endpoint in test_endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    print(f"\n🔗 Testing: {url}")
                    print(f"📋 Headers: {json.dumps(self.headers, indent=2)}")
                    
                    response = await client.get(url, headers=self.headers)
                    
                    print(f"📊 Status Code: {response.status_code}")
                    print(f"📄 Response Preview: {response.text[:500]}")
                    
                    if response.status_code == 200:
                        print("✅ 엔드포인트 작동 확인!")
                    else:
                        print(f"❌ 에러 발생")
                        # 에러 상세 분석
                        if response.status_code == 401:
                            print("   → API 키가 잘못되었거나 권한이 없습니다")
                        elif response.status_code == 403:
                            print("   → API 접근이 거부되었습니다 (구독 확인 필요)")
                        elif response.status_code == 404:
                            print("   → 엔드포인트를 찾을 수 없습니다 (경로 확인 필요)")
                        elif response.status_code == 429:
                            print("   → API 호출 제한 초과")
                        
                except Exception as e:
                    print(f"❌ Exception: {str(e)}")
        
        print("=" * 60)

    async def _ask_llm_for_iata(self, location: str) -> str | None:
        """LLM에게 도시 이름을 주고 IATA 코드를 물어봅니다."""
        if not self.use_llm: return None
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
        if not city_name: return None
        
        print(f"\n[AgodaClient] 🔎 Resolving IATA Code for: '{city_name}'")

        # 1. 입력값이 이미 IATA 코드인 경우
        if re.match(r'^[A-Z]{3}$', city_name):
            print(f"[AgodaClient] ⚡ Direct IATA Code: '{city_name}'")
            return city_name

        # 2. 괄호 안에 있는 코드 추출
        iata_match = re.search(r'\(([A-Z]{3})\)', city_name)
        if iata_match:
            code = iata_match.group(1)
            print(f"[AgodaClient] ⚡ Extracted from parens: '{code}'")
            return code

        # 3. LLM에게 물어보기
        llm_code = await self._ask_llm_for_iata(city_name)
        if llm_code:
            print(f"[AgodaClient] 🤖 LLM Extracted IATA: '{city_name}' -> '{llm_code}'")
            return llm_code

        # 4. API 검색 (Fallback)
        try:
            clean_query = re.sub(r'\([^)]*\)', '', city_name).strip()
            clean_query = re.split(r'[/,]', clean_query)[0].strip()
            
            print(f"[AgodaClient] 🌐 API Fallback Search: '{clean_query}'")
            
            # 🔍 [디버깅] 요청 상세 로그
            endpoint = f"{self.base_url}/flights/auto-complete"
            params = {"query": clean_query}
            print(f"   → Request URL: {endpoint}")
            print(f"   → Params: {params}")
            
            response = await client.get(endpoint, headers=self.headers, params=params)
            
            print(f"   → Response Status: {response.status_code}")
            print(f"   → Response Body: {response.text[:300]}...")
            
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
            print(f"[AgodaClient] ❌ Auto-complete Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def search_flights(self, origin: str, destination: str, start_date: date, end_date: date, pax: int = 1):
        print(f"\n{'='*60}")
        print(f"[AgodaClient] ✈️ FLIGHT SEARCH START")
        print(f"{'='*60}")
        print(f"Origin: {origin}")
        print(f"Destination: {destination}")
        print(f"Dates: {start_date} → {end_date}")
        print(f"Passengers: {pax}")
        print(f"{'='*60}\n")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            origin_code = await self._get_iata_code(client, origin)
            dest_code = await self._get_iata_code(client, destination)
            
            print(f"\n[AgodaClient] 🎯 Final Flight Codes:")
            print(f"   Origin Code: {origin_code}")
            print(f"   Destination Code: {dest_code}")

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
            
            endpoint = f"{self.base_url}/flights/search-roundtrip"
            print(f"\n[AgodaClient] 🚀 Flight API Request:")
            print(f"   Endpoint: {endpoint}")
            print(f"   Params: {json.dumps(params, indent=4)}")

            try:
                # 🎯 [FIX] 비동기 검색 처리 - 최대 5번 재시도
                max_retries = 5
                retry_count = 0
                
                while retry_count < max_retries:
                    response = await client.get(endpoint, headers=self.headers, params=params)
                    
                    print(f"\n[AgodaClient] 📡 Flight API Response (Attempt {retry_count + 1}/{max_retries}):")
                    print(f"   Status Code: {response.status_code}")
                    
                    if response.status_code != 200:
                        print(f"\n[AgodaClient] ❌ API Error Details:")
                        print(f"   Full Response: {response.text}")
                        
                        if response.status_code == 401:
                            print("\n💡 해결방법: API 키를 확인하세요")
                        elif response.status_code == 403:
                            print("\n💡 해결방법: RapidAPI 대시보드에서 구독 상태를 확인하세요")
                        elif response.status_code == 404:
                            print("\n💡 해결방법: 엔드포인트 경로가 올바른지 확인하세요")
                        elif response.status_code == 429:
                            print("\n💡 해결방법: API 호출 제한이 초과되었습니다")
                        
                        return []
                    
                    json_data = response.json()
                    
                    # retry 정보 확인
                    retry_info = json_data.get("retry", {})
                    next_retry_ms = retry_info.get("next", 0)
                    
                    # trips 확인
                    trips = json_data.get("trips", [])
                    if trips:
                        trip = trips[0]
                        is_completed = trip.get("isCompleted", False)
                        bundles = trip.get("bundles", [])
                        total_bundles = trip.get("totalBundles", 0)
                        
                        print(f"   → isCompleted: {is_completed}")
                        print(f"   → Bundles: {len(bundles)}/{total_bundles}")
                        print(f"   → Retry after: {next_retry_ms}ms")
                        
                        # 검색 완료된 경우
                        if is_completed or len(bundles) > 0:
                            print(f"\n[AgodaClient] ✅ Search completed! Found {len(bundles)} bundles")
                            
                            if not bundles:
                                print("[AgodaClient] ⚠️ No flight results found")
                                return []
                            
                            # 결과 파싱
                            results = []
                            for idx, item in enumerate(bundles[:10], 1):
                                print(f"\n   Processing bundle {idx}/{min(10, len(bundles))}...")
                                
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
                                    "currency": currency,
                                    "arrival_time": arrival_time,
                                    "departure_time": departure_time,
                                    "duration": duration_str,
                                    "deeplink_url": None 
                                })
                            
                            print(f"\n[AgodaClient] ✅ Successfully parsed {len(results)} flights")
                            return results
                        
                        # 아직 검색 중인 경우 - 대기 후 재시도
                        if next_retry_ms > 0:
                            wait_seconds = next_retry_ms / 1000
                            print(f"\n[AgodaClient] ⏳ Search in progress... Waiting {wait_seconds}s before retry")
                            await asyncio.sleep(wait_seconds)
                            retry_count += 1
                            continue
                    
                    # 예상치 못한 응답 구조
                    print(f"\n[AgodaClient] ⚠️ Unexpected response structure:")
                    print(f"   Response Preview: {response.text[:500]}")
                    break
                
                # 최대 재시도 초과
                print(f"\n[AgodaClient] ❌ Max retries ({max_retries}) exceeded")
                return []
                
            except Exception as e:
                print(f"\n[AgodaClient] ❌ Flight Search Exception:")
                print(f"   Error Type: {type(e).__name__}")
                print(f"   Error Message: {str(e)}")
                import traceback
                print(f"   Traceback:\n{traceback.format_exc()}")
                return []

    async def _get_place_id(self, client: httpx.AsyncClient, query: str) -> str | None:
        clean_query = re.split(r'[/,]', query)[0].strip() 
        print(f"\n[AgodaClient] 🏨 Search Place ID for: '{clean_query}'")
        
        try:
            endpoint = f"{self.base_url}/hotels/auto-complete"
            params = {"query": clean_query, "language": "en-us"}
            
            print(f"   → Request: {endpoint}")
            print(f"   → Params: {params}")
            
            response = await client.get(endpoint, headers=self.headers, params=params)
            
            print(f"   → Status: {response.status_code}")
            
            if response.status_code != 200: 
                print(f"   → Error Response: {response.text}")
                return None
            
            # 🔍 전체 응답 구조 확인
            full_response = response.json()
            print(f"\n   📦 Full Response Structure:")
            print(json.dumps(full_response, indent=2, ensure_ascii=False)[:1000])
            
            # 🎯 [FIX] places가 최상위에 있는 경우 처리
            if "places" in full_response and full_response["places"]:
                places_list = full_response["places"]
                if isinstance(places_list, list) and places_list:
                    first_place = places_list[0]
                    place_id = first_place.get("id")
                    type_id = first_place.get("typeId")
                    place_name = first_place.get("name", "")
                    
                    # 🔑 [중요] API 형식: "typeId_id" (예: "1_5085")
                    if type_id is not None and place_id is not None:
                        formatted_id = f"{type_id}_{place_id}"
                        print(f"   ✅ Found Place ID from top-level places: {formatted_id} ({place_name})")
                        print(f"      → typeId: {type_id}, id: {place_id}")
                        return formatted_id
                    elif place_id:
                        # typeId가 없으면 id만 문자열로
                        place_id_str = str(place_id)
                        print(f"   ✅ Found Place ID (no typeId): {place_id_str} ({place_name})")
                        return place_id_str
            
            # 기존 로직: data 필드 확인
            data = full_response.get("data", [])
            
            if isinstance(data, list) and data:
                print(f"\n   🔎 Analyzing {len(data)} items in data array...")
                
                for idx, item in enumerate(data):
                    print(f"\n   Item {idx}: {json.dumps(item, indent=2, ensure_ascii=False)[:300]}")
                    
                    # 케이스 1: 직접 id 필드가 있는 경우
                    if item.get("id"):
                        place_id = str(item["id"])
                        item_type = item.get("type", "unknown")
                        print(f"   ✅ Found ID (type: {item_type}): {place_id}")
                        return place_id
                    
                    # 케이스 2: places 배열 안에 있는 경우
                    if "places" in item and item["places"]:
                        place_id = str(item["places"][0].get("id"))
                        print(f"   ✅ Found Place ID from places array: {place_id}")
                        return place_id
                    
                    # 케이스 3: cityId 필드
                    if item.get("cityId"):
                        place_id = str(item["cityId"])
                        print(f"   ✅ Found City ID: {place_id}")
                        return place_id
                    
                    # 케이스 4: locationId 필드
                    if item.get("locationId"):
                        place_id = str(item["locationId"])
                        print(f"   ✅ Found Location ID: {place_id}")
                        return place_id
                
                print("   ⚠️ No valid ID found in any item")
            
            elif isinstance(data, dict):
                print(f"   🔎 Data is dict: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                if data.get("id"):
                    place_id = str(data["id"])
                    print(f"   ✅ Found ID from dict: {place_id}")
                    return place_id
            
            print("   ❌ Could not extract Place ID")
            return None
            
        except Exception as e:
            print(f"[AgodaClient] ❌ Place ID Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def search_hotels(self, destination: str, start_date: date, end_date: date, pax: int = 2):
        print(f"\n{'='*60}")
        print(f"[AgodaClient] 🏨 HOTEL SEARCH START")
        print(f"{'='*60}")
        print(f"Destination: {destination}")
        print(f"Dates: {start_date} → {end_date}")
        print(f"Guests: {pax}")
        print(f"{'='*60}\n")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            place_id = await self._get_place_id(client, destination)
            
            if not place_id: 
                print(f"[AgodaClient] ❌ Place ID not found. Search Aborted.")
                return []

            # 🎯 [FIX] id를 문자열로 전달 (API 요구사항)
            params = {
                "id": place_id,  # 이미 "1_5085" 형태의 문자열
                "checkinDate": start_date.strftime("%Y-%m-%d"), 
                "checkoutDate": end_date.strftime("%Y-%m-%d"),
                "adult": str(pax),  # 문자열로 변환
                "currency": "KRW", 
                "language": "en-us", 
                "sort": "Ranking,Desc", 
                "limit": 20,
                "page": 1
            }
            
            endpoint = f"{self.base_url}/hotels/search-overnight"
            print(f"\n[AgodaClient] 🚀 Hotel API Request:")
            print(f"   Endpoint: {endpoint}")
            print(f"   Params: {json.dumps(params, indent=4)}")

            try:
                response = await client.get(endpoint, headers=self.headers, params=params)
                
                print(f"\n[AgodaClient] 📡 Hotel API Response:")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response Preview: {response.text[:500]}")
                
                if response.status_code != 200: 
                    print(f"\n[AgodaClient] ❌ Hotel API Error:")
                    print(f"   Full Response: {response.text}")
                    return []
                
                response_data = response.json()
                
                # 🎯 [FIX] 에러 처리 추가
                if response_data.get("status") == False or response_data.get("errors"):
                    print(f"\n[AgodaClient] ❌ API returned errors:")
                    print(f"   Errors: {response_data.get('errors')}")
                    print(f"   Message: {response_data.get('message')}")
                    return []
                
                data = response_data.get("data")
                
                # data가 None인 경우 처리
                if data is None:
                    print(f"\n[AgodaClient] ❌ No data in response")
                    return []
                
                # 🎯 [FIX] Agoda API의 실제 응답 구조에 맞춰 파싱
                hotels = []
                
                # 케이스 1: citySearch 구조 (실제 Agoda API)
                if "citySearch" in data:
                    city_search = data["citySearch"]
                    search_result = city_search.get("searchResult", {})
                    
                    # searchInfo 확인
                    search_info = search_result.get("searchInfo", {})
                    total_hotels = search_info.get("totalFilteredHotels", 0)
                    print(f"\n[AgodaClient] 📊 Search Info:")
                    print(f"   Total Filtered Hotels: {total_hotels}")
                    
                    # 🔍 [디버깅] searchResult의 모든 키 확인
                    print(f"\n   🔑 searchResult keys: {list(search_result.keys())}")
                    
                    # 🎯 [FIX] 실제 응답 구조: properties 배열 사용
                    hotels = search_result.get("properties", [])
                
                # 케이스 2: 직접 hotels 필드
                elif "hotels" in data:
                    hotels = data["hotels"]
                
                # 케이스 3: properties 필드
                elif "properties" in data:
                    hotels = data["properties"]
                
                # 케이스 4: result 필드
                elif "result" in data:
                    hotels = data["result"]
                
                # 🔍 [디버깅] hotels가 비어있으면 전체 응답 출력
                if not hotels:
                    print(f"\n   ⚠️ Hotels list is empty. Full response structure:")
                    print(json.dumps(response_data, indent=2, ensure_ascii=False)[:3000])
                
                print(f"\n[AgodaClient] ✅ Hotels Found: {len(hotels)}")
                
                parsed_hotels = []
                for idx, hotel in enumerate(hotels, 1):
                    print(f"   Processing hotel {idx}/{len(hotels)}...")
                    
                    # 🎯 [FIX] Agoda properties 구조에 맞춰 파싱
                    property_id = hotel.get("propertyId")
                    content = hotel.get("content", {})
                    info = content.get("informationSummary", {})
                    pricing = hotel.get("pricing", {})
                    
                    # 호텔 이름
                    name = info.get("localeName") or info.get("defaultName") or "이름 없음"
                    
                    # 가격 추출 (복잡한 구조)
                    price_val = 0
                    try:
                        # pricing.offers[0].price 구조일 가능성
                        if "offers" in pricing and pricing["offers"]:
                            first_offer = pricing["offers"][0]
                            if "price" in first_offer:
                                price_info = first_offer["price"]
                                # perRoomPerNight 또는 perBook
                                price_val = (price_info.get("perRoomPerNight") or 
                                           price_info.get("perBook") or 
                                           price_info.get("amount") or 0)
                        
                        # 직접 pricing에 있을 수도
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
                    
                    # 이미지 (복잡한 구조일 수 있음)
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
                
                print(f"\n[AgodaClient] ✅ Successfully parsed {len(parsed_hotels)} hotels")
                return parsed_hotels
                
            except Exception as e:
                print(f"\n[AgodaClient] ❌ Hotel Search Exception:")
                print(f"   Error: {str(e)}")
                import traceback
                traceback.print_exc()
                return []

    async def get_hotel_details(self, hotel_id: str, start_date: date, end_date: date, pax: int = 2):
        url = f"{self.base_url}/hotels/details"
        params = {
            "hotelId": hotel_id,
            "checkIn": start_date.isoformat(),
            "checkOut": end_date.isoformat(),
            "adults": str(pax),
            "currency": "KRW",
            "language": "ko-kr"
        }
        
        print(f"\n[AgodaClient] 🔍 Hotel Details Request:")
        print(f"   URL: {url}")
        print(f"   Params: {json.dumps(params, indent=4)}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code != 200: 
                    print(f"   Error: {response.text}")
                    return None
                    
                data = response.json().get("data", {})
                
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
            except Exception as e:
                print(f"   Exception: {str(e)}")
                import traceback
                traceback.print_exc()
                return None