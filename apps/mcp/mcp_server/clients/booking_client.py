import httpx
from ..config import settings

class BookingClient:
    """RapidAPI를 통해 Booking.com 데이터를 가져오는 클라이언트"""
    
    async def search_hotels(self, destination: str, start_date: str, end_date: str, pax: int):
        # TODO: Booking.com API 명세에 맞춰 도시 ID를 찾는 로직,
        #       체크인/체크아웃 날짜 포맷팅 등 실제 호출 로직을 구현해야 합니다.
        
        # 아래는 실제 API가 연동되었다고 가정한 예시 Mock 데이터입니다.
        return [{
            "id": "H1_REAL",
            "name": f"{destination} Grand Hotel",
            "nights": (end_date - start_date).days,
            "pricePerNight": 150000,
            "priceTotal": 450000,
            "currency": "KRW",
        }]

# 항공권 API도 유사한 방식으로 client 파일을 만들 수 있습니다.
