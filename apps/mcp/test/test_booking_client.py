import asyncio
from datetime import date
import pprint  # 결과를 예쁘게 출력하기 위해 사용

# MCP 서버의 클라이언트와 설정을 가져옵니다.
from mcp_server.clients.booking_client import BookingClient, BookingClientError
from mcp_server.config import settings

async def main():
    """
    BookingClient를 직접 실행하여 RapidAPI 연동을 테스트하는 메인 함수입니다.
    """
    print("--- RapidAPI (Booking.com) 연동 테스트 시작 ---")

    # .env 파일에서 API 키가 제대로 로드되었는지 확인
    if not settings.RAPID_API_KEY or not settings.BOOKING_RAPID_HOST:
        print("🔴 오류: .env 파일에서 RAPID_API_KEY 또는 BOOKING_RAPID_HOST를 찾을 수 없습니다.")
        return

    # 1. BookingClient 인스턴스 생성
    booking_client = BookingClient()

    # 2. 테스트할 여행 정보 정의
    test_destination = "도쿄"
    test_start_date = date(2025, 11, 20)
    test_end_date = date(2025, 11, 23)
    test_pax = 2

    print(f"\n🔍 검색 조건:")
    print(f"  - 목적지: {test_destination}")
    print(f"  - 체크인: {test_start_date}")
    print(f"  - 체크아웃: {test_end_date}")
    print(f"  - 인원: {test_pax}명")

    # 3. search_hotels 메소드 호출 및 결과 확인
    try:
        print("\n⏳ RapidAPI 서버에 호텔 정보를 요청합니다...")
        hotel_result = await booking_client.search_hotels(
            destination=test_destination,
            start_date=test_start_date,
            end_date=test_end_date,
            pax=test_pax,
        )
        
        print("\n--- 테스트 결과 ---")
        if hotel_result:
            print("✅ 성공: Booking.com API로부터 호텔 정보를 성공적으로 수신했습니다.")
            pprint.pprint(hotel_result)
        else:
            print("🟡 정보: API 호출은 성공했으나, 조건에 맞는 호텔을 찾지 못했습니다.")

    except BookingClientError as e:
        print(f"🔴 API 클라이언트 오류: {e}")
    except Exception as e:
        print(f"🔴 예측하지 못한 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
