from flask import Blueprint, request, jsonify

# TripMind의 모든 비즈니스 로직을 총괄하는 TripService를 임포트합니다.
from ..services.trip_service import TripService
from ..services.llm_service import LLMServiceError

# 'trip'이라는 이름으로 새로운 Blueprint를 생성합니다.
bp = Blueprint("trip", __name__)

# TripService 인스턴스를 생성하여 이 라우트 파일 내에서 사용합니다.
trip_service = TripService() 

@bp.post("/plan")
def create_trip_plan():
    """
    사용자의 자연어 요청을 받아 전체 여행 계획을 생성하는 메인 엔드포인트입니다.
    TripService를 호출하여 모든 비즈니스 로직을 처리합니다.
    """
    # 프론트엔드에서 {"text": "오사카 3박 4일 여행", "preferred_style": "맛집"} 형식의
    # JSON을 보낼 것으로 예상합니다.
    request_data = request.get_json()
    if not request_data or "text" not in request_data:
        return jsonify({"error": "text field is required"}), 400

    try:
        # --- Mock 응답을 실제 서비스 호출로 교체 ---
        # 사용자의 요청 전체를 TripService에 전달하여 여행 계획 생성을 시작합니다.
        final_plan = trip_service.create_personalized_trip(request_data)
        
        # TripService가 반환한 최종 여행 계획을 클라이언트에 응답합니다.
        return jsonify(final_plan), 200

    except LLMServiceError as e:
        # LLM 파싱 단계에서 에러가 발생한 경우
        return jsonify({"error": f"LLM parsing failed: {e}"}), 500
    except Exception as e:
        # 그 외 예측하지 못한 서버 에러 처리
        # 실제 운영 환경에서는 로깅을 통해 에러를 추적해야 합니다.
        print(f"An unexpected error occurred: {e}") # 개발용 에러 로그
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

