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

    # (Flask는 동기 방식이므로 'def' 유지)
    def create_personalized_trip(self, request_data: dict, parsed_data: dict) -> dict:
        """
        LLM이 파싱한 데이터를 기반으로, 실제 여행 계획을 생성하는 메인 메소드입니다.
        """
        try:
            # --- 💡 1. .get()을 사용하여 안전하게 값 추출 ---
            user_style = request_data.get('preferred_style', '관광')
            start_date_str = parsed_data.get('start_date')
            end_date_str = parsed_data.get('end_date')
            destination = parsed_data.get('destination')
            party_size = parsed_data.get('party_size', 1)
            is_domestic = parsed_data.get("is_domestic", False)
            
            # 💡 1-B. 필수 값이 없는 경우를 명시적으로 처리 (라우터에서 이미 검사했지만, 이중 방어)
            if not all([start_date_str, end_date_str, destination]):
                missing = [k for k, v in {"start_date": start_date_str, "end_date": end_date_str, "destination": destination}.items() if not v]
                raise KeyError(f"필수 필드 누락: {missing}")
            # -----------------------------------------------

            # Step 1: MCP 서비스를 호출하여 모든 외부 데이터를 병렬로 수집합니다.
            mcp_data = self.mcp_service.fetch_all_data(parsed_data, user_style)
            
            if not mcp_data:
                raise Exception("MCP service failed to fetch data.")

            # Step 2: 여행 기간(일)을 계산합니다.
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            trip_duration_days = (end_date - start_date).days + 1
            trip_duration_nights = (end_date - start_date).days # 박 수 계산

            # Step 3: Scoring 서비스를 사용하여 총 경비 및 비용 비중을 계산합니다.
            cost_info = self.scoring_service.calculate_total_cost(
                mcp_data.get('flight_quote'), 
                mcp_data.get('hotel_quote'),
                trip_duration_nights,
                party_size,
                destination,
                user_style
            )
            cost_breakdown_chart = self.scoring_service.calculate_cost_breakdown(
                cost_info.get('costs_by_category', {})
            )

            # Step 4: POI 후보들의 1차 점수(사용자 선호도)를 계산합니다.
            scored_pois = self.scoring_service.score_poi_candidates(
                mcp_data.get('poi_list', []), user_style
            )
            
            # Step 5: Map Service를 사용하여 동선을 최적화하고 최종 일정을 배치합니다.
            final_schedule = self._arrange_schedule_optimized(
                scored_pois, trip_duration_days, is_domestic
            )
            
            # Step 6: 모든 데이터를 취합하여 최종 응답 JSON을 구성합니다.
            return {
                "trip_summary": f"{destination}으로의 {trip_duration_nights}박 {trip_duration_days}일 맞춤 여행",
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
        if not scored_pois:
            return []
        
        # --- 💡 API 호출 제한을 위한 수정 ---
        # 1. 하루에 방문할 POI 개수를 정의합니다 (예: 4개)
        pois_per_day = 4
        # 2. 전체 일정에 필요한 POI 개수만큼만 상위 목록을 자릅니다.
        total_pois_needed = trip_duration_days * pois_per_day
        pois_for_schedule = scored_pois[:total_pois_needed]
        # ---------------------------------
        
        # 💡 3. 잘라낸 POI 목록(pois