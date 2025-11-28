# 테스트 코드 (apps/mcp/test_agoda.py 같은 파일 만들어서)
import asyncio
from datetime import date, timedelta
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_server.clients.agoda_client import AgodaClient

async def test():
    client = AgodaClient()
    
    # 1. API 연결 테스트 먼저!
    print("\n🧪 Step 1: API 연결 테스트")
    await client._test_api_connection()
    
    # 2. 실제 항공편 검색
    print("\n✈️ Step 2: 항공편 검색 테스트")
    start_date = date.today() + timedelta(days=30)
    end_date = start_date + timedelta(days=4)
    
    flights = await client.search_flights(
        origin="서울",
        destination="도쿄",
        start_date=start_date,
        end_date=end_date,
        pax=1
    )
    print(f"\n결과: {len(flights)}개 항공편 발견")
    
    # 3. 호텔 검색
    print("\n🏨 Step 3: 호텔 검색 테스트")
    hotels = await client.search_hotels(
        destination="도쿄",
        start_date=start_date,
        end_date=end_date,
        pax=2
    )
    print(f"\n결과: {len(hotels)}개 호텔 발견")

if __name__ == "__main__":
    asyncio.run(test())