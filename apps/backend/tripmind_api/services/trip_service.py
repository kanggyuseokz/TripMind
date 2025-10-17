from datetime import datetime

# TripMind의 모든 전문 서비스를 임포트합니다.
from .llm_service import LLMService
from .mcp_service import MCPService
from .scoring_service import ScoringService
from .map_service import MapService

class TripService:
    """
    여행 계획 생성 프로세스를 총괄하는 최종 오케스트레이터.
    MCP(데이터 수집) -> Scoring/Map(분석/최적화) -> 최종 결과 생성
    """
    def __init__(self):
        # 각 서비스의 인스턴스를 생성합니다.
        self.mcp_service = MCPService()
        self.scoring_service = ScoringService()
        self.map_service = MapService()

    def create_personalized_trip(self, request_data: dict, parsed_data: dict) -> dict:
        """
        모든 정보가 수집된 후, 실제 여행 계획을 생성하는 메인 메소드입니다.
        """
        # Step 1: MCP 서비스를 호출하여 모든 외부 데이터를 병렬로 수집합니다.
        user_style = request_data.get('preferred_style', '관광')
        mcp_data = self.mcp_service.fetch_all_data(parsed_data, user_style)
        
        # Step 2: 여행 기간(일)을 계산합니다.
        start_date = datetime.strptime(parsed_data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(parsed_data['end_date'], '%Y-%m-%d')
        trip_duration_days = (end_date - start_date).days + 1

        # Step 3: Scoring 서비스를 사용하여 총 경비 및 비용 비중을 계산합니다.
        cost_info = self.scoring_service.calculate_total_cost(
            mcp_data.get('flight_quote'), 
            mcp_data.get('hotel_quote'),
            trip_duration_days, 
            parsed_data['party_size'], 
            'moderate', {} # 예산 등급 및 물가 정보 (향후 확장 가능)
        )
        cost_breakdown_chart = self.scoring_service.calculate_cost_breakdown(
            cost_info.get('costs_by_category', {})
        )

        # Step 4: POI 후보들의 1차 점수(사용자 선호도)를 계산합니다.
        scored_pois = self.scoring_service.score_poi_candidates(
            mcp_data.get('poi_list', []), user_style
        )
        
        # Step 5: Map Service를 사용하여 동선을 최적화하고 최종 일정을 배치합니다.
        is_domestic = parsed_data.get("is_domestic", False)
        final_schedule = self._arrange_schedule_optimized(
            scored_pois, trip_duration_days, is_domestic
        )
        
        # Step 6: 모든 데이터를 취합하여 최종 응답 JSON을 구성합니다.
        return {
            "trip_summary": f"{parsed_data['destination']}으로의 {trip_duration_days - 1}박 {trip_duration_days}일 맞춤 여행",
            "total_cost": cost_info.get('total_cost'),
            "cost_breakdown_chart": cost_breakdown_chart,
            "schedule": final_schedule,
            "raw_data": { # 디버깅 및 프론트엔드 추가 정보 활용용
                "llm_parsed_request": parsed_data,
                "mcp_fetched_data": mcp_data
            }
        }

    def _arrange_schedule_optimized(self, scored_pois: list[dict], trip_duration_days: int, is_domestic: bool) -> list[dict]:
        """점수가 높은 POI들을 기반으로 지리적으로 최적화된 일정을 생성합니다."""
        if not scored_pois:
            return []
        
        # POI 좌표 목록을 준비합니다.
        poi_coords = [{"lat": poi.get("lat", 0), "lng": poi.get("lng", 0)} for poi in scored_pois]
        
        try:
            # 지도 서비스에서 POI 간 이동 시간 매트릭스를 가져옵니다.
            distance_matrix = self.map_service.get_distance_matrix(poi_coords, poi_coords, is_domestic)
        except NotImplementedError:
             # 국내 다중 경로 미지원 시, 단순 목록 나열로 대체 (Graceful Degradation)
            distance_matrix = None
            print("Warning: Distance matrix for domestic travel is not implemented. Falling back to simple list.")

        # TODO: distance_matrix를 활용하여 실제 동선 최적화 로직(TSP 알고리즘 등) 구현 필요
        # 현재는 점수 순서대로 하루 4개씩 간단히 배치하는 임시 로직입니다.
        schedule = []
        pois_per_day = 4
        for day in range(trip_duration_days):
            daily_schedule = {"day": day + 1, "slots": []}
            start_index = day * pois_per_day
            day_pois = scored_pois[start_index : start_index + pois_per_day]
            
            if not day_pois: break

            slot_names = ["오전", "점심", "저녁", "야간"]
            for i, poi in enumerate(day_pois):
                daily_schedule["slots"].append({
                    "slot_name": slot_names[i],
                    "activity": poi['name'],
                    "poi_details": poi
                })
            schedule.append(daily_schedule)
            
        return schedule

