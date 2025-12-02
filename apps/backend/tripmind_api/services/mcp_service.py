# backend/tripmind_api/services/mcp_service.py
import httpx
from ..config import settings

class MCPService:
    """
    메인 백엔드 서버가 MCP 서버와 통신(Internal API Call)을 담당하는 서비스
    """
    def __init__(self):
        # 💡 .env의 MCP_BASE_URL을 사용 (사용자님 확인)
        if not settings.MCP_BASE_URL:
            raise ValueError("MCP_BASE_URL이 .env 파일에 설정되지 않았습니다.")
        
        self.base_url = f"{settings.MCP_BASE_URL}/plan/generate"
        # 💡 1. 비동기 클라이언트 대신 동기 클라이언트를 클래스 변수로 선언
        self.client = httpx.Client(timeout=60.0)

    # 💡 2. 'async def'를 다시 'def' (동기 함수)로 변경
    def fetch_all_data(self, parsed_data: dict, user_style: str) -> dict | None:
        """
        MCP 서버의 /plan/generate 엔드포인트를 동기로 호출하여
        항공, 호텔, POI, 날씨 데이터를 한 번에 가져옵니다.
        """
        payload = {
            "llm_parsed_data": parsed_data,
            "user_preferred_style": user_style
        }
        
        print("[MCPService] MCP 서버로 데이터 요청 시작...", payload) # 디버깅 로그

        try:
            # 💡 3. 'await' 제거, self.client.post (동기) 사용
            response = self.client.post(self.base_url, json=payload)
            
            response.raise_for_status() # 4xx, 5xx 에러 발생 시 예외 처리
            
            response_json = response.json()
            print("[MCPService] MCP 서버로부터 데이터 수신 성공.") # 디버깅 로그
             # ✅ 디버깅 추가
            print(f"[MCP] 📦 Full Response Keys: {list(response_json.keys())}")
            
            mcp_data = response_json.get("data")
            if mcp_data:
                print(f"[MCP] 📦 Data Keys: {list(mcp_data.keys())}")
                schedule = mcp_data.get('schedule', [])
                print(f"[MCP] 📅 Schedule exists: {schedule is not None}")
                print(f"[MCP] 📅 Schedule length: {len(schedule) if schedule else 0}")
                if schedule and len(schedule) > 0:
                    print(f"[MCP] 📅 First day: {schedule[0]}")
            else:
                print("[MCP] ⚠️ 'data' key not found in response!")

            # MCP 서버의 응답에서 'data' 키 내부의 실제 데이터를 반환
            return mcp_data

        except httpx.HTTPStatusError as e:
            # MCP 서버가 4xx, 5xx 응답을 반환한 경우
            print(f"[MCPService] MCP 서버 오류: {e.response.status_code} - {e.response.text}")
            raise # 오류를 상위 trip_service로 다시 전달
        except httpx.RequestError as e:
            # 네트워크 연결 실패 등 (MCP 서버가 꺼져있을 경우)
            print(f"[MCPService] MCP 서버 연결 실패: {e}")
            raise # 오류를 상위 trip_service로 다시 전달
        except Exception as e:
            print(f"[MCPService] 데이터 수신 중 알 수 없는 오류: {e}")
            raise # 오류를 상위 trip_service로 다시 전달

    # 💡 (참고) httpx.Client는 앱 종료 시 닫아주는 것이 좋으나,
    # Flask에서는 복잡하므로 일단 이대로 두어도 큰 문제는 없습니다.
    # def close(self):
    #     self.client.close()

