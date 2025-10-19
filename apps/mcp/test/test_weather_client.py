import asyncio
import pprint
import sys
import os
from datetime import date, timedelta

# 테스트 스크립트가 mcp_server 모듈을 찾을 수 있도록 경로를 추가합니다.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Weather 클라이언트를 임포트합니다.
from mcp_server.clients.weather_client import WeatherClient, WeatherClientError
from mcp_server.config import settings

async def main():
    """
    WeatherClient를 직접 실행하여 OpenWeatherMap API 연동을 테스트합니다.
    """
    print("--- OpenWeatherMap API 연동 테스트 시작 ---")

    # .env 파일에서 API 키가 제대로 로드되었는지 확인
    if not settings.OWM_API_KEY:
        print("🔴 오류: .env 파일에서 OWM_API_KEY를 찾을 수 없습니다.")
        return

    # 1. WeatherClient 인스턴스 생성
    weather_client = WeatherClient()

    # 2. 테스트할 여행 정보 정의
    today = date.today()
    test_start_date = today + timedelta(days=1) # 내일
    test_end_date = today + timedelta(days=4)   # 4일 후
    test_destination = "파리"

    print(f"\n🔍 검색 조건: 목적지='{test_destination}', 기간='{test_start_date}~{test_end_date}'")

    # 3. get_weather_forecast 메소드 호출 및 결과 확인
    try:
        print("⏳ API 서버에 날씨 정보를 요청합니다...")
        weather_result = await weather_client.get_weather_forecast(
            destination=test_destination,
            start_date=test_start_date,
            end_date=test_end_date
        )
        
        print("\n--- 테스트 결과 ---")
        if weather_result:
            print(f"✅ 성공: '{test_destination}'의 날씨 정보를 성공적으로 수신했습니다.")
            pprint.pprint(weather_result)
        else:
            print("🟡 정보: API 호출은 성공했으나, 조건에 맞는 날씨 예보를 찾지 못했습니다.")

    except WeatherClientError as e:
        print(f"🔴 API 클라이언트 오류: {e}")
    except Exception as e:
        print(f"🔴 예측하지 못한 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
