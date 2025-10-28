import asyncio
from datetime import date, timedelta
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가 (mcp 폴더의 상위 폴더)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 경로 추가 후 모듈 임포트
from mcp_server.clients.agoda_client import AgodaClient, AgodaClientError

async def run_hotel_test():
    """Agoda 호텔 API 클라이언트 테스트를 실행합니다."""
    print("--- RapidAPI (Agoda Hotels) 연동 테스트 시작 ---")

    # --- 검색 조건 ---
    destination = "도쿄" # 검색할 도시 이름
    start_date = date.today() + timedelta(days=90) # 오늘로부터 90일 후
    end_date = start_date + timedelta(days=3) # 3박
    pax = 2 # 성인 2명
    # ---------------

    print("\n🔍 검색 조건:")
    print(f"  - 목적지: {destination}")
    print(f"  - 체크인: {start_date}")
    print(f"  - 체크아웃: {end_date}")
    print(f"  - 인원: {pax}명")

    client = AgodaClient()

    print("\n⏳ RapidAPI 서버에 호텔 정보를 요청합니다...")

    try:
        hotel_result = await client.search_hotels(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            pax=pax
        )
        print("\n--- 테스트 결과 ---")
        if hotel_result:
            print("✅ 성공: Agoda API로부터 호텔 정보를 성공적으로 수신했습니다.")
            print(hotel_result)
        else:
            print("🟡 정보: API 호출은 성공했으나, 조건에 맞는 호텔을 찾지 못했습니다.")

    except AgodaClientError as e:
        print("\n--- 테스트 결과 ---")
        print(f"❌ 오류: Agoda API 호출 중 에러 발생: {e}")
    except Exception as e:
        print("\n--- 테스트 결과 ---")
        print(f"❌ 오류: 예상치 못한 에러 발생: {e}")

if __name__ == "__main__":
    # Python 3.7+ 에서는 asyncio.run() 사용 권장
    try:
        asyncio.run(run_hotel_test())
    except RuntimeError as e:
        # Jupyter Notebook 등 이미 이벤트 루프가 실행 중인 환경 처리
        if "cannot run nested event loops" in str(e):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_hotel_test())
        else:
            raise
