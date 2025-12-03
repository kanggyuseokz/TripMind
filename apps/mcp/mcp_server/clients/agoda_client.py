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
        """
        특정 통화의 매매기준율(KRW) 조회
        
        Args:
            currency_code: 통화 코드 (USD, JPY, EUR 등)
            search_date: 검색 날짜 (YYYYMMDD 또는 YYYY-MM-DD, 기본값: 오늘)
        
        Returns:
            float: 매매기준율 (KRW)
        """
        if not self.enabled:
            return 1300.0  # Fallback
        
        try:
            params = {
                "authkey": self.auth_key,
                "data": self.data_code
            }
            
            # 날짜 파라미터 추가 (옵션)
            if search_date:
                params["searchdate"] = search_date
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10,
                verify=False  # SSL 검증 비활성화
            )
            response.raise_for_status()
            rows = response.json()
            
            # ✅ 응답 검증
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
            
            # 통화 검색
            for row in rows:
                cur_unit = row.get("cur_unit", "")
                
                # 통화 코드 매칭 (JPY(100) 같은 형식 처리)
                if cur_unit.upper().startswith(currency_code.upper()):
                    deal_bas_r = row.get("deal_bas_r", "0")
                    
                    # 쉼표 제거 및 float 변환
                    try:
                        base_rate = float(deal_bas_r.replace(",", ""))
                    except (ValueError, AttributeError):
                        print(f"[ExchangeService] ⚠️ Invalid rate value: {deal_bas_r}")
                        continue
                    
                    # 단위 보정 (JPY(100), IDR(100), ESP(100) 등)
                    match = re.search(r"\((\d+)\)", cur_unit)
                    if match:
                        divisor = int(match.group(1))
                        if divisor > 0:
                            base_rate /= divisor
                    
                    print(f"[ExchangeService] ✅ {cur_unit}: {base_rate} KRW")
                    return base_rate
            
            print(f"[ExchangeService] ⚠️ Currency '{currency_code}' not found")
            return 1300.0  # Fallback
            
        except requests.RequestException as e:
            print(f"[ExchangeService] ⚠️ API request failed: {e}")
            return 1300.0  # Fallback
        except Exception as e:
            print(f"[ExchangeService] ⚠️ Unexpected error: {e}")
            return 1300.0  # Fallback


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
        url = "https://agoda-com-flight.p.rapidapi.com/api/v1/flights/search-roundtrip"
        
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
            "x-rapidapi-host": "agoda-com-flight.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('status'):
            print(f"[Agoda] API returned status=false")
            return []
        
        bundles = data.get('data', {}).get('bundles', [])
        
        if not bundles:
            print(f"[Agoda] No flight bundles found")
            return []
        
        flights = []
        
        for bundle in bundles[:10]:  # 상위 10개만
            try:
                # 가격 정보
                price_info = bundle.get('bundlePrice', [{}])[0].get('price', {}).get('usd', {})
                price_usd = price_info.get('display', {}).get('perBook', {}).get('allInclusive', 0)
                
                # USD → KRW 변환
                price_krw = int(price_usd * self.usd_to_krw_rate)
                print(f"[Agoda] ✅ Price in KRW: {price_krw}")
                
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
                inbound_slice = bundle.get('inboundSlice')
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
                    'outbound_departure_time': outbound_departure_time,  # ✅ 추가
                    'outbound_arrival_time': outbound_arrival_time,      # ✅ 추가
                    'inbound_departure_time': inbound_departure_time,    # ✅ 추가
                    'inbound_arrival_time': inbound_arrival_time,        # ✅ 추가
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
                            print(f"[Agoda] ✅ Price in {price_currency}: {price_val}")
                            
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
                        if isinstance(images, list) and images:
                            hotel_images = images.get("hotelImages", [])
                            if hotel_images:
                                urls = hotel_images[0].get("urls", [])
                                if urls:
                                    img_url = urls[0].get("value")
                    
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
                
            except Exception as e:
                print(f"[Agoda] ❌ Hotel search error: {e}")
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