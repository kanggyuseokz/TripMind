# backend/tripmind_api/services/trip_service.py
from datetime import datetime, timedelta
import requests

from .mcp_service import MCPService
from .scoring_service import ScoringService
from .map_service import MapService

class TripService:
    """여행 계획 생성 프로세스를 총괄하는 최종 오케스트레이터."""
    
    def __init__(self):
        self.mcp_service = MCPService()
        self.scoring_service = ScoringService()
        self.map_service = MapService()

    def create_personalized_trip(self, request_data: dict, parsed_data: dict) -> dict:
        """LLM이 파싱한 데이터를 기반으로, 실제 여행 계획을 생성하는 메인 메소드입니다."""
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
            mcp_result = self.mcp_service.fetch_all_data(parsed_data, user_style)
            if not mcp_result:
                raise Exception("MCP service failed to fetch data.")

            # ✅ MCP가 'data' 키로 감싸서 반환하는 경우 처리
            if 'data' in mcp_result and isinstance(mcp_result['data'], dict):
                mcp_data = mcp_result['data']
                print("[TripService] ✅ MCP data unwrapped from 'data' key")
            else:
                mcp_data = mcp_result

            print(f"[TripService] 🔍 MCP Data Keys: {list(mcp_data.keys())}")
            print(f"[TripService] ✈️ flight_candidates: {len(mcp_data.get('flight_candidates', []))}")
            print(f"[TripService] 🏨 hotel_candidates: {len(mcp_data.get('hotel_candidates', []))}")

            # ✅ Schedule 디버깅 추가
            print(f"[TripService] 📅 schedule exists in mcp_data: {'schedule' in mcp_data}")
            raw_schedule = mcp_data.get('schedule', [])
            print(f"[TripService] 📅 raw schedule type: {type(raw_schedule)}")
            print(f"[TripService] 📅 raw schedule length: {len(raw_schedule) if raw_schedule else 0}")
            if raw_schedule and len(raw_schedule) > 0:
                print(f"[TripService] 📅 First schedule item: {raw_schedule[0]}")
            else:
                print(f"[TripService] ⚠️ Schedule is empty or None!")

            # Step 2: 여행 기간 계산
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            trip_duration_days = (end_date - start_date).days + 1
            trip_duration_nights = (end_date - start_date).days

            # Step 3: 비용 계산
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

            # Step 4: POI 점수 산정
            scored_pois = self.scoring_service.score_poi_candidates(
                mcp_data.get('poi_list', []), user_style
            )
            
            # Step 5: 일정 생성 (MCP에서 이미 enriched된 일정 사용)
            final_schedule = mcp_data.get('schedule', [])

            # ✅ Final schedule 디버깅
            print(f"[TripService] 📅 final_schedule length: {len(final_schedule)}")
            if final_schedule:
                print(f"[TripService] 📅 final_schedule sample: {final_schedule[0] if len(final_schedule) > 0 else 'empty'}")


            # 🎯 Step 6: 프론트엔드 구조에 맞춰 최종 결과 반환
            result = {
                "trip_summary": f"{destination} {trip_duration_nights}박 {trip_duration_days}일 여행",
                "destination": destination,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "pax": party_size,
                "party_size": party_size,
                "head_count": party_size,
                "total_cost": cost_info.get('total_cost'),
                "budget": cost_info.get('total_cost'),
                "cost_breakdown_chart": cost_breakdown_chart,
                "schedule": final_schedule,
                
                # 🎯 [핵심] raw_data 안에 mcp_fetched_data 구조로 전달
                "raw_data": {
                    "llm_parsed_request": parsed_data,
                    "mcp_fetched_data": {
                        "flight_candidates": mcp_data.get('flight_candidates', []),
                        "hotel_candidates": mcp_data.get('hotel_candidates', []),
                        "flight_quote": mcp_data.get('flight_quote'),
                        "hotel_quote": mcp_data.get('hotel_quote'),
                        "poi_list": mcp_data.get('poi_list', []),
                        "weather_info": mcp_data.get('weather_info', {}),
                        "schedule": final_schedule,
                        "cost_breakdown_chart": cost_breakdown_chart,
                        "travel_style": mcp_data.get('travel_style', 'sightseeing')
                    }
                }
            }
            
            print(f"[TripService] ✅ Final Result - Flights in raw_data: {len(result['raw_data']['mcp_fetched_data']['flight_candidates'])}")
            print(f"[TripService] ✅ Final Result - Hotels in raw_data: {len(result['raw_data']['mcp_fetched_data']['hotel_candidates'])}")
            print(f"[TripService] ✅ Final Result - Schedule in result: {len(result['schedule'])}")
            print(f"[TripService] ✅ Final Result - Schedule in raw_data: {len(result['raw_data']['mcp_fetched_data']['schedule'])}")
     
            return result
        
        except Exception as e:
            print(f"[TripService] ❌ Error in create_personalized_trip: {e}")
            raise e