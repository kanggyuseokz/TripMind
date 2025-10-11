import requests
import json
from ..config import Config

MCP_BASE_URL = Config.MCP_BASE_URL

def get_flight_and_hotel_quotes(origin: str, destination: str, startDate: str, endDate: str, pax: int) -> dict:
    """
    MCP 서버의 /quotes 엔드포인트를 호출하여 항공 및 숙소 견적을 가져옵니다.
    
    이 함수는 LLM의 Tool Use 지시에 따라 실행되며, MCP 서버 응답을 반환합니다.
    """
    url = f"{MCP_BASE_URL}/quotes"
    payload = {
        "origin": origin,
        "destination": destination,
        "startDate": startDate,
        "endDate": endDate,
        "pax": pax
    }
    
    try:
        # MCP 서버로 JSON 요청을 보냅니다.
        response = requests.post(url, json=payload, timeout=10) 
        response.raise_for_status() # HTTP 오류가 발생하면 예외 발생
        
        # MCP 서버에서 받은 JSON 응답을 그대로 반환합니다.
        return response.json()
        
    except requests.exceptions.RequestException as e:
        # 통신 오류 발생 시 LLM에게 전달할 수 있도록 오류 객체를 반환합니다.
        return {"error": f"MCP server error during quotes retrieval: {e}"}
