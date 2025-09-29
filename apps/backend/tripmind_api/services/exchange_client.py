# tripmind_api/services/exchange_client.py
from __future__ import annotations
import requests
from tripmind_api.config import settings

BASE = settings.EXCHANGE_BASE
DATA = settings.EXCHANGE_DATA_CODE
AUTH = settings.EXCHANGE_API_KEY

def fetch_rates(searchdate: str | None = None) -> list[dict]:
    """
    한국수출입은행 환율 API 호출
    searchdate: YYYYMMDD (예: '20250926'), None이면 API의 기본(오늘/최근영업일)
    """
    params = {"authkey": AUTH, "data": DATA}
    if searchdate:
        params["searchdate"] = searchdate
    r = requests.get(BASE, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    # 정상일 때 list로 내려옴. dict 형태(RESULT 등)로 에러 알려주기도 함.
    if isinstance(data, dict) and data.get("RESULT") != 1:
        raise RuntimeError(f"EXIM error: {data}")
    return data  # 보통 list

def pick_rate(rows: list[dict], code: str = "USD") -> float:
    """
    응답 리스트에서 원하는 통화의 매매기준율(DEAL_BAS_R) float 반환.
    'JPY(100)' 보정 포함.
    """
    for row in rows:
        unit = row.get("CUR_UNIT", "")
        if unit.startswith(code):
            base = float(row["DEAL_BAS_R"].replace(",", ""))
            if "JPY(100)" in unit:
                base /= 100.0
            return base
    raise KeyError(f"{code} not found in EXIM response")
