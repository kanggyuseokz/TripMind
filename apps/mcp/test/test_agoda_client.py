import asyncio
from datetime import date
import pprint
import sys
import os

# 테스트 스크립트가 mcp_server 모듈을 찾을 수 있도록 상위 디렉토리(mcp/)를 Python 경로에 추가합니다.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 💡 import 대상을 AgodaClient로 변경합니다.
from mcp_server.clients.agoda_client import AgodaClient, AgodaClientError
from mcp_server.config import settings

async def main():
    """
    AgodaClient를 직접 실행하여 RapidAPI 연동을 테스트하는 메인 함수입니다.
    """
    print("--- RapidAPI (Agoda) 연동 테스트 시작 ---")

    # .env 파일에서 API 키가 제대로 로드되었는지 확인
    if not settings.RAPID_API_KEY or not settings.BOOKING_RAPID_HOST:
        print("🔴 오류: .env 파일에서 RAPID_API_KEY 또는 BOOKING_RAPID_HOST를 찾을 수 없습니다.")
        return

    # 1. AgodaClient 인스턴스 생성
    agoda_client = AgodaClient()

    # 2. 테스트할 여행 정보 정의
    test_destination = "도쿄"
    test_start_date = date(2025, 12, 10)
    test_end_date = date(2025, 12, 13)
    test_pax = 2

    print(f"\n🔍 검색 조건:")
    print(f"  - 목적지: {test_destination}")
    print(f"  - 체크인: {test_start_date}")
    print(f"  - 체크아웃: {test_end_date}")
    print(f"  - 인원: {test_pax}명")

    # 3. search_hotels 메소드 호출 및 결과 확인
    try:
        print("\n⏳ RapidAPI 서버에 호텔 정보를 요청합니다...")
        hotel_result = await agoda_client.search_hotels(
            destination=test_destination,
            start_date=test_start_date,
            end_date=test_end_date,
            pax=test_pax,
        )
        
        print("\n--- 테스트 결과 ---")
        if hotel_result:
            print("✅ 성공: Agoda API로부터 호텔 정보를 성공적으로 수신했습니다.")
            pprint.pprint(hotel_result)
        else:
            print("🟡 정보: API 호출은 성공했으나, 조건에 맞는 호텔을 찾지 못했습니다.")

    except AgodaClientError as e:
        print(f"🔴 API 클라이언트 오류: {e}")
    except Exception as e:
        print(f"🔴 예측하지 못한 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
