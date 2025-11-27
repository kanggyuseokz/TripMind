import httpx
from ..config import settings

class MCPService:
    """
    메인 백엔드 서버가 MCP 서버와 통신(Internal API Call)을 담당하는 서비스
    """
    def __init__(self):
        # .env의 MCP_BASE_URL 확인
        if not settings.MCP_BASE_URL:
            raise ValueError("MCP_BASE_URL이 .env 파일에 설정되지 않았습니다.")
        
        self.base_url = f"{settings.MCP_BASE_URL}/plan/generate"
        
        # [Good] 동기 클라이언트 재사용 (Connection Pooling)
        self.client = httpx.Client(timeout=60.0)

    def fetch_all_data(self, parsed_data: dict, user_style: list) -> dict | None:
        """
        MCP 서버의 /plan/generate 엔드포인트를 동기로 호출합니다.
        """
        payload = {
            "llm_parsed_data": parsed_data,
            "user_preferred_style": user_style
        }
        
        print(f"[MCPService] Requesting to {self.base_url}...") 

        try:
            # 동기 요청 (Blocking)
            response = self.client.post(self.base_url, json=payload)
            response.raise_for_status()
            
            response_json = response.json()
            print("[MCPService] Data received successfully.")
            
            # 🚀 [수정됨] .get("data") 제거!
            # MCP 서버가 {"destination": "...", "poi_list": [...]} 형태의 딕셔너리를 
            # 바로 반환하므로, response_json 자체가 데이터입니다.
            # 만약 response_json.get("data")를 쓰면 결과가 None이 되어버립니다.
            return response_json 

        except httpx.HTTPStatusError as e:
            print(f"[MCPService] HTTP Error: {e.response.status_code} - {e.response.text}")
            raise 
        except httpx.RequestError as e:
            print(f"[MCPService] Connection Error: {e}")
            raise 
        except Exception as e:
            print(f"[MCPService] Unexpected Error: {e}")
            raise