# backend/tripmind_api/services/trip_parse.py

import re
from typing import Tuple, Optional
from ..data.aliases import ALIASES

# 컨텍스트 키워드 (출발/도착 판정에 사용)
DEPART_HINTS = ["에서", "출발", "발"]
ARRIVE_HINTS = ["로", "행", "도착", "까지", "->", "→", "➡", "⇒"]

# 동적 토큰 테이블 생성
def _build_token_tables():
    token_to_city = {}
    tokens = []
    for city, names in ALIASES.items():
        for n in names:
            key = n.strip().lower()
            if not key:
                continue
            token_to_city[key] = city
            tokens.append(re.escape(n))
    pattern = re.compile(rf"({'|'.join(tokens)})", re.IGNORECASE)
    return token_to_city, pattern

_TOKEN_TO_CITY, _PATTERN = _build_token_tables()

def infer_origin_dest(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    1) 텍스트에서 모든 도시/공항 토큰 위치 수집
    2) 주변 문맥(출발/도착 힌트)으로 역할 판정
    3) 판정 못하면 가장 왼쪽=출발, 가장 오른쪽=도착으로 폴백
    """
    if not text:
        return None, None

    hits = [(m.group(1), m.start(), m.end()) for m in _PATTERN.finditer(text)]
    if not hits:
        return None, None

    origin, dest = None, None

    def _has_any(hay: str, needles) -> bool:
        return any(n in hay for n in needles)

    for tok, s, e in hits:
        city = _TOKEN_TO_CITY.get(tok.lower())
        if not city:
            continue
        # 주변 8자 정도 컨텍스트 확인 (한글 조사/기호용)
        ctx = text[max(0, s-8):min(len(text), e+8)]
        if _has_any(ctx, DEPART_HINTS) and origin is None:
            origin = city
        if _has_any(ctx, ARRIVE_HINTS):
            dest = city

    # 폴백: 왼쪽/오른쪽
    if origin is None:
        left_city = _TOKEN_TO_CITY.get(hits[0][0].lower())
        origin = left_city
    if dest is None:
        right_city = _TOKEN_TO_CITY.get(hits[-1][0].lower())
        dest = right_city

    # 같은 도시가 둘 다 잡혔을 때 간단 조정(예: "서울에서 서울로"같은 오류)
    if origin == dest and len(hits) >= 2:
        # 두 번째 토큰을 도착으로 가정
        dest = _TOKEN_TO_CITY.get(hits[-1][0].lower())

    return origin, dest

# 날짜/인원 간단 파서(임시)
DATE_RANGE = re.compile(r"(\d{1,2})[./-](\d{1,2})\s*[~\-–]\s*(\d{1,2})[./-](\d{1,2})")
NIGHTS = re.compile(r"(\d+)\s*박")
PAX = re.compile(r"(\d+)\s*(명|인|pax)", re.IGNORECASE)

def parse_trip(text: str) -> dict:
    origin, dest = infer_origin_dest(text)
    # 임시 기본값
    start_date = "2025-10-10"
    end_date   = "2025-10-13"
    pax = 2

    # 날짜 범위 "10/10~10/13" 형태 추출(연도는 임시 고정)
    m = DATE_RANGE.search(text)
    if m:
        m1, d1, m2, d2 = m.groups()
        start_date = f"2025-{int(m1):02d}-{int(d1):02d}"
        end_date   = f"2025-{int(m2):02d}-{int(d2):02d}"
    else:
        # "3박" → 종료일 계산은 나중에 정확히, 지금은 미사용
        pass

    mp = PAX.search(text)
    if mp:
        pax = int(mp.group(1))

    return {
        "origin": origin or "서울",
        "destination": dest or "오사카",
        "startDate": start_date,
        "endDate": end_date,
        "pax": pax,
    }
