from flask import Blueprint, request
from ..adapters.mcp_client import get_quotes

bp = Blueprint("quotes", __name__)

@bp.post("/search")
def search():
    payload = request.get_json()
    # MCP 서버에서 mock 견적 가져오기
    flights, hotels = get_quotes(payload)
    return {"flights": flights, "hotels": hotels}
