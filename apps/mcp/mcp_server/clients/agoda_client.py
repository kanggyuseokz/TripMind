# mcp/mcp_server/clients/agoda_client.py

import re
import httpx
import json
import asyncio
import google.generativeai as genai
import requests
from datetime import date
from ..config import settings


class AgodaClientError(Exception):
    """Agoda API 클라이언트 관련 에러 정의"""
    pass


class ExchangeService:
    """한국수출입은행 환율 정보 간편 조회"""
    
    def __init__(self):
        try:
            # ✅ 정확한 API URL (oapi 서브도메인)
            self.base_url = settings.EXCHANGE_BASE or "https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON"
            self.auth_key = settings.EXCHANGE_API_KEY
            self.data_code = settings.EXCHANGE_DATA_CODE or "AP01"
            self.enabled = True
            
            # urllib3 경고 숨기기
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
        except AttributeError:
            print("[ExchangeService] ⚠️ Exchange API settings not found, using fallback rate")
            self.enabled = False
    
    def get_rate(self, currency_code: str, search_date: str = None) -> float:
        if not self.enabled:
            return 1300.0
        
        try:
            params = {
                "authkey": self.auth_key,
                "data": self.data_code
            }
            
            if search_date:
                params["searchdate"] = search_date
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10,
                verify=False
            )
            response.raise_for_status()
            
            # ✅ JSON 파싱 에러 방지
            try:
                rows = response.json()
            except ValueError as e:
                print(f"[ExchangeService] ❌ JSON parse error: {e}")
                print(f"[ExchangeService] Raw response: {response.text[:200]}")
                return 1300.0
            
            # ✅ 응답 검증 (기존과 동일)
            if not rows or not isinstance(rows, list):
                print(f"[ExchangeService] ⚠️ Invalid response format")
                return 1300.0
            
            # 첫 번째 항목의 result 확인
            if rows and rows[0].get("result") != 1:
                result_code = rows[0].get("result")
                error_msg = {
                    2: "DATA 코드 오류",
                    3: "인증코드 오류", 
                    4: "일일제한횟수 마감"
                }.get(result_code, f"알 수 없는 오류 ({result_code})")
                print(f"[ExchangeService] ❌ API Error: {error_msg}")
                return 1300.0
            
            # USD 찾기
            for row in rows:
                cur_unit = row.get("cur_unit", "")
                if cur_unit.upper().startswith("USD"):
                    deal_bas_r = row.get("deal_bas_r", "0")
                    try:
                        rate = float(deal_bas_r.replace(",", ""))
                        print(f"[ExchangeService] ✅ USD: {rate} KRW")
                        return rate
                    except (ValueError, AttributeError):
                        continue
            
            print(f"[ExchangeService] ⚠️ USD not found")
            return 1300.0
            
        except Exception as e:
            print(f"[ExchangeService] ❌ Error: {e}")
            return 1300.0

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
        
        # ✅ 환율 서비스 및 캐시
        self.exchange_service = ExchangeService()
        self._usd_to_krw_rate = None
    
    def _get_usd_to_krw_rate(self) -> float:
        """USD → KRW 환율 조회 (캐시 사용)"""
        if self._usd_to_krw_rate:
            return self._usd_to_krw_rate
        
        try:
            self._usd_to_krw_rate = self.exchange_service.get_rate("USD")
            print(f"[Agoda] ✅ USD/KRW rate: {self._usd_to_krw_rate}")
        except Exception as e:
            print(f"[Agoda] ⚠️ Exchange API error: {e}, using fallback rate: 1300")
            self._usd_to_krw_rate = 1300.0
        
        return self._usd_to_krw_rate

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

    # ✅ search_flights를 동기 함수로 유지 (원본 그대로)
    def search_flights(self, origin, destination, depart_date, return_date, adults=1):
        """
        항공권 검색 (왕복)
        
        Returns:
            list: 항공편 리스트, 각 항공편은 다음 필드를 포함:
                - outbound_departure_time: 출국편 출발 시간
                - outbound_arrival_time: 출국편 도착 시간
                - inbound_departure_time: 입국편 출발 시간 (왕복인 경우)
                - inbound_arrival_time: 입국편 도착 시간 (왕복인 경우)
                - price_krw: 가격 (KRW)
                - airline: 항공사
                - duration: 총 소요 시간 (분)
        """
        try:
            # API 호출
            url = "https://agoda-com.p.rapidapi.com/flights/search-roundtrip"
            
            querystring = {
                "origin": origin,
                "destination": destination,
                "departureDate": depart_date,
                "returnDate": return_date,
                "adults": str(adults),
                "children": "0",
                "infants": "0",
                "cabinClass": "ECONOMY",
                "currency": "USD",
                "market": "en-us",
                "countryCode": "US"
            }
            
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": "agoda-com.p.rapidapi.com"
            }
            
            print(f"[Agoda] 🔍 Searching flights: {origin} → {destination} ({depart_date} ~ {return_date})")
            
            response = requests.get(url, headers=headers, params=querystring, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            # ✅ Retry 로직 (비동기 검색 대응)
            import time
            retry_info = data.get('retry', {})
            max_retries = 5
            retry_count = 0
            
            while retry_info.get('next') and retry_count < max_retries:
                trips = data.get('trips', [])
                if trips and trips[0].get('isCompleted') and trips[0].get('bundles'):
                    print(f"[Agoda] ✅ Search completed! Found {len(trips[0].get('bundles', []))} bundles")
                    break

                retry_delay = (retry_info.get('next') or 2000) / 1000
                print(f"[Agoda] ⏳ Search in progress, retrying in {retry_delay}s... ({retry_count + 1}/{max_retries})")
                time.sleep(retry_delay)

                response = requests.get(url, headers=headers, params=querystring, timeout=60)
                response.raise_for_status()
                data = response.json()
                retry_info = data.get('retry', {})
                retry_count += 1
            
            # ✅ 디버깅 로그 추가
            print(f"[Agoda] 🔍 API Response keys: {list(data.keys())}")
            print(f"[Agoda] 🔍 Status: {data.get('status')}")
            print(f"[Agoda] 🔍 Retry info: {data.get('retry')}")
            
            if 'trips' in data:
                trips = data.get('trips', [])
                print(f"[Agoda] 🔍 Number of trips: {len(trips)}")
                if trips:
                    trip0 = trips[0]
                    print(f"[Agoda] 🔍 Trip[0] keys: {list(trip0.keys())}")
                    print(f"[Agoda] 🔍 Bundles count: {len(trip0.get('bundles', []))}")
                    print(f"[Agoda] 🔍 QuickSorted count: {len(trip0.get('quickSortedItineraries', []))}")
                    print(f"[Agoda] 🔍 isCompleted: {trip0.get('isCompleted')}")
            
            trips = data.get('trips', [])
            if not trips:
                return []

            trip = trips[0]
            if not trip.get('isCompleted'):
                return []

            bundles = trip.get('bundles', [])
            
            if not bundles:
                print(f"[Agoda] No flight bundles found")
                return []
            
            flights = []
            
            # ✅ 환율 가져오기
            usd_to_krw = self._get_usd_to_krw_rate()
            
            for bundle in bundles[:10]:  # 상위 10개만
                try:
                    # 가격 정보
                    price_info = bundle.get('bundlePrice', [{}])[0].get('price', {}).get('usd', {})
                    price_usd = price_info.get('display', {}).get('perBook', {}).get('allInclusive', 0)
                    
                    # USD → KRW 변환
                    price_krw = int(price_usd * usd_to_krw)
                    
                    # 여정 정보
                    itineraries = bundle.get('itineraries', [])
                    if not itineraries:
                        continue
                    
                    itinerary_info = itineraries[0].get('itineraryInfo', {})
                    
                    # Outbound (출국편)
                    outbound_slice = bundle.get('outboundSlice', {})
                    outbound_segments = outbound_slice.get('segments', [])
                    
                    # ✅ 출국편 시간 추출
                    outbound_departure_time = None
                    outbound_arrival_time = None
                    
                    if outbound_segments:
                        # 첫 번째 구간의 출발 시간
                        outbound_departure_time = outbound_segments[0].get('departDateTime')
                        # 마지막 구간의 도착 시간
                        outbound_arrival_time = outbound_segments[-1].get('arrivalDateTime')
                    
                    # Inbound (입국편) - 왕복인 경우에만
                    if itineraries:
                        first_itinerary = itineraries[0]
                        inbound_slice = first_itinerary.get('inboundSlice')
                    inbound_departure_time = None
                    inbound_arrival_time = None
                    
                    if inbound_slice:
                        inbound_segments = inbound_slice.get('segments', [])
                        if inbound_segments:
                            # 첫 번째 구간의 출발 시간
                            inbound_departure_time = inbound_segments[0].get('departDateTime')
                            # 마지막 구간의 도착 시간
                            inbound_arrival_time = inbound_segments[-1].get('arrivalDateTime')
                    
                    # 항공사 정보
                    carrier = outbound_segments[0].get('carrierContent', {}) if outbound_segments else {}
                    airline = carrier.get('carrierName', 'Unknown')
                    
                    # 총 소요 시간
                    total_duration = itinerary_info.get('totalTripDuration', 0)
                    
                    # 항공편 딕셔너리 생성
                    flight = {
                        'price_krw': price_krw,
                        'price_usd': price_usd,
                        'airline': airline,
                        'duration': total_duration,
                        'outbound_departure_time': outbound_departure_time,
                        'outbound_arrival_time': outbound_arrival_time,
                        'inbound_departure_time': inbound_departure_time,
                        'inbound_arrival_time': inbound_arrival_time,
                        'origin': origin,
                        'destination': destination,
                        'segments': len(outbound_segments)
                    }
                    
                    flights.append(flight)
                    
                except Exception as e:
                    print(f"[Agoda] Error parsing flight bundle: {e}")
                    continue
            
            print(f"[Agoda] ✅ Found {len(flights)} flights")
            return flights
            
        except requests.exceptions.Timeout:
            print(f"[Agoda] Request timeout")
            return []
        except requests.exceptions.RequestException as e:
            print(f"[Agoda] Request error: {e}")
            return []
        except Exception as e:
            print(f"[Agoda] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def _get_place_id(self, client: httpx.AsyncClient, query: str) -> str | None:
        """도시 이름을 Agoda Place ID로 변환"""
        clean_query = re.split(r'[/,]', query)[0].strip()
        
        try:
            print(f"[DEBUG] 🔍 Searching place_id for: {clean_query}")
            
            response = await client.get(
                f"{self.base_url}/hotels/auto-complete",
                headers=self.headers,
                params={"query": clean_query, "language": "en-us"}
            )
            
            print(f"[DEBUG] 🔍 Auto-complete response: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[DEBUG] ❌ Bad status code: {response.status_code}")
                return None
            
            full_response = response.json()
            print(f"[DEBUG] 🔍 Response keys: {list(full_response.keys())}")
            
            # places가 최상위에 있는 경우 처리
            if "places" in full_response and full_response["places"]:
                places_list = full_response["places"]
                print(f"[DEBUG] 🔍 Found {len(places_list)} places")
                
                if isinstance(places_list, list) and places_list:
                    first_place = places_list[0]
                    print(f"[DEBUG] First place: name='{first_place.get('name')}', id={first_place.get('id')}, typeId={first_place.get('typeId')}")
                    
                    place_id = first_place.get("id")
                    type_id = first_place.get("typeId")
                    print(f"[DEBUG] Raw place_id: {place_id}, type_id: {type_id}")
                    
                    # API 형식: "typeId_id" (예: "1_5085")
                    if type_id is not None and place_id is not None:
                        result = f"{type_id}_{place_id}"
                        print(f"[DEBUG] Returning place_id: {result}")
                        return result
                    elif place_id:
                        result = str(place_id)
                        print(f"[DEBUG] Returning place_id (no typeId): {result}")
                        return result
            
            # data 필드 확인 (Fallback)
            data = full_response.get("data", [])
            if isinstance(data, list) and data:
                print(f"[DEBUG] 🔍 Trying fallback data field")
                for item in data:
                    if item.get("id"):
                        result = str(item["id"])
                        print(f"[DEBUG] Returning from data: {result}")
                        return result
                    if "places" in item and item["places"]:
                        result = str(item["places"][0].get("id"))
                        print(f"[DEBUG] Returning from data.places: {result}")
                        return result
            
            print(f"[DEBUG] ❌ No place_id found, returning None")
            return None
            
        except Exception as e:
            print(f"[DEBUG] ❌ _get_place_id error: {e}")
            import traceback
            print(f"[DEBUG] ❌ Traceback: {traceback.format_exc()}")
            return None
    async def search_hotels(self, destination: str, start_date: date, end_date: date, pax: int = 2):
        """호텔 검색"""
        print(f"[DEBUG] 🏨 Hotel search called: destination={destination}, dates={start_date}~{end_date}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            place_id = await self._get_place_id(client, destination)
            print(f"[DEBUG] 🏨 place_id result: {place_id}")
            
            if not place_id:
                print(f"[Agoda] ❌ Could not find place_id for: {destination}")
                return []
            
            print(f"[DEBUG] 🏨 Creating params...")

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
            print(f"[DEBUG] 🏨 About to call API...")
            print(f"[Agoda] 🔍 Searching hotels: {destination} (place_id={place_id})")  

            try:
                print(f"[DEBUG] 🏨 Making request...")
                print(f"[DEBUG] 🏨 URL: {self.base_url}/hotels/search-overnight")
                print(f"[DEBUG] 🏨 Headers: {dict(self.headers)}")
                print(f"[DEBUG] 🏨 Params: {params}")
                response = await client.get(
                    f"{self.base_url}/hotels/search-overnight",
                    headers=self.headers,
                    params=params
                )
                print(f"[DEBUG] 🏨 Response received: {response.status_code}")
                print(f"[Agoda] 🔍 Hotel API Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    return []
                
                response_data = response.json()
                
                print(f"[Agoda] 🔍 Hotel Response keys: {list(response_data.keys())}")
                print(f"[Agoda] 🔍 Hotel Status: {response_data.get('status')}")

                if "errors" in response_data:
                    print(f"[Agoda] 🔍 Hotel Errors: {response_data.get('errors')}")
                
                # 에러 체크
                if response_data.get("status") == False:
                    print(f"[DEBUG] 🏨 API returned status=false")
                    return []
                
                if response_data.get("errors"):
                    print(f"[DEBUG] 🏨 API returned errors: {response_data.get('errors')}")
                    return []

                data = response_data.get("data")
                if data is None:
                    print(f"[Agoda] ❌ No 'data' field in response")
                    return []
                
                print(f"[Agoda] 🔍 Data keys: {list(data.keys())}")
                
                # Agoda API 응답 구조 파싱
                hotels = []
                if "properties" in data:
                    hotels = data["properties"]  # ← 예시 응답 구조
                elif "searchResult" in data:
                    search_result = data.get("searchResult", {})
                    hotels = search_result.get("properties", [])
                elif "citySearch" in data:
                    city_search = data["citySearch"]
                    search_result = city_search.get("searchResult", {})
                    hotels = search_result.get("properties") or city_search.get("properties") or []
                
                print(f"[Agoda] 🔍 Found {len(hotels)} hotels")
                
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
                    
                    # ✅ 가격 추출 (정확한 경로)
                    price_val = 0
                    price_currency = "KRW"
                    try:
                        # API 응답 구조: pricing.offers[0].roomOffers[0].room.pricing[0].price.perRoomPerNight.exclusive.display
                        offers = pricing.get("offers", [])
                        if offers and len(offers) > 0:
                            room_offers = offers[0].get("roomOffers", [])
                            if room_offers and len(room_offers) > 0:
                                room = room_offers[0].get("room", {})
                                room_pricing = room.get("pricing", [])
                                if room_pricing and len(room_pricing) > 0:
                                    price_data = room_pricing[0]
                                    
                                    # 통화 확인
                                    price_currency = price_data.get("currency", "USD").upper()
                                    
                                    # 가격 추출
                                    price_obj = price_data.get("price", {})
                                    per_room = price_obj.get("perRoomPerNight", {})
                                    exclusive = per_room.get("exclusive", {})
                                    price_val = exclusive.get("display", 0)
                        
                        # ✅ USD인 경우에만 KRW로 변환
                        if price_val > 0 and price_currency == "USD":
                            exchange_rate = self._get_usd_to_krw_rate()
                            price_val = int(price_val * exchange_rate)
                            print(f"[Agoda] 💱 Converted {price_val / exchange_rate:.2f} USD → {price_val} KRW")
                        elif price_val > 0:
                            price_val = int(price_val)
                            
                    except Exception as e:
                        print(f"[Agoda] ❌ Price extraction error for hotel {property_id}: {e}")
                        price_val = 0
                    
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
                        if isinstance(images, dict) and "hotelImages" in images:
                            hotel_images = images["hotelImages"]
                            if hotel_images and isinstance(hotel_images, list):
                                urls = hotel_images[0].get("urls", [])
                                if urls:
                                    img_url = urls[0].get("value")
                        elif isinstance(images, list) and images:
                            # 이미지가 리스트인 경우
                            img_url = images[0] if isinstance(images[0], str) else images[0].get("url")
                    
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
                
                print(f"[Agoda] ✅ Returning {len(parsed_hotels)} hotels")
                return parsed_hotels
                
            except Exception as e:
                print(f"[Agoda] ❌ Hotel search error: {e}")
                import traceback
                print(f"[DEBUG] 🏨 Traceback: {traceback.format_exc()}")
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
        
        async with httpx.AsyncClient(timeout=30.0) as client:
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