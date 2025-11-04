# backend/tripmind_api/services/mcp_service.py
import httpx
import uuid
from typing import Dict, Any
from ..config import settings # 👈 메인 백엔드의 설정 파일

class MCPService:
    """
    메인 백엔드 서버에서 MCP 마이크로서비스로 API 요청을 보내는 클라이언트 서비스.
    """
    def __init__(self):
        # MCP 서버의 기본 URL을 설정 파일에서 가져옵니다.
        # (예: .env 파일에 MCP_SERVER_URL=http://localhost:8001 추가 필요)
        self.base_url = settings.MCP_SERVER_URL 
        # 비동기 HTTP 클라이언트를 생성합니다.
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    async def fetch_all_data(self, parsed_data: dict, user_style: str) -> Dict[str, Any]:
        """
        MCP 서버의 /plan/generate 엔드포인트를 호출하여 모든 외부 데이터를 가져옵니다.
        """
        # MCP 서버의 PlanRequest 스키마에 맞게 요청 바디를 구성합니다.
        request_body = {
            "request_id": str(uuid.uuid4()), # 고유한 요청 ID 생성
            "destination": parsed_data.get("destination"),
            "start_date": parsed_data.get("start_date"),
            "end_date": parsed_data.get("end_date"),
            "origin": parsed_data.get("origin"), # LLM 파싱 결과에 'origin'이 포함되어야 함
            "party_size": parsed_data.get("party_size"),
            "preferred_style": user_style
        }

        try:
            print(f"[MCPService] MCP 서버로 데이터 요청 시작: {request_body.get('destination')}")
            
            response = await self.client.post("/plan/generate", json=request_body)
            
            # MCP 서버가 4xx 또는 5xx 오류를 반환하면 예외 발생
            response.raise_for_status() 
            
            mcp_data = response.json()
            print(f"[MCPService] MCP 서버로부터 데이터 수신 성공.")
            
            # (예: {'poi_list': [...], 'weather_quote': {...}, 'flight_quote': {...}, 'hotel_quote': {...}, ...})
            return mcp_data

        except httpx.HTTPStatusError as e:
            # MCP 서버가 오류를 반환한 경우
            print(f"[MCPService] MCP 서버 오류: {e.response.status_code} - {e.response.text}")
            # 메인 TripService에 빈 데이터를 반환하여 부분적 처리를 시도하게 함
            return self._get_empty_mcp_data()
        except httpx.RequestError as e:
            # MCP 서버에 연결할 수 없는 경우 (네트워크 오류 등)
            print(f"[MCPService] MCP 서버 연결 오류: {e}")
            return self._get_empty_mcp_data()
        except Exception as e:
            print(f"[MCPService] 알 수 없는 오류 발생: {e}")
            return self._get_empty_mcp_data()

    def _get_empty_mcp_data(self) -> Dict[str, Any]:
        """MCP 호출 실패 시 반환할 기본 빈 데이터 구조"""
        return {
            "poi_list": [],
            "weather_quote": {},
            "flight_quote": {},
            "hotel_quote": {},
            "trip_duration_nights": 0,
            "request_id": None
        }

# 참고: 이 서비스는 비동기(async)로 작성되었으므로,
# 이 서비스를 호출하는 backend/trip_service.py의 create_personalized_trip 메소드도
# async def create_personalized_trip(...)으로 선언하고,
# mcp_data = await self.mcp_service.fetch_all_data(...) 로 호출