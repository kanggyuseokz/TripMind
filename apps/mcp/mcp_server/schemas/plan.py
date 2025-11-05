# mcp/mcp_server/schemas/plan.py
from pydantic import BaseModel, Field
from typing import Any, List

# 💡 이 스키마는 mcp_service.py의 generate_trip_data 함수가 기대하는
# request_data["llm_parsed_data"]의 구조와 일치해야 합니다.

class LLMParsedData(BaseModel):
    """LLM이 파싱한 데이터 스키마"""
    destination: str
    start_date: str
    end_date: str
    origin: str
    party_size: int = 1
    is_domestic: bool = False
    budget_per_person: dict = Field(default_factory=dict)
    interests: List[str] = Field(default_factory=list)

class PlanRequest(BaseModel):
    """메인 백엔드로부터 받을 요청 Body 스키마"""
    llm_parsed_data: LLMParsedData
    user_preferred_style: str = "관광"

