from __future__ import annotations
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..config import settings

class MapServiceError(Exception):
    """지도 서비스 관련 에러"""
    pass

class MapService:
    """
    Google Maps와 Kakao Map API를 사용하여 위치 정보를 처리하는 서비스.
    - is_domestic 플래그에 따라 국내(Kakao)/해외(Google) API를 선택
    - POI 좌표 검색 (Geocoding)
    - POI 간 이동 시간 매트릭스 계산
    """

    def __init__(self, timeout: int = 10, retries: int = 3):
        self.google_api_key = settings.GOOGLE_MAP_API_KEY
        self.kakao_api_key = settings.KAKAO_REST_API_KEY
        
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.timeout = timeout

    def get_coordinates_for_poi(self, poi_name: str, destination_city: str, is_domestic: bool) -> dict[str, float]:
        """
        POI 이름과 is_domestic 플래그를 기반으로 위도, 경도 좌표를 반환합니다.
        """
        full_poi_name = f"{destination_city} {poi_name}" if destination_city not in poi_name else poi_name

        if is_domestic:
            return self._get_coords_from_kakao(full_poi_name)
        return self._get_coords_from_google(full_poi_name)

    def _get_coords_from_google(self, address: str) -> dict[str, float]:
        """Google Geocoding API를 사용하여 좌표를 가져옵니다."""
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": self.google_api_key, "language": "ko"}
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if data["status"] == "OK":
                location = data["results"][0]["geometry"]["location"]
                return {"lat": location["lat"], "lng": location["lng"]}
            else:
                # --- 💡 개선점 ---
                # Google이 제공하는 상세 에러 메시지를 포함하여 디버깅을 용이하게 합니다.
                error_message = data.get('error_message', data['status'])
                raise MapServiceError(f"Google Geocoding failed for '{address}': {error_message}")
        except (requests.RequestException, IndexError, KeyError) as e:
            raise MapServiceError(f"Failed to get coordinates from Google for '{address}': {e}")

    def _get_coords_from_kakao(self, query: str) -> dict[str, float]:
        """Kakao 키워드 검색 API를 사용하여 좌표를 가져옵니다."""
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {self.kakao_api_key}"}
        params = {"query": query}

        try:
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if data.get("documents"):
                location = data["documents"][0]
                return {"lat": float(location["y"]), "lng": float(location["x"])}
            else:
                # --- 💡 개선점 ---
                # API는 성공했으나 결과가 없는 경우를 명확히 알려줍니다.
                raise MapServiceError(f"Kakao search for '{query}' returned no results. (API call was successful)")
        except requests.RequestException as e:
            error_details = e.response.text if e.response else str(e)
            raise MapServiceError(f"Failed to get coordinates from Kakao for '{query}': {error_details}")
        except (IndexError, KeyError) as e:
            raise MapServiceError(f"Failed to parse Kakao API response for '{query}': {e}")

    def get_distance_matrix(self, origins: list[dict[str, float]], destinations: list[dict[str, float]], is_domestic: bool) -> list[list[int]]:
        """
        여러 출발지와 목적지 간의 이동 시간(초) 매트릭스를 계산합니다.
        """
        if not origins or not destinations:
            return []
        
        if is_domestic:
             raise NotImplementedError("Kakao API를 사용한 국내 다중 경로 계산은 아직 구현되지 않았습니다.")

        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        origin_str = "|".join([f"{o['lat']},{o['lng']}" for o in origins])
        dest_str = "|".join([f"{d['lat']},{d['lng']}" for d in destinations])
        
        params = {
            "origins": origin_str,
            "destinations": dest_str,
            "key": self.google_api_key,
            "mode": "transit",
            "language": "ko",
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data["status"] != "OK":
                # --- 💡 개선점 ---
                # 상세 에러 메시지를 포함합니다.
                error_message = data.get('error_message', data['status'])
                raise MapServiceError(f"Google Distance Matrix failed: {error_message}")

            matrix = []
            for row in data["rows"]:
                row_durations = [
                    element["duration"]["value"] if element["status"] == "OK" else -1
                    for element in row["elements"]
                ]
                matrix.append(row_durations)
            return matrix
        except (requests.RequestException, KeyError) as e:
            raise MapServiceError(f"Failed to get distance matrix from Google: {e}")

