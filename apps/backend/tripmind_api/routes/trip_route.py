from flask import Blueprint, request, jsonify
from ..services.trip_service import TripService
from ..services.llm_service import LLMService, LLMServiceError

bp = Blueprint("trip", __name__)

llm_service = LLMService()
trip_service = TripService()

@bp.post("/plan")
def handle_conversation():
    """
    사용자와의 전체 대화 기록을 받아 처리합니다.
    - 정보가 충분하면 여행 계획을 생성합니다.
    - 정보가 부족하면 사용자에게 다시 질문합니다.
    """
    request_data = request.get_json()
    if not request_data or "messages" not in request_data:
        return jsonify({"error": "messages field is required"}), 400

    messages = request_data["messages"]

    try:
        # 1. LLM을 통해 현재까지의 대화 내용 전체를 파싱합니다.
        parsed_data = llm_service.parse_conversation(messages)
        
        # 2. 파싱된 결과에 핵심 정보가 모두 포함되어 있는지 검증합니다.
        required_fields = ['origin', 'destination', 'start_date', 'end_date']
        missing_fields = [
            field for field in required_fields 
            if parsed_data.get(field) is None or parsed_data.get(field) == ""
        ]
        
        if missing_fields:
            # 3-A. 정보가 부족하면, 사용자에게 되물을 질문을 LLM에게 생성하도록 요청합니다.
            question = llm_service.generate_clarifying_question(messages, missing_fields)
            return jsonify({
                "type": "question",
                "content": question,
                "missing_fields": missing_fields
            }), 200
        else:
            # --- 💡 여기를 수정합니다 ---
            # 3-B. 정보가 충분하면, TripService를 호출하여 최종 여행 계획을 생성합니다.
            # 원본 요청 데이터(request_data)와 파싱된 데이터(parsed_data)를 모두 전달합니다.
            final_plan = trip_service.create_personalized_trip(request_data, parsed_data)
            return jsonify({
                "type": "plan",
                "content": final_plan
            }), 200

    except LLMServiceError as e:
        return jsonify({"error": f"LLM service failed: {e}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}") # 개발용 에러 로그
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

