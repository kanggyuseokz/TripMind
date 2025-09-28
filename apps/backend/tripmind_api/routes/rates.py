# tripmind_api/routes/rates.py
from flask import Blueprint, jsonify, request
from tripmind_api.services.exchange_client import fetch_rates, pick_rate

bp = Blueprint("rates", __name__)

@bp.get("/today")
def today():
    data = fetch_rates(None)
    return jsonify(data)

@bp.get("/convert/usd-krw")
def convert_usd_krw():
    """
    예: /api/rates/convert/usd-krw?date=20250926&amount=100
    """
    date = request.args.get("date")       # YYYYMMDD (옵션)
    amount = float(request.args.get("amount", "100"))
    data = fetch_rates(date)
    usd_krw = pick_rate(data, "USD")
    return jsonify({
        "date": date,
        "usd_krw": usd_krw,
        "amount_usd": amount,
        "amount_krw": amount * usd_krw
    })
