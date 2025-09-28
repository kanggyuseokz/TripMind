from flask import Blueprint, request
from pydantic import BaseModel, ValidationError
from ..services.trip_parse import parse_trip

bp = Blueprint("planner", __name__)

class ParseIn(BaseModel):
    text: str

@bp.post("/parse")
def parse():
    try:
        data = ParseIn(**request.get_json())
    except ValidationError as e:
        return {"error": e.errors()}, 400

    result = parse_trip(data.text or "")
    return result
