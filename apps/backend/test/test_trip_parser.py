from tripmind_api.services.trip_parse import infer_origin_dest, parse_trip

def test_basic_direction():
    o,d = infer_origin_dest("서울에서 오사카 3박 2명")
    assert o == "서울" and d == "오사카"

def test_arrow_and_codes():
    o,d = infer_origin_dest("김포->하네다 10/10~10/13 1명")
    assert o == "서울" and d == "도쿄"  # 김포/하네다 별칭 매핑

def test_parse_trip_dates():
    out = parse_trip("인천발 뉴욕 도착 10/10-10/13 2명")
    assert out["origin"] == "서울"
    assert out["destination"] == "뉴욕"
    assert out["startDate"] == "2025-10-10"
    assert out["endDate"] == "2025-10-13"
    assert out["pax"] == 2
    