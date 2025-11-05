# mcp/mcp_server/routers/plan_router.py

from fastapi import APIRouter, Depends, HTTPException
from ..schemas.plan import PlanRequest
from ..services.trip_service import TripService, get_trip_service
from typing import Dict, Any

router = APIRouter(
    prefix="/plan",
    tags=["Trip Planning"]
)

@router.post("/generate", response_model=Dict[str, Any])
async def generate_trip_plan_endpoint(
    request: PlanRequest,
    trip_service: TripService = Depends(get_trip_service)
):
    """
    메인 백엔드로부터 여행 계획 생성 요청을 받아 처리하는 API 엔드포인트입니다.
    
    모든 외부 API(POI, 날씨, 항공권, 호텔) 조회를 MCP 서버에서 수행하고
    취합된 데이터를 JSON 형태로 반환합니다.
    """
    try:
        # 서비스 레이어에 실제 로직 위임
        trip_plan_data = await trip_service.generate_trip_plan(request)
        
        # 부분적 실패 처리 (예: 항공권은 찾았으나 호텔은 못 찾음)
        # 클라이언트 단에서 빈 dict( {} )를 반환하므로,
        # 이 자체를 오류로 처리하지 않고 그대로 반환합니다.
        # 메인 백엔드가 flight_quote가 비어있는지 확인하고 처리합니다.
        
        return trip_plan_data
        
    except Exception as e:
        # (예: AgodaClientError 등)
        # 서비스 로직 실행 중 발생한 예외 처리
        print(f"[{request.request_id}] MCP: /generate 엔드포인트에서 심각한 오류 발생: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"MCP 서버에서 계획 생성 중 오류 발생: {str(e)}"
        )
