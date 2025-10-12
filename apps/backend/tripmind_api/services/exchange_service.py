from __future__ import annotations
import re
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tripmind_api.config import settings

class ExchangeAPIError(Exception):
    """환율 API 관련 에러"""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class ExchangeService:
    """한국수출입은행 환율 정보를 조회하는 서비스"""
    def __init__(self, timeout: int = 10, retries: int = 3):
        self.base_url = settings.EXCHANGE_BASE
        self.auth_key = settings.EXCHANGE_API_KEY
        
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.timeout = timeout

    def fetch_rates(self, search_date: str | None = None) -> list[dict]:
        """지정된 날짜의 환율 정보를 API로 가져옵니다."""
        params = {
            "authkey": self.auth_key,
            "data": settings.EXCHANGE_DATA_CODE
        }
        if search_date:
            params["searchdate"] = search_date
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and data.get("RESULT") != 1:
                raise ExchangeAPIError(f"EXIM error: {data.get('message', 'Unknown error')}")
            return data
        except requests.Timeout:
            raise ExchangeAPIError("API request timed out", status_code=408)
        except requests.RequestException as e:
            raise ExchangeAPIError(f"API request failed: {e}", status_code=e.response.status_code if e.response else 500)
        except json.JSONDecodeError:
            raise ExchangeAPIError("Failed to parse API response as JSON", status_code=500)

    def get_rate(self, currency_code: str, search_date: str | None = None) -> float:
        """특정 통화의 KRW 환율을 조회합니다."""
        rows = self.fetch_rates(search_date)
        currency_code = currency_code.upper()

        for row in rows:
            unit = row.get("CUR_UNIT", "")
            if unit == currency_code:
                return float(row["DEAL_BAS_R"].replace(",", ""))
            
            # JPY(100) 같은 특수 케이스 처리
            match = re.match(r"([A-Z]{3})\((\d+)\)", unit)
            if match and match.group(1) == currency_code:
                base_rate = float(row["DEAL_BAS_R"].replace(",", ""))
                divisor = int(match.group(2))
                return base_rate / divisor

        raise KeyError(f"'{currency_code}' not found in API response.")
