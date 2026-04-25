# mcp/mcp_server/services/mcp_service.py
import asyncio
import re
import json
import os
import random
import httpx
from datetime import date, datetime, timedelta
from typing import Dict, Any, List
import google.generativeai as genai

from ..clients.poi_client import PoiClient
from ..clients.weather_client import WeatherClient
from ..clients.agoda_client import AgodaClient
from ..config import settings

class MCPService:
    def __init__(self):
        self.poi_client = PoiClient()
        self.weather_client = WeatherClient()
        self.agoda_client = AgodaClient()
        self.valid_styles = {
            'foodie': ['맛집', '음식', '미식', '식도락', '요리', '레스토랑', 'restaurant', 'food'],
            'relaxation': ['휴양', '휴식', '느긋', '여유', '스파', '힐링', 'spa', 'relax', '휴양지', '휴양형'],
            'activity': ['액티비티', '체험', '스포츠', '등산', '다이빙', '서핑', 'activity', 'sport'],
            'shopping': ['쇼핑', '면세점', '구매', '백화점', '아울렛', 'shopping', 'mall'],
            'sightseeing': ['관광', '여행', '구경', '투어', '명소', '랜드마크', 'tour', 'sight']
        }
        
        # ✅ LLM 모델 초기화
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.llm_model = genai.GenerativeModel('gemini-2.5-flash')
            print("[MCP] ✅ LLM initialized")
        except Exception as e:
            print(f"[MCP] ⚠️ LLM initialization failed: {e}")
            self.llm_model = None

    def _get_safe_value(self, obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict): return obj.get(key, default)
        return getattr(obj, key, default)

    def _sanitize_price(self, price_raw: Any) -> int:
        if not price_raw: return 0
        try:
            if isinstance(price_raw, str):
                clean_str = re.sub(r'[^\d.]', '', price_raw)
                return int(float(clean_str))
            return int(price_raw)
        except: return 0

    def _parse_time(self, time_str: str) -> int:
        try:
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        except: return 0
    
    def _generate_default_schedule(self, start_date: date, end_date: date) -> List[Dict]:
        """기본 일정 생성"""
        schedule = []
        current_date = start_date
        day_num = 1
        
        while current_date <= end_date:
            day_schedule = {
                "day": day_num,
                "date": f"{day_num}일차",
                "full_date": current_date.isoformat(),
                "events": [
                    {"time_slot": "09:00", "description": "호텔 출발 및 관광 시작", "icon": "car"},
                    {"time_slot": "12:00", "description": "점심 식사", "icon": "utensils"},
                    {"time_slot": "14:00", "description": "오후 관광", "icon": "camera"},
                    {"time_slot": "18:00", "description": "저녁 식사 및 자유 시간", "icon": "utensils"},
                    {"time_slot": "21:00", "description": "호텔 복귀", "icon": "home"}
                ]
            }
            schedule.append(day_schedule)
            current_date += timedelta(days=1)
            day_num += 1
        
        return schedule
    
    def _load_schedule_style_prompt(self, travel_style: str) -> str:
        """
        여행 스타일에 맞는 프롬프트 로드
        
        Args:
            travel_style: 사용자 입력 스타일 (한국어 또는 영어)
        
        Returns:
            str: 해당 스타일의 MD 파일 내용
        """
        
        # ✅ 한국어 입력을 영어 스타일로 매핑
        mapped_style = None
        input_lower = travel_style.lower().strip()
        
        print(f"[MCP] 🔍 Mapping input style: '{travel_style}'")
        
        for style_key, keywords in self.valid_styles.items():
            if input_lower in [k.lower() for k in keywords]:
                mapped_style = style_key
                break
        
        # 매핑된 스타일이 있으면 사용, 없으면 원본 사용
        final_style = mapped_style if mapped_style else travel_style
        
        # 최종 검증 (영어 키에 없으면 기본값)
        if final_style not in self.valid_styles:
            print(f"[MCP] ⚠️ Invalid style '{final_style}', using 'sightseeing'")
            final_style = 'sightseeing'
        
        print(f"[MCP] 📋 Input: '{travel_style}' → Mapped: '{final_style}'")
        print(f"[MCP] 📋 Loading style guide: {final_style}")
        
        # MD 파일 읽기
        try:
            # ✅ 현재 파일의 절대 경로 기준으로 계산
            current_file = os.path.abspath(__file__)
            print(f"[MCP] 📂 Current file: {current_file}")
            
            # services/mcp_service.py → services 폴더
            services_dir = os.path.dirname(current_file)
            print(f"[MCP] 📂 Services dir: {services_dir}")
            
            # services → mcp_server 폴더
            mcp_server_dir = os.path.dirname(services_dir)
            print(f"[MCP] 📂 MCP server dir: {mcp_server_dir}")
            
            # mcp_server/prompts 폴더
            prompts_dir = os.path.join(mcp_server_dir, 'prompts')
            print(f"[MCP] 📂 Prompts dir: {prompts_dir}")
            print(f"[MCP] 📂 Prompts dir exists: {os.path.exists(prompts_dir)}")
            
            # ✅ 최종 파일 경로 (매핑된 스타일 사용)
            prompt_path = os.path.join(prompts_dir, f'schedule_style_{final_style}.md')
            print(f"[MCP] 📂 Looking for: {prompt_path}")
            print(f"[MCP] 📂 File exists: {os.path.exists(prompt_path)}")
            
            # 폴더 내 파일 목록 출력
            if os.path.exists(prompts_dir):
                files = os.listdir(prompts_dir)
                print(f"[MCP] 📂 Files in prompts dir: {files}")
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[MCP] ✅ Loaded {final_style} style guide: {len(content)} chars")
                return content
                
        except FileNotFoundError:
            print(f"[MCP] ❌ Style file not found: schedule_style_{final_style}.md")
            print(f"[MCP] ❌ Searched path: {prompt_path}")
            return ""
        except Exception as e:
            print(f"[MCP] ❌ Failed to load style prompt: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _generate_schedule_with_style(
        self,
        destination: str,
        start_date: date,
        end_date: date,
        travel_style: str,
        interests: List[str],
        poi_list: List[Dict]
    ) -> List[Dict]:
        """
        POI와 스타일 가이드를 기반으로 일정 생성
        
        Args:
            destination: 목적지
            start_date: 시작 날짜
            end_date: 종료 날짜
            travel_style: 사용자 입력 여행 스타일 (한국어 가능)
            interests: 사용자 관심사
            poi_list: POI 목록 (평점 포함)
        
        Returns:
            List[Dict]: 날짜별 일정
        """
        # LLM이 없으면 기본 일정
        if not self.llm_model:
            print("[MCP] ⚠️ LLM not available, using default schedule")
            return self._generate_default_schedule(start_date, end_date)
        
        # 1. 스타일 프롬프트 로드 (primary + secondary)
        style_guide = self._load_schedule_style_prompt(travel_style)
        # interests에 valid style ID가 있으면 secondary md도 로드해서 추가
        secondary_guides = []
        for interest in interests:
            if interest != travel_style and interest in self.valid_styles:
                sg = self._load_schedule_style_prompt(interest)
                if sg:
                    secondary_guides.append(f"### 보조 스타일 ({interest})\n{sg}")
        if secondary_guides:
            style_guide += "\n\n## 보조 스타일 가이드 (참고)\n" + "\n\n".join(secondary_guides)
        
        # 2. POI 필터링 (평점 3.5 이상) + 셔플로 매번 다른 POI 노출
        high_rated_pois = [p for p in poi_list if p.get('rating', 0) >= 3.5]
        random.shuffle(high_rated_pois)

        # 3. POI 카테고리별 분류 (poi_client가 저장하는 실제 category 값 기준)
        def _is_restaurant(p):
            cat = p.get('category', '')
            return '맛집' in cat or '음식점' in cat or '식당' in cat or 'restaurant' in p.get('types', [])

        def _is_cafe(p):
            cat = p.get('category', '')
            return '카페' in cat or 'cafe' in cat or 'coffee' in cat or 'cafe' in p.get('types', [])

        def _is_attraction(p):
            cat = p.get('category', '')
            return '관광' in cat or '명소' in cat or '공원' in cat or '박물관' in cat or 'tourist_attraction' in p.get('types', [])

        restaurants = [p for p in high_rated_pois if _is_restaurant(p)]
        cafes       = [p for p in high_rated_pois if _is_cafe(p) and not _is_restaurant(p)]
        attractions = [p for p in high_rated_pois if _is_attraction(p) and not _is_restaurant(p) and not _is_cafe(p)]

        # 부족한 카테고리는 전체 POI에서 보충
        if len(restaurants) < 3:
            restaurants += [p for p in high_rated_pois if p not in restaurants][:5]
        if len(attractions) < 3:
            attractions += [p for p in high_rated_pois if p not in attractions][:5]

        print(f"[MCP] 🏪 POI Categories - Restaurants: {len(restaurants)}, Cafes: {len(cafes)}, Attractions: {len(attractions)}")
        
        # 4. LLM 프롬프트 생성 — 일자별 POI 배분 (중복 방지)
        num_days = (end_date - start_date).days + 1

        # 일자별로 POI를 미리 분배해서 프롬프트에 포함 (같은 POI 반복 방지)
        def _slice_for_day(lst, day_idx, per_day=3):
            start = (day_idx * per_day) % max(len(lst), 1)
            items = lst[start:start + per_day]
            if len(items) < per_day:
                items += lst[:per_day - len(items)]
            return items

        days_poi_sections = []
        for d in range(num_days):
            day_restaurants = _slice_for_day(restaurants, d, 2)
            day_cafes       = _slice_for_day(cafes, d, 1)
            day_attractions = _slice_for_day(attractions, d, 3)
            days_poi_sections.append(
                f"### {d+1}일차 배정 장소\n"
                f"관광: {', '.join(a.get('name','') for a in day_attractions)}\n"
                f"식사: {', '.join(r.get('name','') for r in day_restaurants)}\n"
                f"카페: {', '.join(c.get('name','') for c in day_cafes)}"
            )
        days_poi_text = "\n".join(days_poi_sections)

        prompt = f"""
당신은 전문 여행 플래너입니다. 상세한 날짜별 여행 일정을 한국어로 작성해주세요.

# 여행 정보
- 여행지: {destination}
- 날짜: {start_date.isoformat()} ~ {end_date.isoformat()}
- 기간: {num_days}일
- 여행 스타일: {travel_style}
- 관심사: {', '.join(interests)}

# 스타일 가이드
{style_guide}

# 일자별 배정 장소 (반드시 이 장소들을 poi_name으로 사용)
{days_poi_text}

# 절대 규칙 (위반 금지)
1. **같은 poi_name을 하루 안에 두 번 이상 쓰지 말 것** — 각 이벤트는 반드시 서로 다른 장소
2. 위 "일자별 배정 장소"에 있는 이름을 poi_name 필드에 그대로 사용할 것
3. "(인근 POI 활용)" 같은 표현 절대 금지 — 구체적인 장소명만 사용
4. description은 반드시 한국어로 작성 (예: "루브르 박물관 관람 및 모나리자 감상")
5. 식사 시간: 점심 12:00~13:30, 저녁 18:30~20:00
6. 이동·휴식 시간 포함, 하루 5~7개 이벤트

반드시 아래 형식의 JSON 배열만 반환하세요 (코드블록 없이):
[
  {{
    "day": 1,
    "date": "1일차",
    "full_date": "{start_date.isoformat()}",
    "events": [
      {{
        "time_slot": "09:00",
        "description": "한국어로 작성한 활동 설명",
        "icon": "camera",
        "poi_name": "위 배정 장소 중 하나의 이름",
        "poi_rating": 4.5
      }}
    ]
  }}
]
"""
        
        # 5. LLM 호출 (동기 함수이므로 결과 반환)
        try:
            response = self.llm_model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            result_text = response.text.strip()

            # JSON 추출
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            schedule = json.loads(result_text)

            print(f"[MCP] ✅ Generated {len(schedule)} days schedule with {travel_style} style")
            return schedule

        except Exception as e:
            print(f"[MCP] ⚠️ LLM schedule generation failed: {e}")
            return self._generate_default_schedule(start_date, end_date)

    def _adjust_first_day_schedule(self, schedule: List[Any], arrival_time_str: str) -> List[Any]:
        print(f"[DEBUG] _adjust_first_day_schedule Called. Arrival: {arrival_time_str}")
        if not schedule:
            print("[DEBUG] Schedule is empty, skipping adjustment.")
            return schedule
        if not arrival_time_str:
            print("[DEBUG] Arrival time is empty, skipping adjustment.")
            return schedule

        first_day = schedule[0]
        events = self._get_safe_value(first_day, 'events', [])
        print(f"[DEBUG] Original First Day Events: {len(events)}")
        
        if 'T' in arrival_time_str: arrival_time_str = arrival_time_str.split('T')[1][:5]
        arrival_minutes = self._parse_time(arrival_time_str)
        start_tour_minutes = arrival_minutes + 120 
        
        valid_events = []
        for event in events:
            time_slot = (event.get('time_slot') if isinstance(event, dict) else getattr(event, 'time_slot', '')).strip()
            event_minutes = 0
            if '오전' in time_slot or '아침' in time_slot: event_minutes = 9 * 60
            elif '점심' in time_slot: event_minutes = 12 * 60
            elif '오후' in time_slot: event_minutes = 14 * 60
            elif '저녁' in time_slot: event_minutes = 18 * 60
            elif '밤' in time_slot: event_minutes = 20 * 60
            
            if event_minutes >= start_tour_minutes: valid_events.append(event)
        
        print(f"[DEBUG] Adjusted First Day Events: {len(valid_events)}")
        
        if not valid_events:
            msg = {"time_slot": "알림", "description": f"항공편이 늦게({arrival_time_str}) 도착하여 첫날은 휴식합니다.", "icon": "home"}
            valid_events.append(msg)
        elif len(valid_events) < len(events):
            arrival_msg = {"time_slot": "도착", "description": f"공항 도착 ({arrival_time_str})", "icon": "plane"}
            valid_events.insert(0, arrival_msg)

        if isinstance(first_day, dict): first_day['events'] = valid_events
        else: setattr(first_day, 'events', valid_events)
        return schedule

    def _enrich_schedule_with_pois(self, schedule: List[Any], pois: List[Dict]) -> List[Any]:
        print(f"[DEBUG] _enrich_schedule_with_pois Called. POIs Count: {len(pois)}")
        if not schedule: return schedule
        
        if not pois:
            print("[DEBUG] ⚠️ No POIs found! Enrichment skipped.")
            return schedule

        dining_pois = [p for p in pois if any(x in p.get('category','').lower() for x in ['식당','맛집','카페','restaurant','cafe'])]
        tourist_pois = [p for p in pois if p not in dining_pois]
        
        print(f"[DEBUG] Dining POIs: {len(dining_pois)}, Tourist POIs: {len(tourist_pois)}")

        enriched_count = 0
        for day in schedule:
            events = self._get_safe_value(day, 'events', [])
            for event in events:
                is_dict = isinstance(event, dict)
                desc = (event.get('description') if is_dict else getattr(event, 'description', '')).lower()
                icon = (event.get('icon') if is_dict else getattr(event, 'icon', '')).lower()
                
                if '도착' in desc or '이동' in desc or '알림' in desc: continue

                selected = None
                if '식사' in desc or '맛집' in desc or '점심' in desc or '저녁' in desc or icon in ['utensils', 'coffee']:
                    if dining_pois:
                        selected = dining_pois.pop(0)
                        dining_pois.append(selected)
                else:
                    if tourist_pois:
                        selected = tourist_pois.pop(0)
                        tourist_pois.append(selected)
                    elif dining_pois:
                        selected = dining_pois.pop(0)
                        dining_pois.append(selected)

                if selected:
                    enriched_count += 1
                    new_name = selected['name']
                    new_desc = f"{selected.get('category', '명소')} - {desc}"
                    
                    if is_dict:
                        event['place_name'] = new_name
                        event['description'] = new_desc
                        event['latitude'] = selected.get('lat')
                        event['longitude'] = selected.get('lng')
                    else:
                        setattr(event, 'place_name', new_name)
                        setattr(event, 'description', new_desc)
                        setattr(event, 'latitude', selected.get('lat'))
                        setattr(event, 'longitude', selected.get('lng'))
        
        print(f"[DEBUG] Total Enriched Events: {enriched_count}")
        return schedule

    async def generate_trip_data(self, llm_parsed_data: dict) -> dict:
        """
        MCP 서버의 핵심 로직: 항공, 호텔, POI, 날씨, 일정을 종합적으로 생성
        
        Returns:
            dict: 다음 필드를 포함:
                - dates: {"start": "2025-12-06", "end": "2025-12-10"}
                - flight_candidates: 항공편 목록 (시간 정보 포함)
                - flight_quote: 추천 항공편 (시간 정보 포함)
                - hotel_candidates: 호텔 목록
                - schedule: 일정 (날짜별 날씨 포함)
                - weather_info: 날씨 정보
                - weather_by_date: 날짜별 날씨 매핑
        """
        try:
            print("[MCP] generate_trip_data Start")
            
            llm_data = llm_parsed_data.get('llm_parsed_data', llm_parsed_data)
            
            # 기본 정보 추출
            dest = self._get_safe_value(llm_data, 'destination')
            origin = self._get_safe_value(llm_data, 'origin') or "Seoul"
            start = self._get_safe_value(llm_data, 'start_date')
            end = self._get_safe_value(llm_data, 'end_date')
            
            s_date = date.fromisoformat(start) if isinstance(start, str) else start
            e_date = date.fromisoformat(end) if isinstance(end, str) else end
            pax = self._get_safe_value(llm_data, 'party_size', 1)
            
            # ✅ interests 먼저 추출
            interests = (
                self._get_safe_value(llm_data, 'interests') or
                self._get_safe_value(llm_parsed_data, 'interests') or
                ['관광']
            )
            
            print(f"[MCP] 🔍 Raw interests: {interests}")

            # ✅ 1순위: interests에 valid style ID가 직접 포함된 경우 (체크박스 직접 전달)
            explicit_style = next((i for i in interests if i in self.valid_styles), None)
            if explicit_style:
                travel_style = explicit_style
                print(f"[MCP] ✅ Explicit style ID from interests: '{travel_style}'")
            else:
                # ✅ 2순위: llm_data의 travel_style 필드
                llm_style = (
                    self._get_safe_value(llm_data, 'travel_style') or
                    self._get_safe_value(llm_parsed_data, 'travel_style')
                )
                if llm_style and llm_style in self.valid_styles:
                    travel_style = llm_style
                    print(f"[MCP] ✅ travel_style from LLM field: '{travel_style}'")
                else:
                    # ✅ 3순위: interests 한국어 키워드 매핑
                    interests_str = ' '.join(interests).lower()
                    if any(k in interests_str for k in ['휴양', '휴식', '스파', '힐링', '리조트']):
                        travel_style = 'relaxation'
                    elif any(k in interests_str for k in ['맛집', '음식', '미식', '식도락']):
                        travel_style = 'foodie'
                    elif any(k in interests_str for k in ['쇼핑', '면세점', '구매']):
                        travel_style = 'shopping'
                    elif any(k in interests_str for k in ['액티비티', '체험', '스포츠', '등산']):
                        travel_style = 'activity'
                    else:
                        travel_style = 'sightseeing'
                    print(f"[MCP] ✅ travel_style from keyword matching: '{travel_style}'")
            
            # ✅ 최종 확인
            print(f"[MCP] 🎯 FINAL DEBUG - travel_style before schedule generation: '{travel_style}'")
            
            is_domestic = (
                self._get_safe_value(llm_data, 'is_domestic') or
                self._get_safe_value(llm_parsed_data, 'is_domestic') or
                False
            )
            
            # ✅ budget 처리 (딕셔너리일 경우 amount 추출)
            budget_raw = self._get_safe_value(llm_data, 'budget_per_person') or self._get_safe_value(llm_data, 'budget') or 0
            if isinstance(budget_raw, dict):
                budget = budget_raw.get('amount', 0)
            else:
                budget = budget_raw
            
        except Exception as e:
            print(f"[MCP] Input Parse Error: {e}")
            return {"error": str(e)}
        
        # 병렬 호출
        try:
            # ✅ 항공편을 위한 IATA 코드 변환
            async with httpx.AsyncClient(timeout=30.0) as iata_client:
                dest_iata = await self.agoda_client._get_iata_code(iata_client, dest)
            
            # IATA 코드가 없으면 항공편 검색 스킵
            if not dest_iata:
                print(f"[MCP] ⚠️ Could not find IATA code for '{dest}', skipping flights")
                results = await asyncio.gather(
                    self.poi_client.search_pois(dest, is_domestic),
                    self.weather_client.get_weather_forecast(dest, s_date, e_date),
                    asyncio.sleep(0),  # 빈 슬롯 (항공편 대신)
                    self.agoda_client.search_hotels(dest, s_date.isoformat(), e_date.isoformat(), pax),
                    return_exceptions=True
                )
            else:
                print(f"[MCP] ✅ IATA code for '{dest}': {dest_iata}")
                results = await asyncio.gather(
                    self.poi_client.search_pois(dest, is_domestic),
                    self.weather_client.get_weather_forecast(dest, s_date, e_date),
                    # ✅ 동기 함수를 asyncio.to_thread로 감싸서 호출
                    asyncio.to_thread(
                        self.agoda_client.search_flights,
                        "ICN", dest_iata, s_date.isoformat(), e_date.isoformat(), pax
                    ),
                    self.agoda_client.search_hotels(dest, s_date, e_date, pax),
                    return_exceptions=True
                )
            
            poi_data = results[0] if not isinstance(results[0], Exception) else []
            weather_data = results[1] if not isinstance(results[1], Exception) else {}
            flight_data = results[2] if not isinstance(results[2], Exception) else []
            hotel_data = results[3] if not isinstance(results[3], Exception) else []
            
            # POI normalize
            norm_pois = []
            for p in poi_data:
                if isinstance(p, dict):
                    np = p.copy()
                    if 'lat' in np: np['latitude'] = np['lat']
                    if 'lng' in np: np['longitude'] = np['lng']
                    norm_pois.append(np)
            
            # ✅ 스타일 기반 일정 생성 — 동기 LLM 호출을 thread pool에서 실행 (이벤트 루프 블로킹 방지)
            try:
                raw_schedule = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._generate_schedule_with_style,
                        dest, s_date, e_date, travel_style, interests, norm_pois
                    ),
                    timeout=90.0  # Gemini 90초 타임아웃
                )
            except asyncio.TimeoutError:
                print("[MCP] ⚠️ Schedule generation timed out, using default schedule")
                raw_schedule = self._generate_default_schedule(s_date, e_date)
            
            # ✅ 날씨를 날짜별로 매핑
            weather_by_date = {}
            if weather_data and "daily" in weather_data:
                for day_weather in weather_data["daily"]:
                    date_key = day_weather.get("date")
                    if date_key:
                        weather_by_date[date_key] = {
                            "temp": day_weather.get("temp"),
                            "condition": day_weather.get("condition"),
                            "icon": day_weather.get("icon"),
                            "description": day_weather.get("description")
                        }
            
            # 항공편 데이터 정리 (✅ 시간 정보 유지)
            final_flight_list = []
            for f in flight_data:
                f_clean = f.copy()
                # 시간 필드 유지
                # outbound_departure_time, outbound_arrival_time
                # inbound_departure_time, inbound_arrival_time
                final_flight_list.append(f_clean)
            
            # 호텔 데이터 정리
            final_hotel_list = []
            for h in hotel_data:
                h_clean = h.copy()
                final_hotel_list.append(h_clean)
            
            # ✅ 최종 응답 데이터
            response_data = {
                # ✅ 1. 여행 기간 추가
                "dates": {
                    "start": s_date.isoformat(),
                    "end": e_date.isoformat()
                },
                
                # ✅ 2. 항공편 (시간 정보 포함)
                "flight_candidates": final_flight_list,
                "flight_quote": final_flight_list[0] if final_flight_list else {},
                
                # 3. 호텔
                "hotel_candidates": final_hotel_list,
                "hotel_quote": final_hotel_list[0] if final_hotel_list else {},
                
                # 4. 일정
                "schedule": raw_schedule,
                
                # ✅ 5. 날씨 (원본 + 날짜별)
                "weather_info": weather_data,
                "weather_by_date": weather_by_date,
                
                # 6. POI
                "poi_list": norm_pois[:50],
                
                # 7. 메타데이터
                "destination": dest,
                "party_size": pax,
                "budget_per_person": budget,
                "travel_style": travel_style,
                "interests": interests
            }
            
            print(f"[MCP] ✅ Response generated successfully")
            print(f"[MCP] 📅 Dates: {response_data['dates']}")
            print(f"[MCP] ✈️ Flights: {len(final_flight_list)}")
            print(f"[MCP] 🏨 Hotels: {len(final_hotel_list)}")
            print(f"[MCP] 📋 Schedule days: {len(raw_schedule)}")
            print(f"[MCP] 🌤️ Weather by date: {len(weather_by_date)} days")
            
            return response_data
            
        except Exception as e:
            print(f"[MCP] ❌ Error in generate_trip_data: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

mcp_service_instance = MCPService()
def get_mcp_service(): return mcp_service_instance