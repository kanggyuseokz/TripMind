# mcp/mcp_server/routers/plan_router.py
from fastapi import APIRouter, Depends, HTTPException
from ..schemas.plan import PlanRequest  # 👈 mcp/mcp_server/schemas/plan.py 파일 임포트
from typing import Dict, Any

# 💡 1. 오류가 난 'trip_service' 대신 'mcp_service'를 임포트합니다.
from ..services.mcp_service import MCPService, mcp_service_instance 

router = APIRouter(
    prefix="/plan",
    tags=["Trip Planning"]
)

# 💡 2. 'mcp_service_instance'를 반환하는 의존성 주입 함수
def get_mcp_service():
    return mcp_service_instance

@router.post("/generate", response_model=Dict[str, Any])
async def generate_trip_plan_endpoint(
    # 💡 3. 요청 바디는 PlanRequest 스키마를 사용
    request_data: PlanRequest, 
    # 💡 4. 'MCPService'와 'get_mcp_service'를 사용
    mcp_service: MCPService = Depends(get_mcp_service)
):
    """
    메인 백엔드로부터 여행 계획 생성 요청을 받아 처리하는 API 엔드포인트입니다.
    
    모든 외부 API(POI, 날씨, 항공권, 호텔) 조회를 MCP 서버에서 수행하고
    취합된 데이터를 JSON 형태로 반환합니다.
    """
    try:
        # 💡 5. Pydantic 모델을 딕셔너리로 변환하여 서비스에 전달
        trip_plan_data = await mcp_service.generate_trip_data(request_data.dict()) 
        
        if trip_plan_data.get("error"):
             raise HTTPException(status_code=400, detail=f"MCP Service Error: {trip_plan_data['error']}")

        return {"status": "success", "data": trip_plan_data}
        
    except Exception as e:
        print(f"[MCP] /generate 엔드포인트에서 심각한 오류 발생: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"MCP 서버에서 계획 생성 중 오류 발생: {str(e)}"
        )