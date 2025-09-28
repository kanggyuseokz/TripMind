from flask import Blueprint, request

bp = Blueprint("cost", __name__)

@bp.post("/estimate")
def estimate():
    data = request.get_json()
    # 선택된 항공/숙소 합산 (세금/수수료 간단 가정)
    flight = data.get("flight", {}).get("price", 0)
    hotel  = data.get("hotel", {}).get("priceTotal", 0)
    fees   = round((flight + hotel) * 0.05, 2)
    total  = round(flight + hotel + fees, 2)
    return {"currency":"KRW","breakdown":{"flight":flight,"hotel":hotel,"fees":fees},"total":total}
