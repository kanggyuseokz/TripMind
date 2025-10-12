import httpx
from datetime import date
from ..config import settings

class FlightClient:
    """항공권 검색 API를 담당하는 클라이언트"""
    
    async def search_flights(self, origin: str, destination: str, start_date: date, end_date: date, pax: int):
        """
        주어진 조건으로 항공권을 검색합니다.
        TODO: 실제 항공권 검색 API (예: Skyscanner, Amadeus) 연동 로직 구현 필요
        """
        # 실제 API 연동 전, 테스트를 위한 Mock(가상) 데이터 반환
        print(f"Searching flights: {origin} -> {destination}")
        
        # 목적지에 따라 가격을 약간 다르게 설정
        base_price = 350000 if "도쿄" in destination or "오사카" in destination else 850000

        return [{
            "id": "FL_MOCK_001",
            "vendor": "MockAir",
            "route": f"{origin} - {destination}",
            "price_per_person": base_price,
            "price_total": base_price * pax,
            "currency": "KRW",
            "deeplink_url": "https://example.com/mock-flight-booking"
        }]
