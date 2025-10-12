from flask import Blueprint, request, jsonify
from ..services.map_service import MapService, MapServiceError

# 'map'이라는 이름으로 새로운 Blueprint를 생성합니다.
bp = Blueprint("map", __name__)

# MapService 인스턴스를 생성하여 이 라우트 파일 내에서 사용합니다.
map_service = MapService()

@bp.post("/geocode")
def geocode_poi():
    """
    POI(관심 장소)의 이름과 목적지 정보를 받아 좌표(위도/경도)를 반환합니다.
    Request Body Example:
    {
        "poi_name": "에펠탑",
        "destination_city": "파리",
        "is_domestic": false
    }
    """
    data = request.get_json()
    if not data or not all(k in data for k in ["poi_name", "destination_city", "is_domestic"]):
        return jsonify({"error": "Missing required fields: poi_name, destination_city, is_domestic"}), 400

    try:
        coordinates = map_service.get_coordinates_for_poi(
            poi_name=data["poi_name"],
            destination_city=data["destination_city"],
            is_domestic=data["is_domestic"]
        )
        return jsonify(coordinates), 200
    except MapServiceError as e:
        # MapService에서 발생한 특정 에러를 처리합니다.
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@bp.post("/distance-matrix")
def get_distance_matrix():
    """
    여러 출발지와 목적지 간의 이동 시간 매트릭스를 반환합니다. (현재 해외만 지원)
    Request Body Example:
    {
        "origins": [{"lat": 48.8584, "lng": 2.2945}, {"lat": 48.8606, "lng": 2.3376}],
        "destinations": [{"lat": 48.8584, "lng": 2.2945}, {"lat": 48.8606, "lng": 2.3376}],
        "is_domestic": false
    }
    """
    data = request.get_json()
    if not data or not all(k in data for k in ["origins", "destinations", "is_domestic"]):
        return jsonify({"error": "Missing required fields: origins, destinations, is_domestic"}), 400

    try:
        matrix = map_service.get_distance_matrix(
            origins=data["origins"],
            destinations=data["destinations"],
            is_domestic=data["is_domestic"]
        )
        return jsonify({"distance_matrix": matrix}), 200
    except NotImplementedError as e:
        # 국내 경로 계산 등 아직 구현되지 않은 기능을 호출했을 때의 에러를 처리합니다.
        return jsonify({"error": str(e)}), 501 # 501 Not Implemented
    except MapServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

