# mcp/mcp_server/clients/poi_client.py (수정 버전)
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
            for place in result.get("results", [])[:15]: # 카테고리별 상위 15개
                loc = place.get("geometry", {}).get("location", {})
                place_name = place.get("name", "")
                place_rating = place.get("rating", 0)
                place_types = place.get("types", [])
                
                # 카테고리 결정
                if "restaurant" in place_types or "food" in place_types:
                    category = "맛집"
                elif "cafe" in place_types:
                    category = "카페"
                else:
                    category = "관광명소"
                
                # ✅ 상세 설명 생성
                description = place_name
                if place_rating > 0:
                    description += f" - {category}"
                    if category == "맛집":
                        description += ", 현지 맛집"
                    elif category == "카페":
                        description += ", 분위기 좋은 카페"
                    else:
                        description += ", 인기 관광지"
                    description += f" (Rating: {place_rating})"
                
                pois.append({
                    "name": place_name,
                    "category": category,
                    "rating": place_rating,  # ✅ Google에서 가져온 실제 rating
                    "description": description,  # ✅ 상세 설명 추가
                    "vicinity": place.get("vicinity", ""),  # ✅ 위치 정보 추가
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
        params = {"query": query, "size": 15} # 카테고리별 상위 15개
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()

            pois = []
            for place in result.get("documents", []):
                place_name = place.get("place_name", "")
                place_rating = float(place.get("rating", 0)) if place.get("rating") else 0
                category = place.get("category_group_name", "관광명소")
                
                # ✅ 상세 설명 생성 (Kakao도 동일하게)
                description = place_name
                if place_rating > 0:
                    description += f" - {category}"
                    if "음식점" in category:
                        description += ", 현지 맛집"
                    elif "카페" in category:
                        description += ", 분위기 좋은 카페"
                    else:
                        description += ", 인기 장소"
                    description += f" (Rating: {place_rating})"
                
                pois.append({
                    "name": place_name,
                    "category": category,
                    "rating": place_rating,  # ✅ 실제 rating
                    "description": description,  # ✅ 상세 설명 추가
                    "vicinity": place.get("address_name", ""),  # ✅ 주소 정보
                    "lat": float(place.get("y")),
                    "lng": float(place.get("x"))
                })
            return pois
        except httpx.HTTPStatusError as e:
            raise PoiClientError(f"Kakao POI search failed: {e.response.text}")