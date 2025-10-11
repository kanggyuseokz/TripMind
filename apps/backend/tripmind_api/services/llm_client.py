import json
from openai import OpenAI
from ..config import Config

# LLM 클라이언트 초기화 (모듈 로드 시 한 번만 실행)
# Config 클래스에서 Hugging Face Router 정보를 가져와 base_url과 api_key로 사용합니다.
client = OpenAI(
    base_url=Config.HF_BASE_URL,
    api_key=Config.HF_TOKEN
)

# MCP 서버의 기능을 LLM이 사용할 수 있도록 JSON 스키마 형태로 정의합니다.
# (이 정의는 llm_client.py에 두거나, tools/definitions.py 같은 별도 파일로 분리할 수 있습니다.)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_flight_and_hotel_quotes",
            "description": "실시간 항공편 및 숙소 견적 정보를 MCP 서버를 통해 검색합니다. 총 경비를 계산하는 데 필수적으로 사용해야 합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "출발 도시"},
                    "destination": {"type": "string", "description": "도착 도시"},
                    "startDate": {"type": "string", "description": "여행 시작 날짜 (YYYY-MM-DD)"},
                    "endDate": {"type": "string", "description": "여행 종료 날짜 (YYYY-MM-DD)"},
                    "pax": {"type": "integer", "description": "여행 인원 수"}
                },
                "required": ["origin", "destination", "startDate", "endDate", "pax"]
            }
        }
    }
    # 추가적인 MCP 도구 (예: get_poi_and_weather)는 여기에 추가됩니다.
]


def chat(messages: list, temperature: float = 0.2):
    """
    Hugging Face Router를 통해 LLM 추론을 요청하고 응답을 반환합니다.
    Tool Use (MCP 연동) 로직을 포함합니다.
    """
    # 토큰 유효성 검사 (실제 호출 전에 빠른 실패를 위함)
    if not Config.HF_TOKEN:
        return {"error": "(DRY-RUN) Hugging Face Token이 설정되지 않았습니다."}
    
    # 1. LLM 호출
    response = client.chat.completions.create(
        model=Config.HF_MODEL,
        messages=messages,
        temperature=temperature,
        tools=TOOL_DEFINITIONS  # LLM에 MCP 도구 사용 가능성을 알려줍니다.
    )
    
    # 2. 응답 처리 (Tool Call 또는 최종 텍스트)
    message = response.choices[0].message
    
    if message.tool_calls:
        # LLM이 MCP 서버 호출을 지시했습니다. 
        # 이 응답은 trip_service로 돌아가 MCP 호출을 처리하게 됩니다.
        return {"tool_calls": message.tool_calls}
    else:
        # 최종 텍스트 응답 또는 초기 파싱 결과
        return {"reply": message.content}