import httpx
from ..config import settings

class PoiClient:
    """Google/Kakao Maps API를 통해 POI(관심 장소) 정보를 가져오는 클라이언트"""
    
    async def search_pois(self, destination: str, is_domestic: bool, category: str = "관광"):
        """
        주어진 목적지와 카테고리에 맞는 POI 목록을 검색합니다.
        TODO: 실제 Google/Kakao Places API 연동 로직 구현 필요
        """
        # 실제 API 연동 전, 테스트를 위한 Mock(가상) 데이터 반환
        print(f"Searching POIs for: {destination} (Domestic: {is_domestic})")
        
        if is_domestic:
            return [
                {"name": "경포해변", "category": "landmark", "rating": 4.6, "lat": 37.8034, "lng": 128.9186},
                {"name": "안목해변 카페거리", "category": "food", "rating": 4.5, "lat": 37.7831, "lng": 128.9465},
                {"name": "오죽헌", "category": "history", "rating": 4.4, "lat": 37.7825, "lng": 128.8783}
            ]
        else: # 해외 (도쿄/오사카 예시)
            return [
                {"name": "도쿄 타워", "category": "landmark", "rating": 4.5, "lat": 35.6586, "lng": 139.7454},
                {"name": "시부야 스크램블 교차로", "category": "landmark", "rating": 4.4, "lat": 35.6595, "lng": 139.7005},
                {"name": "츠키지 시장", "category": "food", "rating": 4.3, "lat": 35.6655, "lng": 139.7708},
                {"name": "신주쿠 교엔", "category": "park", "rating": 4.6, "lat": 35.6852, "lng": 139.7100}
            ]
