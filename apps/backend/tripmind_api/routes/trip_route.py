# backend/tripmind_api/routes/trip_route.py
from flask import Blueprint, request, jsonify
from ..services.trip_service import TripService
from ..services.llm_service import LLMService, LLMServiceError
import httpx
from datetime import datetime
# 💡 1. extensions.py에서 'db' 세션을 임포트합니다.
from ..extensions import db
# 💡 2. models.py에서 'Trip'과 'User' 모델을 임포트합니다.
from ..models import Trip, User

bp = Blueprint("trip", __name__)

llm_service = LLMService()
trip_service = TripService()

@bp.post("/plan")
def handle_plan_request(): # 👈 함수 이름 변경 (대화가 아니므로)
    """
    프론트엔드로부터 구조화된 JSON(장소, 날짜 등)과
    여행 스타일(텍스트)을 받아 여행 계획을 생성합니다. (하이브리드 방식)
    """
    request_data = request.get_json()
    if not request_data:
        return jsonify({"error": "Request body is required"}), 400

    try:
        # --- 1. LLM 호출 (최소한으로 사용) ---
        # 💡 A. (LLM 사용 O) 'preferred_style_text'를 기반으로 '흥미' 키워드 추출
        # (llm_service에 extract_interests 함수가 구현되어 있다고 가정)
        interests = llm_service.extract_interests(
            request_data.get("preferred_style_text", "관광")
        )
        
        # 💡 B. (LLM 사용 O) 'origin'/'destination'을 기반으로 '국내/해외' 추론
        # (llm_service에 check_domestic 함수가 구현되어 있다고 가정)
        is_domestic = llm_service.check_domestic(
            request_data.get("origin"),
            request_data.get("destination")
        )

        # --- 2. parsed_data 조립 (UI 데이터 + LLM 추론 데이터) ---
        # 💡 (LLM 사용 X) UI에서 받은 정형 데이터는 그대로 사용
        party_size = request_data.get("party_size", 1)
        budget = request_data.get("budget", 0)
        
        parsed_data = {
            "origin": request_data.get("origin"),
            "destination": request_data.get("destination"),
            "start_date": request_data.get("start_date"),
            "end_date": request_data.get("end_date"),
            "party_size": party_size,
            
            "is_domestic": is_domestic, # 💡 LLM 추론 결과
            "interests": interests,     # 💡 LLM 추론 결과
            
            # 💡 (LLM 사용 X) 예산 정보는 백엔드에서 직접 계산
            "budget_per_person": {
                "amount": (budget / party_size) if party_size > 0 else budget,
                "currency": "KRW"
            }
        }
        
        # 💡 (참고) '정보가 부족하여 되묻는' 로직은 프론트 UI가 처리하므로 제거됨.

        # --- 3. TripService 호출 (동기) ---
        # request_data (원본 요청)와 parsed_data (조립된 데이터)를 모두 전달.
        final_plan = trip_service.create_personalized_trip(request_data, parsed_data)

                # --- 💡 4. (신규) DB에 여행 계획 저장 ---
        try:
            # (임시: 실제로는 @jwt_required() 등으로 로그인된 user_id를 가져와야 함)
            current_user_id = 1 
            
            # 4-1. models.py의 Trip 클래스로 새 여행 객체 생성
            new_trip = Trip(
                user_id = current_user_id,
                origin = parsed_data.get("origin"),
                destination = parsed_data.get("destination"),
                start_date = datetime.fromisoformat(parsed_data.get("start_date")),
                end_date = datetime.fromisoformat(parsed_data.get("end_date")),
                party_size = parsed_data.get("party_size", 1),
                preferred_style_text = request_data.get("preferred_style_text"),
                trip_summary = final_plan.get("trip_summary"),
                total_cost = final_plan.get("total_cost"),
                
                # 4-2. JSON 데이터 저장 (SQLAlchemy가 자동 변환)
                schedule_json = final_plan.get("schedule", []),
                cost_chart_json = final_plan.get("cost_breakdown_chart", []),
                raw_data_json = final_plan.get("raw_data", {})
            )

            # 4-3. 세션에 추가하고 DB에 커밋 (flask_sqlalchemy는 'db.session' 사용)
            db.session.add(new_trip)
            db.session.commit()
            
        except Exception as db_error:
            db.session.rollback() # 👈 오류 발생 시 DB 롤백
            print(f"DB 저장 실패: {db_error}")
            # (DB 오류가 나더라도 사용자에게는 플랜을 반환)
        
        return jsonify({
            "type": "plan",
            "content": final_plan
        }), 200

    except LLMServiceError as e:
        return jsonify({"error": f"LLM service failed: {e}"}), 500
    except httpx.HTTPStatusError as e:
         # mcp_service가 반환한 오류 (예: 404, 500)
         return jsonify({"error": f"MCP Service Error: {e.response.text}"}), e.response.status_code
    except httpx.RequestError as e:
        # MCP 서버 연결 자체 실패
         return jsonify({"error": f"MCP Service Connection Error: {e}"}), 503
    except Exception as e:
        print(f"An unexpected error occurred: {e}") # 개발용 에러 로그
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500