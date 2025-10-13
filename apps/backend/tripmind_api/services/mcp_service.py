import requests
from ..config import settings

class MCPServiceError(Exception):
    """MCP 서비스 통신 관련 에러"""
    pass

class MCPService:
    """
    백엔드(Flask)가 MCP 서버(FastAPI)와 통신할 수 있도록 돕는 서비스입니다.
    """
    def __init__(self):
        self.base_url = settings.MCP_BASE_URL
        self.session = requests.Session()

    def fetch_all_data(self, parsed_llm_data: dict) -> dict:
        """
        LLM이 파싱한 데이터를 MCP 서버의 /gather-all 엔드포인트로 보내고,
        수집된 모든 외부 데이터(항공, 숙소, POI 등)를 받아옵니다.
        """
        mcp_endpoint = f"{self.base_url}/gather-all"
        
        try:
            # MCP 서버가 요구하는 데이터 형식에 맞춰 payload를 재구성합니다.
            # 예: start_date, end_date를 date 객체가 아닌 문자열로 전달
            payload = {
                "origin": parsed_llm_data.get("origin"),
                "destination": parsed_llm_data.get("destination"),
                "is_domestic": parsed_llm_data.get("is_domestic"),
                "start_date": parsed_llm_data.get("start_date"),
                "end_date": parsed_llm_data.get("end_date"),
                "party_size": parsed_llm_data.get("party_size"),
                # 'preferred_style'은 trip_route.py에서 받은 원본 요청에서 가져와야 할 수 있습니다.
                # 여기서는 예시로 '관광'을 사용합니다.
                "preferred_style": "관광"
            }
            
            response = self.session.post(mcp_endpoint, json=payload, timeout=60)
            response.raise_for_status() # 200번대 응답이 아니면 에러 발생
            return response.json()

        except requests.RequestException as e:
            raise MCPServiceError(f"Failed to fetch data from MCP server: {e}")
        except Exception as e:
            raise MCPServiceError(f"An unexpected error occurred during MCP communication: {e}")

