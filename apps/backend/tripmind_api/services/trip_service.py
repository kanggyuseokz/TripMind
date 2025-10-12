# tripmind_api/services/trip_service.py
import json
from datetime import datetime

# 리팩토링: _client -> _service로 변경하고, 각 서비스 클래스를 임포트합니다.
from .llm_service import LLMService
from .mcp_service import MCPService
from .scoring_service import ScoringService
from .map_service import MapService

class TripService:
    """
    여행 계획 생성 프로세스를 총괄하는 최종 오케스트레이터.
    LLM(파싱) -> MCP(데이터 수집) -> Scoring/Map(분석/최적화) -> 최종 결과 생성
    """
    def __init__(self):
        # 리팩토링: 서비스 클래스의 인스턴스를 생성합니다.
        self.llm_service = LLMService()
        self.mcp_service = MCPService()
        self.scoring_service = ScoringService()
        self.map_service = MapService()

    def _arrange_schedule_optimized(self, scored_pois, trip_duration_days, is_domestic):
        if not scored_pois:
            return []
        
        # MapService의 get_distance_matrix를 호출하기 위해 POI 좌표 목록을 준비합니다.
        poi_coords = [{"lat": poi.get("lat", 0), "lng": poi.get("lng", 0)} for poi in scored_pois]
        distance_matrix = self.map_service.get_distance_matrix(poi_coords, poi_coords, is_domestic)
        
        schedule, remaining_pois, slots_per_day = [], list(scored_pois), 4

        for day in range(1, trip_duration_days + 1):
            if not remaining_pois: break
            daily_schedule = {"day": day, "slots": []}
            
            current_poi = remaining_pois.pop(0)
            daily_schedule["slots"].append({"slot_name": "오전", "activity": current_poi['name'], "poi_details": current_poi})

            for i in range(1, slots_per_day):
                if not remaining_pois: break
                # _find_nearest_poi에 poi_coords 대신 scored_pois를 전달해야 합니다.
                next_poi = self._find_nearest_poi(current_poi, remaining_pois, distance_matrix)
                if not next_poi: break
                
                daily_schedule["slots"].append({"slot_name": ["점심", "저녁", "야간"][i-1], "activity": next_poi['name'], "poi_details": next_poi})
                current_poi = next_poi
                remaining_pois.remove(next_poi)
            schedule.append(daily_schedule)
        return schedule

    def _find_nearest_poi(self, start_poi, candidate_pois, distance_matrix):
        # A more robust implementation is needed here, as distance_matrix indexing can be complex.
        # This is a simplified version assuming the matrix is well-formed.
        # For now, this logic might be brittle and should be improved with proper indexing.
        min_duration, nearest_poi = float('inf'), None
        # This fallback is a simple placeholder for more robust logic.
        return candidate_pois[0] if candidate_pois else None

    def create_personalized_trip(self, user_request_raw: dict):
        # Step 1: LLMService를 사용하여 사용자의 자연어 요청을 구조화된 JSON으로 파싱
        user_query = user_request_raw.get('text', '') # 'prompt' 대신 'text' 사용
        parsed_request = self.llm_service.parse_query(user_query)
        if "error" in parsed_request:
            return parsed_request # LLM 파싱 실패 시 에러 반환

        # Step 2: 파싱된 요청을 MCP 서비스에 전달하여 모든 외부 데이터를 병렬로 수집
        # mcp_data = self.mcp_service.fetch_all_data_concurrently(parsed_request)
        # TODO: MCPService가 아직 Mock이므로, 임시 데이터로 대체합니다.
        mcp_data = {
            "flight_quote": {"price": 350000},
            "hotel_quote": {"priceTotal": 400000},
            "poi_list": [
                {"name": "도톤보리", "category": "landmark", "rating": 4.5, "lat": 34.6687, "lng": 135.5010},
                {"name": "오사카성", "category": "landmark", "rating": 4.6, "lat": 34.6873, "lng": 135.5262},
                {"name": "유니버설 스튜디오 재팬", "category": "entertainment", "rating": 4.7, "lat": 34.6654, "lng": 135.4323}
            ]
        }
        
        # Step 3: Scoring 서비스를 사용하여 총 경비 및 비용 비중 계산
        start_date = datetime.strptime(parsed_request['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(parsed_request['end_date'], '%Y-%m-%d')
        trip_duration = (end_date - start_date).days

        cost_info = self.scoring_service.calculate_total_cost(
            mcp_data['flight_quote'], mcp_data['hotel_quote'],
            trip_duration, parsed_request['party_size'], 'moderate', {}
        )
        cost_breakdown_chart_data = self.scoring_service.calculate_cost_breakdown(
            cost_info['costs_by_category']
        )

        # Step 4: Scoring 서비스를 사용하여 POI 후보들의 1차 점수(선호도) 계산
        user_style = user_request_raw.get('preferred_style', '관광')
        scored_pois = self.scoring_service.score_poi_candidates(
            mcp_data['poi_list'], user_style
        )
        
        # Step 5: Map Service를 사용하여 동선을 최적화하고 최종 일정을 배치
        is_domestic = parsed_request.get("is_domestic", False)
        final_schedule = self._arrange_schedule_optimized(
            scored_pois, trip_duration, is_domestic
        )
        
        # Step 6: 모든 데이터를 취합하여 최종 응답 JSON을 구성
        return {
            "trip_summary": f"{parsed_request['destination']}으로의 {trip_duration-1}박 {trip_duration}일 맞춤 여행 계획입니다.",
            "total_cost": cost_info['total_cost'],
            "cost_breakdown_chart": cost_breakdown_chart_data,
            "schedule": final_schedule,
            "raw_data": { # 디버깅용
                "llm_parsed_request": parsed_request,
                "mcp_fetched_data": mcp_data
            }
        }

