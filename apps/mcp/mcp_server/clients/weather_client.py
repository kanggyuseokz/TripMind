import httpx
from datetime import date
from statistics import mean
from ..config import settings

class WeatherClientError(Exception):
    """날씨 API 클라이언트 관련 에러"""
    pass

class WeatherClient:
    """OpenWeatherMap API를 통해 날씨 정보를 가져오는 클라이언트"""

    def __init__(self):
        self.api_key = settings.OWM_API_KEY
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    async def _get_coordinates(self, client: httpx.AsyncClient, destination: str) -> dict | None:
        """도시 이름을 기반으로 위도와 경도를 찾습니다."""
        params = {"q": destination, "limit": 1, "appid": self.api_key}
        try:
            response = await client.get(self.geo_url, params=params)
            response.raise_for_status()
            locations = response.json()
            if locations:
                return {"lat": locations[0]["lat"], "lon": locations[0]["lon"]}
        except httpx.HTTPStatusError as e:
            print(f"Error fetching coordinates for '{destination}': {e} - Response: {e.response.text}")
            return None
        return None

    async def get_weather_forecast(self, destination: str, start_date: date, end_date: date):
        """주어진 기간과 목적지의 평균 날씨 예보를 가져옵니다."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            coords = await self._get_coordinates(client, destination)
            if not coords:
                raise WeatherClientError(f"Could not find coordinates for '{destination}'")

            params = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": self.api_key,
                "units": "metric", # 섭씨 온도
                "lang": "kr"     # 한국어 설명
            }
            
            try:
                response = await client.get(self.forecast_url, params=params)
                response.raise_for_status()
                forecast_data = response.json()
                
                # 여행 기간에 해당하는 예보만 필터링
                relevant_forecasts = [
                    item for item in forecast_data.get("list", [])
                    if start_date <= date.fromisoformat(item["dt_txt"].split(" ")[0]) <= end_date
                ]
                
                if not relevant_forecasts:
                    return {"location": destination, "condition": "정보 없음"}

                # 평균 온도와 가장 빈번한 날씨 상태 계산
                avg_temp = mean([item["main"]["temp"] for item in relevant_forecasts])
                main_condition = max(set([item["weather"][0]["description"] for item in relevant_forecasts]), 
                                     key=[item["weather"][0]["description"] for item in relevant_forecasts].count)

                return {
                    "location": destination,
                    "average_temperature_celsius": round(avg_temp, 1),
                    "condition": main_condition,
                    "icon_url": f"http://openweathermap.org/img/wn/{relevant_forecasts[0]['weather'][0]['icon']}.png"
                }

            except httpx.HTTPStatusError as e:
                raise WeatherClientError(f"Failed to get weather forecast: {e.response.text}")
            except (KeyError, IndexError) as e:
                raise WeatherClientError(f"Failed to parse weather forecast response: {e}")

