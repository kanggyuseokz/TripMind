import httpx
from ..config import settings

class PoiClientError(Exception):
    """POI API 클라이언트 관련 에러"""
    pass

class PoiClient:
    """Google/Kakao Maps API를 통해 POI(관심 장소) 정보를 가져오는 클라이언트"""
    
    def __init__(self):
        self.google_api_key = settings.GOOGLE_MAP_API_KEY
        self.kakao_api_key = settings.KAKAO_REST_API_KEY

    async def search_pois(self, destination: str, is_domestic: bool, category: str = "관광"):
        """주어진 목적지와 카테고리에 맞는 POI 목록을 검색합니다."""
        query = f"{destination} {category}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            if is_domestic:
                return await self._search_kakao(client, query)
            else:
                return await self._search_google(client, query)

    async def _search_google(self, client: httpx.AsyncClient, query: str) -> list[dict]:
        """Google Places API (Text Search)를 사용하여 POI를 검색합니다."""
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {"query": query, "key": self.google_api_key, "language": "ko"}
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            pois = []
            for place in result.get("results", [])[:10]: # 상위 10개 결과만 사용
                loc = place.get("geometry", {}).get("location", {})
                pois.append({
                    "name": place.get("name"),
                    "category": place.get("types", [])[0] if place.get("types") else "etc",
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
        params = {"query": query, "size": 10} # 상위 10개 결과
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()

            pois = []
            for place in result.get("documents", []):
                pois.append({
                    "name": place.get("place_name"),
                    "category": place.get("category_group_name"),
                    "rating": float(place.get("rating", 0)) if place.get("rating") else 0, # 카카오는 평점이 문자열일 수 있음
                    "lat": float(place.get("y")),
                    "lng": float(place.get("x"))
                })
            return pois
        except httpx.HTTPStatusError as e:
            raise PoiClientError(f"Kakao POI search failed: {e.response.text}")

