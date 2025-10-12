import httpx
from datetime import date
from ..config import settings

class WeatherClient:
    """OpenWeatherMap API를 통해 날씨 정보를 가져오는 클라이언트"""

    async def get_weather_forecast(self, destination: str, start_date: date, end_date: date):
        """
        주어진 기간과 목적지의 날씨 예보를 가져옵니다.
        TODO: 실제 OpenWeatherMap API 연동 로직 구현 필요
        """
        # 실제 API 연동 전, 테스트를 위한 Mock(가상) 데이터 반환
        print(f"Fetching weather for: {destination}")
        
        # 목적지에 따라 다른 날씨를 반환
        if "도쿄" in destination or "오사카" in destination:
            weather_condition = "맑음"
            avg_temp = 22.5
        else:
            weather_condition = "구름 조금"
            avg_temp = 18.0

        return {
            "location": destination,
            "forecast_period": f"{start_date.isoformat()} ~ {end_date.isoformat()}",
            "average_temperature_celsius": avg_temp,
            "condition": weather_condition,
            "icon_url": "https://example.com/weather-icon.png"
        }
