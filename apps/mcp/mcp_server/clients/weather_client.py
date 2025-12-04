# mcp/mcp_server/clients/weather_client.py

import httpx
from datetime import date, timedelta
from collections import defaultdict
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
        """
        주어진 기간과 목적지의 날짜별 날씨 예보를 가져옵니다.
        
        Returns:
            dict: {
                "location": str,
                "daily": [
                    {
                        "date": "2025-12-06",
                        "temp": 15.3,
                        "temp_min": 12.0,
                        "temp_max": 18.0,
                        "condition": "Clear",
                        "description": "맑음",
                        "icon": "01d",
                        "humidity": 65,
                        "wind_speed": 3.5
                    },
                    ...
                ]
            }
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            coords = await self._get_coordinates(client, destination)
            if not coords:
                raise WeatherClientError(f"Could not find coordinates for '{destination}'")

            params = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": self.api_key,
                "units": "metric",  # 섭씨 온도
                "lang": "kr"        # 한국어 설명
            }
            
            try:
                response = await client.get(self.forecast_url, params=params)
                response.raise_for_status()
                forecast_data = response.json()
                
                # ✅ 날짜별로 데이터 그룹화
                daily_data = defaultdict(list)
                
                for item in forecast_data.get("list", []):
                    # dt_txt 형식: "2025-12-06 15:00:00"
                    forecast_datetime = item["dt_txt"]
                    forecast_date = forecast_datetime.split(" ")[0]  # "2025-12-06"
                    
                    # 여행 기간 내의 데이터만 수집
                    item_date = date.fromisoformat(forecast_date)
                    if start_date <= item_date <= end_date:
                        daily_data[forecast_date].append(item)
                
                if not daily_data:
                    # ✅ 데이터가 없으면 여행 기간만큼 빈 데이터 생성
                    print(f"[Weather] No forecast data available for {destination} ({start_date} ~ {end_date})")
                    daily_forecasts = []
                    current_date = start_date
                    while current_date <= end_date:
                        daily_forecasts.append({
                            "date": current_date.isoformat(),
                            "temp": None,
                            "temp_min": None,
                            "temp_max": None,
                            "condition": "N/A",
                            "description": "정보 없음",
                            "icon": "01d",
                            "humidity": None,
                            "wind_speed": None
                        })
                        current_date += timedelta(days=1)
                    
                    return {
                        "location": destination,
                        "daily": daily_forecasts
                    }
                
                # ✅ 각 날짜별로 평균/대표값 계산
                daily_forecasts = []
                
                for forecast_date in sorted(daily_data.keys()):
                    day_items = daily_data[forecast_date]
                    
                    # 온도 평균 및 min/max
                    temps = [item["main"]["temp"] for item in day_items]
                    temp_mins = [item["main"]["temp_min"] for item in day_items]
                    temp_maxs = [item["main"]["temp_max"] for item in day_items]
                    
                    avg_temp = round(mean(temps), 1)
                    min_temp = round(min(temp_mins), 1)
                    max_temp = round(max(temp_maxs), 1)
                    
                    # 가장 빈번한 날씨 상태 (영어 main)
                    conditions = [item["weather"][0]["main"] for item in day_items]
                    main_condition = max(set(conditions), key=conditions.count)
                    
                    # 가장 빈번한 날씨 설명 (한국어)
                    descriptions = [item["weather"][0]["description"] for item in day_items]
                    main_description = max(set(descriptions), key=descriptions.count)
                    
                    # 대표 아이콘 (가장 많이 등장하는 아이콘)
                    icons = [item["weather"][0]["icon"] for item in day_items]
                    main_icon = max(set(icons), key=icons.count)
                    
                    # 습도, 풍속 평균
                    avg_humidity = round(mean([item["main"]["humidity"] for item in day_items]))
                    avg_wind = round(mean([item["wind"]["speed"] for item in day_items]), 1)
                    
                    daily_forecasts.append({
                        "date": forecast_date,
                        "temp": avg_temp,
                        "temp_min": min_temp,
                        "temp_max": max_temp,
                        "condition": main_condition,        # "Clear", "Clouds", "Rain" 등
                        "description": main_description,    # "맑음", "구름 조금" 등
                        "icon": main_icon,                  # "01d", "02d" 등
                        "humidity": avg_humidity,           # %
                        "wind_speed": avg_wind              # m/s
                    })
                
                return {
                    "location": destination,
                    "daily": daily_forecasts
                }

            except httpx.HTTPStatusError as e:
                raise WeatherClientError(f"Failed to get weather forecast: {e.response.text}")
            except (KeyError, IndexError) as e:
                raise WeatherClientError(f"Failed to parse weather forecast response: {e}")