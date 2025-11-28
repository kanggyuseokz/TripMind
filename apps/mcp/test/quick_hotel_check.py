"""
호텔 API 응답 전체 구조 확인
"""
import asyncio
import httpx
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_server.config import settings

async def check_hotel_response():
    headers = {
        "X-RapidAPI-Key": settings.RAPID_API_KEY,
        "X-RapidAPI-Host": "agoda-com.p.rapidapi.com"
    }
    
    params = {
        "id": "1_5085",
        "checkinDate": "2025-12-28",
        "checkoutDate": "2026-01-01",
        "adult": "2",
        "currency": "KRW",
        "language": "en-us",
        "sort": "Ranking,Desc",
        "limit": 20,
        "page": 1
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            "https://agoda-com.p.rapidapi.com/hotels/search-overnight",
            headers=headers,
            params=params
        )
        
        print(f"Status: {response.status_code}\n")
        
        data = response.json()
        
        # 1. 전체 키 구조 확인
        print("="*80)
        print("TOP LEVEL KEYS:")
        print("="*80)
        print(list(data.keys()))
        print()
        
        # 2. data 안의 구조
        if "data" in data:
            print("="*80)
            print("data KEYS:")
            print("="*80)
            print(list(data["data"].keys()))
            print()
            
            # 3. citySearch 안의 구조
            if "citySearch" in data["data"]:
                print("="*80)
                print("citySearch KEYS:")
                print("="*80)
                print(list(data["data"]["citySearch"].keys()))
                print()
                
                # 4. searchResult 안의 구조
                if "searchResult" in data["data"]["citySearch"]:
                    search_result = data["data"]["citySearch"]["searchResult"]
                    print("="*80)
                    print("searchResult KEYS:")
                    print("="*80)
                    print(list(search_result.keys()))
                    print()
                    
                    # 5. 각 키의 타입 확인
                    print("="*80)
                    print("searchResult KEYS & TYPES:")
                    print("="*80)
                    for key in search_result.keys():
                        value = search_result[key]
                        value_type = type(value).__name__
                        
                        if isinstance(value, list):
                            print(f"  {key}: {value_type} (length: {len(value)})")
                            if len(value) > 0:
                                print(f"    → First item type: {type(value[0]).__name__}")
                        elif isinstance(value, dict):
                            print(f"  {key}: {value_type} (keys: {list(value.keys())[:5]})")
                        else:
                            print(f"  {key}: {value_type}")
                    print()
                    
                    # 6. 호텔 데이터 찾기
                    print("="*80)
                    print("LOOKING FOR HOTEL DATA:")
                    print("="*80)
                    
                    # 가능한 모든 필드 확인
                    possible_fields = [
                        'hotels', 'hotelList', 'result', 'results', 
                        'properties', 'listings', 'items', 'data'
                    ]
                    
                    for field in possible_fields:
                        if field in search_result:
                            value = search_result[field]
                            if isinstance(value, list):
                                print(f"✅ FOUND: '{field}' is a list with {len(value)} items")
                                if len(value) > 0:
                                    print(f"   First item keys: {list(value[0].keys())[:10]}")
                                    print(f"   First item preview:")
                                    print(json.dumps(value[0], indent=4, ensure_ascii=False)[:500])
                            else:
                                print(f"⚠️ FOUND: '{field}' but it's {type(value).__name__}")
                    
                    # 7. 전체 응답 저장 (파일로)
                    print("\n" + "="*80)
                    print("SAVING FULL RESPONSE TO FILE:")
                    print("="*80)
                    
                    with open("hotel_response_full.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    print("✅ Saved to: hotel_response_full.json")
                    print("   → Open this file to see the complete structure")

if __name__ == "__main__":
    asyncio.run(check_hotel_response())