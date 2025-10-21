import asyncio
from datetime import date
import pprint
import sys
import os

# 테스트 스크립트가 mcp_server 모듈을 찾을 수 있도록 경로를 추가합니다.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 💡 import 대상을 FlightClient로 변경합니다.
from mcp_server.clients.flight_client import FlightClient, FlightClientError
from mcp_server.config import settings

async def main():
    """
    FlightClient를 직접 실행하여 Agoda 항공권 API 연동을 테스트합니다.
    """
    print("--- RapidAPI (Agoda Flights) 연동 테스트 시작 ---")

    if not settings.RAPID_API_KEY or not settings.BOOKING_RAPID_HOST:
        print("🔴 오류: .env 파일에서 API 키 또는 호스트 정보를 찾을 수 없습니다.")
        return

    flight_client = FlightClient()

    test_origin = "서울"
    test_destination = "도쿄"
    test_start_date = date(2025, 11, 5)
    test_end_date = date(2025, 11, 9)
    test_pax = 2

    print(f"\n🔍 검색 조건:")
    print(f"  - 출발지: {test_origin}")
    print(f"  - 도착지: {test_destination}")
    print(f"  - 가는날: {test_start_date}")
    print(f"  - 오는날: {test_end_date}")
    print(f"  - 인원: {test_pax}명")

    try:
        print("\n⏳ RapidAPI 서버에 항공권 정보를 요청합니다...")
        flight_result = await flight_client.search_flights(
            origin=test_origin,
            destination=test_destination,
            start_date=test_start_date,
            end_date=test_end_date,
            pax=test_pax,
        )
        
        print("\n--- 테스트 결과 ---")
        if flight_result:
            print("✅ 성공: Agoda API로부터 항공권 정보를 성공적으로 수신했습니다.")
            pprint.pprint(flight_result)
        else:
            print("🟡 정보: API 호출은 성공했으나, 조건에 맞는 항공권을 찾지 못했습니다.")

    except FlightClientError as e:
        print(f"🔴 API 클라이언트 오류: {e}")
    except Exception as e:
        print(f"🔴 예측하지 못한 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
