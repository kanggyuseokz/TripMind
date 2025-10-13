from __future__ import annotations
import re
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..config import settings

class ExchangeAPIError(Exception):
    """환율 API 관련 에러"""
    pass

class ExchangeService:
    """한국수출입은행 환율 정보를 가져오는 서비스"""

    def __init__(self, timeout: int = 10, retries: int = 3):
        self.base_url = settings.EXCHANGE_BASE
        self.auth_key = settings.EXCHANGE_API_KEY
        self.data_code = settings.EXCHANGE_DATA_CODE
        self.timeout = timeout
        
        retry_strategy = Retry(
            total=retries, backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        
        # --- 💡 여기를 수정합니다 ---
        # SSL 인증서 검증을 비활성화하여 SSLCertVerificationError를 우회합니다.
        self.session.verify = False 
        # urllib3의 경고 메시지를 숨깁니다.
        requests.packages.urllib3.disable_warnings()
        # ------------------------

    def fetch_rates(self, search_date: str | None = None) -> list[dict]:
        """한국수출입은행 환율 API를 호출하여 전체 환율 정보를 가져옵니다."""
        params = {"authkey": self.auth_key, "data": self.data_code}
        if search_date:
            params["searchdate"] = search_date
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and data.get("result") != 1:
                raise ExchangeAPIError(f"API returned an error: {data}")
            return data
        except (requests.RequestException, json.JSONDecodeError) as e:
            raise ExchangeAPIError(f"API request failed: {e}")

    def get_rate(self, currency_code: str, search_date: str | None = None) -> float:
        """특정 통화의 매매기준율(KRW)을 조회합니다."""
        rows = self.fetch_rates(search_date)
        
        for row in rows:
            unit = row.get("cur_unit", "")
            if unit.startswith(currency_code.upper()):
                base_rate = float(row["deal_bas_r"].replace(",", ""))
                
                # JPY(100) 등 단위 보정
                match = re.search(r"\((\d+)\)", unit)
                if match:
                    divisor = int(match.group(1))
                    if divisor > 0:
                        base_rate /= divisor
                
                return base_rate
        
        raise KeyError(f"Currency code '{currency_code}' not found in API response.")

