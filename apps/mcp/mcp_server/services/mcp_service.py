# mcp/mcp_server/services/mcp_service.py
import asyncio
import re
import json
import os
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
                "date": f"Day {day_num}",
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
            travel_style: LLM이 선택한 스타일 (foodie, sightseeing, relaxation, activity, shopping)
        
        Returns:
            str: 해당 스타일의 MD 파일 내용
        """
        # 유효한 스타일 목록
        valid_styles = ['relaxation', 'sightseeing', 'foodie', 'activity', 'shopping']
        
        # 기본값 처리
        if travel_style not in valid_styles:
            print(f"[MCP] ⚠️ Invalid style '{travel_style}', using 'sightseeing'")
            travel_style = 'sightseeing'
        
        print(f"[MCP] 📋 Loading style guide: {travel_style}")
        
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
            
            # 최종 파일 경로
            prompt_path = os.path.join(prompts_dir, f'schedule_style_{travel_style}.md')
            print(f"[MCP] 📂 Looking for: {prompt_path}")
            print(f"[MCP] 📂 File exists: {os.path.exists(prompt_path)}")
            
            # 폴더 내 파일 목록 출력
            if os.path.exists(prompts_dir):
                files = os.listdir(prompts_dir)
                print(f"[MCP] 📂 Files in prompts dir: {files}")
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[MCP] ✅ Loaded {travel_style} style guide: {len(content)} chars")
                return content
                
        except FileNotFoundError:
            print(f"[MCP] ❌ Style file not found: schedule_style_{travel_style}.md")
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
            travel_style: LLM이 선택한 여행 스타일 (foodie, sightseeing 등)
            interests: 사용자 관심사
            poi_list: POI 목록 (평점 포함)
        
        Returns:
            List[Dict]: 날짜별 일정
        """
        # LLM이 없으면 기본 일정
        if not self.llm_model:
            print("[MCP] ⚠️ LLM not available, using default schedule")
            return self._generate_default_schedule(start_date, end_date)
        
        # 1. 스타일 프롬프트 로드
        style_guide = self._load_schedule_style_prompt(travel_style)
        
        # 2. POI 필터링 (평점 4.0 이상)
        high_rated_pois = [
            poi for poi in poi_list 
            if poi.get('rating', 0) >= 4.0
        ]
        
        # 3. POI 카테고리별 분류
        restaurants = [p for p in high_rated_pois if 'restaurant' in p.get('types', []) or '음식점' in p.get('category', '')]
        cafes = [p for p in high_rated_pois if 'cafe' in p.get('types', []) or '카페' in p.get('category', '')]
        attractions = [p for p in high_rated_pois if 'tourist_attraction' in p.get('types', []) or '관광' in p.get('category', '')]
        
        print(f"[MCP] 🏪 POI Categories - Restaurants: {len(restaurants)}, Cafes: {len(cafes)}, Attractions: {len(attractions)}")
        
        # 4. LLM 프롬프트 생성
        # POI를 미리 JSON 문자열로 변환
        restaurants_json = json.dumps(
            [{"name": r.get("name"), "rating": r.get("rating"), "vicinity": r.get("vicinity")} 
             for r in restaurants[:10]], 
            ensure_ascii=False, indent=2
        )
        
        cafes_json = json.dumps(
            [{"name": c.get("name"), "rating": c.get("rating"), "vicinity": c.get("vicinity")} 
             for c in cafes[:10]], 
            ensure_ascii=False, indent=2
        )
        
        attractions_json = json.dumps(
            [{"name": a.get("name"), "rating": a.get("rating"), "vicinity": a.get("vicinity")} 
             for a in attractions[:10]], 
            ensure_ascii=False, indent=2
        )
        
        prompt = f"""
You are a professional travel planner. Create a detailed day-by-day itinerary.

# Travel Information
- Destination: {destination}
- Dates: {start_date.isoformat()} to {end_date.isoformat()}
- Duration: {(end_date - start_date).days + 1} days
- Travel Style: {travel_style}
- Interests: {', '.join(interests)}

# Style Guide
{style_guide}

# Available POIs (Rating 4.0+)
## Restaurants (Rating 4.3+)
{restaurants_json}

## Cafes (Rating 4.2+)
{cafes_json}

## Attractions (Rating 4.0+)
{attractions_json}

# Instructions
1. Follow the style guide strictly
2. Use high-rated POIs (4.3+ for restaurants, 4.0+ for attractions)
3. Include cafes as separate activities
4. Keep meal times realistic (1-1.5 hours)
5. Add walking/digestion time between meals

Return ONLY valid JSON array:
[
  {{
    "day": 1,
    "date": "Day 1",
    "full_date": "{start_date.isoformat()}",
    "events": [
      {{
        "time_slot": "09:00",
        "description": "[POI Name] Activity description (Rating: 4.5)",
        "icon": "utensils",
        "poi_name": "POI Name",
        "poi_rating": 4.5
      }}
    ]
  }}
]
"""
        
        # 5. LLM 호출
        try:
            response = self.llm_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # JSON 추출
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            schedule = json.loads(result_text)
            
            print(f"[MCP] ✅ Generated {len(schedule)} days schedule with {travel_style} style")
            return schedule
            
        except Exception as e:
            print(f"[MCP] ⚠️ LLM schedule generation failed: {e}")
            # Fallback: 기본 일정 생성
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

    async def generate_trip_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[MCP] generate_trip_data Start")
        try:
            if 'llm_parsed_data' in request_data:
                llm_data = request_data['llm_parsed_data'] if isinstance(request_data, dict) else getattr(request_data, 'llm_parsed_data')
                user_style = request_data.get("user_preferred_style", []) if isinstance(request_data, dict) else getattr(request_data, "user_preferred_style", [])
                request_id = request_data.get("request_id", "mcp") if isinstance(request_data, dict) else getattr(request_data, "request_id", "mcp")
            else:
                llm_data = request_data
                user_style = request_data.get("user_preferred_style", [])
                request_id = "mcp"
            
            dest = self._get_safe_value(llm_data, 'destination')
            origin = self._get_safe_value(llm_data, 'origin') or "Seoul"
            start = self._get_safe_value(llm_data, 'start_date')
            end = self._get_safe_value(llm_data, 'end_date')
            
            s_date = date.fromisoformat(start) if isinstance(start, str) else start
            e_date = date.fromisoformat(end) if isinstance(end, str) else end
            pax = self._get_safe_value(llm_data, 'party_size', 1)
            
            # ✅ travel_style 추출
            travel_style = self._get_safe_value(llm_data, 'travel_style', 'sightseeing')
            interests = self._get_safe_value(llm_data, 'interests', ['관광'])
            
            print(f"[MCP] Travel Style: {travel_style}, Interests: {interests}")
            
            # ✅ budget 처리 (딕셔너리일 경우 amount 추출)
            budget_raw = self._get_safe_value(llm_data, 'budget_per_person') or self._get_safe_value(llm_data, 'budget') or 0
            if isinstance(budget_raw, dict):
                budget = budget_raw.get('amount', 0)
            else:
                budget = budget_raw
            
        except Exception as e:
            print(f"[MCP] Input Parse Error: {e}")
            return {"error": str(e)}

        results = await asyncio.gather(
            self.poi_client.search_pois(dest, False, user_style),
            self.weather_client.get_weather_forecast(dest, s_date, e_date),
            self.agoda_client.search_flights(origin, dest, s_date, e_date, pax),
            self.agoda_client.search_hotels(dest, s_date, e_date, pax),
            return_exceptions=True
        )

        poi_data = results[0] if not isinstance(results[0], Exception) else []
        weather_data = results[1] if not isinstance(results[1], Exception) else {}
        flight_data = results[2] if not isinstance(results[2], Exception) else []
        hotel_data = results[3] if not isinstance(results[3], Exception) else []

        norm_pois = []
        for p in poi_data:
            if isinstance(p, dict):
                np = p.copy()
                if 'lat' in np: np['latitude'] = np['lat']
                if 'lng' in np: np['longitude'] = np['lng']
                norm_pois.append(np)
        
        # ✅ 스타일 기반 일정 생성
        raw_schedule = self._generate_schedule_with_style(
            destination=dest,
            start_date=s_date,
            end_date=e_date,
            travel_style=travel_style,
            interests=interests,
            poi_list=norm_pois
        )
        
        # ✅ 비어있으면 기본 일정 생성
        if not raw_schedule:
            print("[MCP] ⚠️ No schedule generated, using default schedule")
            raw_schedule = self._generate_default_schedule(s_date, e_date)

        arrival_time = None
        if flight_data: arrival_time = flight_data[0].get("arrival_time")
        
        # 1. 일정 조정 (시간 기준)
        if arrival_time: adjusted_schedule = self._adjust_first_day_schedule(raw_schedule, arrival_time)
        else: adjusted_schedule = raw_schedule

        # 2. 일정 Enrichment (POI 주입)
        enriched_schedule = self._enrich_schedule_with_pois(adjusted_schedule, norm_pois)

        final_flight_list = []
        for f in flight_data:
            f_clean = f.copy()
            if 'price_total' in f_clean:
                f_clean['price_total'] = self._sanitize_price(f_clean['price_total'])
                f_clean['price'] = f_clean['price_total']
            final_flight_list.append(f_clean)

        final_hotel_list = []
        for h in hotel_data:
            h_clean = h.copy()
            if 'price' in h_clean: h_clean['price'] = self._sanitize_price(h_clean['price'])
            final_hotel_list.append(h_clean)

        response_data = {
            "destination": dest,
            "dates": {"start": s_date.isoformat(), "end": e_date.isoformat()},
            "trip_duration_nights": (e_date - s_date).days,
            "party_size": pax,
            "budget_per_person": budget,
            "poi_list": norm_pois,
            "weather_info": weather_data,
            "flight_candidates": final_flight_list, 
            "hotel_candidates": final_hotel_list,
            "flight_quote": final_flight_list[0] if final_flight_list else {},
            "hotel_quote": final_hotel_list,
            "schedule": enriched_schedule
        }
        
        print(f"[{request_id}] MCP Done. Flights: {len(final_flight_list)}, Hotels: {len(final_hotel_list)}")
        print(f"[MCP] 📅 Schedule in response_data: {len(response_data.get('schedule', []))}")
        
        return response_data

mcp_service_instance = MCPService()
def get_mcp_service(): return mcp_service_instance