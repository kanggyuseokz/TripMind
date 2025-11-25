# backend/tripmind_api/services/trip_service.py
from datetime import datetime, timedelta
import requests

# TripMind의 모든 전문 서비스를 임포트합니다.
from .mcp_service import MCPService
from .scoring_service import ScoringService
from .map_service import MapService

class TripService:
    """
    여행 계획 생성 프로세스를 총괄하는 최종 오케스트레이터.
    MCP(데이터 수집) -> Scoring/Map(분석/최적화) -> 최종 결과 생성
    """
    def __init__(self):
        self.mcp_service = MCPService()
        self.scoring_service = ScoringService()
        self.map_service = MapService()

    def create_personalized_trip(self, request_data: dict, parsed_data: dict) -> dict:
        """
        LLM이 파싱한 데이터를 기반으로, 실제 여행 계획을 생성하는 메인 메소드입니다.
        """
        try:
            user_style = request_data.get('preferred_style', '관광')
            start_date_str = parsed_data.get('start_date')
            end_date_str = parsed_data.get('end_date')
            destination = parsed_data.get('destination')
            party_size = parsed_data.get('party_size', 1)
            is_domestic = parsed_data.get("is_domestic", False)
            
            if not all([start_date_str, end_date_str, destination]):
                raise KeyError("필수 필드 누락")

            # Step 1: MCP 데이터 수집
            mcp_data = self.mcp_service.fetch_all_data(parsed_data, user_style)
            if not mcp_data:
                raise Exception("MCP service failed to fetch data.")

            # Step 2: 여행 기간 계산
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            trip_duration_days = (end_date - start_date).days + 1
            trip_duration_nights = (end_date - start_date).days

            # Step 3: 비용 계산 (ScoringService 인자 개수 수정됨)
            cost_info = self.scoring_service.calculate_total_cost(
                mcp_data.get('flight_quote'), 
                mcp_data.get('hotel_quote'),
                trip_duration_nights,
                party_size,
                destination,
                user_style # 💡 수정된 ScoringService에 맞춰 인자 전달
            )
            
            cost_breakdown_chart = self.scoring_service.calculate_cost_breakdown(
                cost_info.get('costs_by_category', {})
            )

            # Step 4: POI 점수 산정
            scored_pois = self.scoring_service.score_poi_candidates(
                mcp_data.get('poi_list', []), user_style
            )
            
            # Step 5: 일정 최적화 및 배치 (여기가 핵심!)
            final_schedule = self._arrange_schedule_optimized(
                scored_pois, start_date, trip_duration_days, is_domestic
            )

            # Step 6: 최종 결과 반환
            return {
                "trip_summary": f"{destination} {trip_duration_nights}박 {trip_duration_days}일 여행",
                "total_cost": cost_info.get('total_cost'),
                "cost_breakdown_chart": cost_breakdown_chart,
                "schedule": final_schedule,
                # 결과 페이지 복원용 데이터
                "destination": destination,
                "startDate": start_date_str,
                "endDate": end_date_str,
                "partySize": party_size,
                "head_count": party_size,
                "flights": [mcp_data.get('flight_quote')] if mcp_data.get('flight_quote') else [],
                "hotels": [mcp_data.get('hotel_quote')] if mcp_data.get('hotel_quote') else [],
                "raw_data": { 
                    "llm_parsed_request": parsed_data,
                    "mcp_fetched_data": mcp_data
                }
            }
        
        except Exception as e:
            print(f"Error in create_personalized_trip: {e}")
            raise e

    def _arrange_schedule_optimized(self, scored_pois: list[dict], start_date: datetime, trip_duration_days: int, is_domestic: bool) -> list[dict]:
        """점수가 높은 POI들을 기반으로 일정을 생성합니다."""
        schedule = []
        
        # 사용할 POI가 없으면 빈 템플릿이라도 반환
        if not scored_pois:
            scored_pois = [
                {"name": "추천 명소", "category": "관광명소"},
                {"name": "현지 맛집", "category": "맛집"},
                {"name": "분위기 좋은 카페", "category": "카페"},
                {"name": "야경 포인트", "category": "관광명소"},
            ] * trip_duration_days

        # 하루에 배치할 시간대 정의
        time_slots = [
            {"slot": "오전", "type": "관광명소", "icon": "home"},
            {"slot": "점심", "type": "맛집", "icon": "utensils"},
            {"slot": "오후", "type": "카페", "icon": "coffee"},
            {"slot": "저녁", "type": "맛집", "icon": "utensils"},
            {"slot": "밤", "type": "관광명소", "icon": "car"} # 야경 등
        ]

        poi_index = 0
        for i in range(trip_duration_days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%m월 %d일')
            day_events = []

            for slot_info in time_slots:
                # POI 리스트에서 하나씩 꺼내오기 (순환)
                if poi_index < len(scored_pois):
                    poi = scored_pois[poi_index]
                    poi_index += 1
                else:
                    # POI가 모자라면 처음부터 다시 순환하거나 기본값 사용
                    poi = scored_pois[poi_index % len(scored_pois)]
                    poi_index += 1

                day_events.append({
                    "time_slot": slot_info["slot"],
                    "description": f"{poi['name']} ({poi.get('category', '관광')})",
                    "icon": slot_info["icon"]
                })

            schedule.append({
                "day": i + 1,
                "date": f"{i+1}일차",
                "full_date": date_str, # 화면 표시용
                "events": day_events
            })
            
        return schedule