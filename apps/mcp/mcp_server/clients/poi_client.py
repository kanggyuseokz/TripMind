import httpx
import asyncio
from ..config import settings

class PoiClientError(Exception):
    """POI API 클라이언트 관련 에러"""
    pass

class PoiClient:
    """Google/Kakao Maps API를 통해 다양한 카테고리의 POI 목록을 가져오는 클라이언트"""
    
    def __init__(self):
        self.google_api_key = settings.GOOGLE_MAP_API_KEY
        self.kakao_api_key = settings.KAKAO_REST_API_KEY

    async def search_pois(self, destination: str, is_domestic: bool, category: str = "관광"):
        """
        주어진 목적지에 대해 '관광명소', '맛집', '카페' 등 필수 카테고리들을
        동시에 검색하여 통합된 POI 목록을 반환합니다.
        """
        # 💡 항상 검색할 핵심 카테고리 목록 정의
        core_categories = ["관광명소", "맛집", "카페"]
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            # 여러 카테고리 검색 작업을 비동기적으로 동시에 실행
            tasks = []
            for cat in core_categories:
                query = f"{destination} {cat}"
                if is_domestic:
                    tasks.append(self._search_kakao(client, query))
                else:
                    tasks.append(self._search_google(client, query))
            
            results_from_all_categories = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 모든 검색 결과를 하나의 리스트로 통합하고 중복 제거
            all_pois = []
            seen_names = set()
            for result in results_from_all_categories:
                if isinstance(result, list):
                    for poi in result:
                        if poi['name'] not in seen_names:
                            all_pois.append(poi)
                            seen_names.add(poi['name'])
            return all_pois

    async def _search_google(self, client: httpx.AsyncClient, query: str) -> list[dict]:
        """Google Places API (Text Search)를 사용하여 POI를 검색합니다."""
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {"query": query, "key": self.google_api_key, "language": "ko", "region": "KR"}
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            pois = []
            for place in result.get("results", [])[:7]: # 카테고리별 상위 7개 결과만 사용
                loc = place.get("geometry", {}).get("location", {})
                pois.append({
                    "name": place.get("name"),
                    # Google의 types를 더 일반적인 카테고리로 매핑 (단순화)
                    "category": "맛집" if "restaurant" in place.get("types", []) else "카페" if "cafe" in place.get("types", []) else "관광명소",
                    "rating": place.get("rating", 0),
                    "lat": loc.get("lat"),
                    "lng": loc.get("lng")
                })
            return pois
        except httpx.HTTPStatusError as e:
            raise PoiClientError(f"Google POI search failed: {e.response.text}")

    async def _search_kakao(self, client: httpx.AsyncClient, query: str) -> list[dict]:
        """Kakao 키워드 검색 API를 사용하여 POI를 검색합니다."""
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {self.kakao_api_key}"}
        params = {"query": query, "size": 7} # 카테고리별 상위 7개 결과
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()

            pois = []
            for place in result.get("documents", []):
                pois.append({
                    "name": place.get("place_name"),
                    "category": place.get("category_group_name"),
                    "rating": float(place.get("rating", 0)) if place.get("rating") else 0,
                    "lat": float(place.get("y")),
                    "lng": float(place.get("x"))
                })
            return pois
        except httpx.HTTPStatusError as e:
            raise PoiClientError(f"Kakao POI search failed: {e.response.text}")

