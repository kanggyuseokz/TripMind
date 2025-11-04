# backend/tripmind_api/services/trip_service.py
from datetime import datetime
import httpx

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
        # 각 서비스의 인스턴스를 생성합니다.
        self.mcp_service = MCPService()
        self.scoring_service = ScoringService()
        self.map_service = MapService()

    # 💡 1. 'def'를 'async def'로 변경
    async def create_personalized_trip(self, request_data: dict, parsed_data: dict) -> dict:
        """
        LLM이 파싱한 데이터를 기반으로, 실제 여행 계획을 생성하는 메인 메소드입니다.
        """
        try:
            # Step 1: MCP 서비스를 호출하여 모든 외부 데이터를 병렬로 수집합니다.
            user_style = request_data.get('preferred_style', '관광')
            # 💡 2. 'await' 추가
            mcp_data = await self.mcp_service.fetch_all_data(parsed_data, user_style)
            
            if not mcp_data:
                # MCP 서비스가 None을 반환한 경우 (예: MCP 서버 통신 실패)
                raise Exception("MCP service failed to fetch data.")

            # Step 2: 여행 기간(일)을 계산합니다.
            start_date_str = parsed_data['start_date']
            end_date_str = parsed_data['end_date']
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            trip_duration_days = (end_date - start_date).days + 1
            trip_duration_nights = (end_date - start_date).days # 💡 박 수 계산

            # Step 3: Scoring 서비스를 사용하여 총 경비 및 비용 비중을 계산합니다.
            cost_info = self.scoring_service.calculate_total_cost(
                mcp_data.get('flight_quote'), 
                mcp_data.get('hotel_quote'),
                trip_duration_nights,  # 💡 '일수' 대신 '박 수'를 전달 (비용 계산에 더 정확)
                parsed_data.get('party_size', 1),
                parsed_data['destination']
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
                "trip_summary": f"{parsed_data['destination']}으로의 {trip_duration_nights}박 {trip_duration_days}일 맞춤 여행",
                "total_cost": cost_info.get('total_cost'),
                "cost_breakdown_chart": cost_breakdown_chart,
                "schedule": final_schedule,
                "raw_data": { # 디버깅 및 프론트엔드 추가 정보 활용용
                    "llm_parsed_request": parsed_data,
                    "mcp_fetched_data": mcp_data
                }
            }
        
        except KeyError as e:
            # parsed_data에 필수 키(start_date, end_date 등)가 없는 경우
            print(f"KeyError during trip creation: {e}")
            raise Exception(f"Missing required data field: {e}")
        except httpx.HTTPStatusError as e:
            # mcp_service.fetch_all_data 내부에서 발생한 HTTP 오류
            print(f"HTTPError during MCP fetch: {e}")
            raise Exception(f"Failed to fetch data from microservice: {e.response.text}")
        except Exception as e:
            # 그 외 모든 예외
            print(f"Unexpected error in create_personalized_trip: {e}")
            raise e # 오류를 상위 라우터로 다시 전달

    def _arrange_schedule_optimized(self, scored_pois: list[dict], trip_duration_days: int, is_domestic: bool) -> list[dict]:
        """점수가 높은 POI들을 기반으로 지리적으로 최적화된 일정을 생성합니다."""
        # (기존 로직 유지)
        if not scored_pois:
            return []
        
        poi_coords = [{"lat": poi.get("lat", 0), "lng": poi.get("lng", 0)} for poi in scored_pois]
        
        try:
            distance_matrix = self.map_service.get_distance_matrix(poi_coords, poi_coords, is_domestic)
        except NotImplementedError:
             distance_matrix = None
             print("Warning: Distance matrix for domestic travel is not implemented. Falling back to simple list.")

        # TODO: distance_matrix를 활용한 실제 동선 최적화 로직 구현 필요
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

