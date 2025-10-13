# tripmind_api/routes/rates.py
from flask import Blueprint, jsonify, request
from ..services.exchange_service import ExchangeService, ExchangeAPIError


bp = Blueprint("rates", __name__)
exchange_service = ExchangeService() # 애플리케이션 시작 시 클라이언트 인스턴스 생성

@bp.get("/today")
def today():
    """오늘 또는 가장 최근 영업일의 전체 환율 정보를 반환합니다."""
    try:
        data = exchange_service.fetch_rates(None)
        return jsonify(data)
    except ExchangeAPIError as e:
        # API 에러 발생 시, 500번대 에러와 함께 에러 메시지를 반환
        return jsonify({"error": str(e)}), 503 # 503 Service Unavailable

@bp.get("/convert")
def convert():
    """
    특정 통화를 KRW로 변환합니다.
    예: /api/rates/convert?date=20250926&amount=100&currency=USD
    """
    date = request.args.get("date")       # YYYYMMDD (옵션)
    amount = float(request.args.get("amount", "100.0"))
    currency = request.args.get("currency", "USD").upper()
    
    try:
        # 클라이언트의 get_rate 메소드를 사용하여 환율 조회
        rate = exchange_service.get_rate(currency, date)
        return jsonify({
            "date": date,
            "currency_pair": f"{currency}/KRW",
            "rate": rate,
            "amount_from": amount,
            "amount_to_krw": round(amount * rate, 2)
        })
    except ExchangeAPIError as e:
        return jsonify({"error": str(e)}), 503
    except KeyError as e:
        # 지원하지 않는 통화 코드 요청 시, 404 에러 반환
        return jsonify({"error": str(e)}), 404 # 404 Not Found
