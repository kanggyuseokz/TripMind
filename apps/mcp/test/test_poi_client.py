import asyncio
import pprint
import sys
import os

# 테스트 스크립트가 mcp_server 모듈을 찾을 수 있도록 경로를 추가합니다.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# POI 클라이언트를 임포트합니다.
from mcp_server.clients.poi_client import PoiClient, PoiClientError
from mcp_server.config import settings

async def run_test(poi_client: PoiClient, destination: str, is_domestic: bool, category: str):
    """개별 POI 검색 테스트를 실행하는 헬퍼 함수입니다."""
    print("-" * 50)
    print(f"🔍 검색 조건: 목적지='{destination}', 국내여부={is_domestic}, 카테고리='{category}'")
    
    try:
        print("⏳ API 서버에 POI 정보를 요청합니다...")
        poi_results = await poi_client.search_pois(
            destination=destination,
            is_domestic=is_domestic,
            category=category
        )
        
        if poi_results:
            print(f"✅ 성공: '{destination}'에 대한 POI 정보를 성공적으로 수신했습니다.")
            pprint.pprint(poi_results)
        else:
            print("🟡 정보: API 호출은 성공했으나, 조건에 맞는 POI를 찾지 못했습니다.")

    except PoiClientError as e:
        print(f"🔴 API 클라이언트 오류: {e}")
    except Exception as e:
        print(f"🔴 예측하지 못한 오류: {e}")
    print("-" * 50)


async def main():
    """
    PoiClient를 직접 실행하여 Google/Kakao Maps API 연동을 테스트합니다.
    """
    print("--- Google/Kakao POI API 연동 테스트 시작 ---")

    # .env 파일에서 API 키가 제대로 로드되었는지 확인
    if not settings.GOOGLE_MAP_API_KEY or not settings.KAKAO_REST_API_KEY:
        print("🔴 오류: .env 파일에서 GOOGLE_MAP_API_KEY 또는 KAKAO_REST_API_KEY를 찾을 수 없습니다.")
        return

    # 1. PoiClient 인스턴스 생성
    poi_client = PoiClient()

    # 2. 해외(Google) 및 국내(Kakao) 테스트 케이스 실행
    # 해외 테스트
    await run_test(poi_client, destination="도쿄", is_domestic=False, category="맛집")
    
    # 국내 테스트
    await run_test(poi_client, destination="강릉", is_domestic=True, category="카페")


if __name__ == "__main__":
    asyncio.run(main())