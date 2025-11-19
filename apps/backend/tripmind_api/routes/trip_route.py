# backend/tripmind_api/routes/trip_route.py
from flask import Blueprint, request, jsonify
from ..services.trip_service import TripService
from ..services.llm_service import LLMService, LLMServiceError
import httpx
from datetime import datetime
# 💡 extensions.py에서 'db' 세션을 임포트합니다.
from ..extensions import db
# 💡 models.py에서 'Trip'과 'User' 모델을 임포트합니다.
from ..models import Trip, User

bp = Blueprint("trip", __name__)

llm_service = LLMService()
trip_service = TripService()

@bp.post("/plan")
def handle_plan_request():
    """
    프론트엔드로부터 구조화된 JSON(장소, 날짜 등)과
    여행 스타일(텍스트)을 받아 여행 계획을 생성합니다. (하이브리드 방식)
    """
    request_data = request.get_json()
    if not request_data:
        return jsonify({"error": "Request body is required"}), 400

    try:
        # --- 1. LLM 호출 (최소한으로 사용) ---
        interests = llm_service.extract_interests(
            request_data.get("preferred_style_text", "관광")
        )
        
        is_domestic = llm_service.check_domestic(
            request_data.get("origin"),
            request_data.get("destination")
        )

        # --- 2. parsed_data 조립 ---
        party_size = int(request_data.get("party_size", 1))
        budget = int(request_data.get("budget", 0))
        
        parsed_data = {
            "origin": request_data.get("origin"),
            "destination": request_data.get("destination"),
            "start_date": request_data.get("start_date"),
            "end_date": request_data.get("end_date"),
            "party_size": party_size,
            "is_domestic": is_domestic,
            "interests": interests,
            "budget_per_person": {
                "amount": (budget / party_size) if party_size > 0 else budget,
                "currency": "KRW"
            }
        }
        
        # --- 3. TripService 호출 (동기) ---
        final_plan = trip_service.create_personalized_trip(request_data, parsed_data)
        
        # (참고: /plan 에서는 계획을 생성해서 보여주기만 하고, 저장은 /save 에서 수행합니다)
        
        return jsonify({
            "type": "plan",
            "content": final_plan
        }), 200

    except LLMServiceError as e:
        return jsonify({"error": f"LLM service failed: {e}"}), 500
    except httpx.HTTPStatusError as e:
         return jsonify({"error": f"MCP Service Error: {e.response.text}"}), e.response.status_code
    except httpx.RequestError as e:
         return jsonify({"error": f"MCP Service Connection Error: {e}"}), 503
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# 👇 [NEW] 여행 계획 저장 API 추가
@bp.post("/save")
def save_trip():
    """
    프론트엔드에서 확정된 여행 계획을 받아 DB에 저장합니다.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # (로그인 기능 연동 전이므로 임시 ID 1 사용)
    user_id = data.get('user_id', 1) 

    try:
        # 날짜 문자열 처리 (YYYY-MM-DD 형식이 아닐 경우 대비)
        start_date_str = data.get('startDate')
        end_date_str = data.get('endDate')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass # 날짜 형식이 맞지 않으면 None으로 저장
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        # 1. DB 모델 객체 생성
        new_trip = Trip(
            user_id=user_id,
            title=data.get('trip_summary', '나만의 여행'), 
            destination=data.get('destination', ''),
            start_date=start_date,
            end_date=end_date,
            total_cost=int(data.get('total_cost', 0)),
            head_count=int(data.get('head_count', 1)),
            
            # 상세 일정(배열)을 JSON 컬럼에 그대로 저장
            schedule_json=data.get('schedule', []) 
        )

        # 2. DB에 저장 (Commit)
        db.session.add(new_trip)
        db.session.commit()

        return jsonify({
            "ok": True, 
            "message": "여행이 성공적으로 저장되었습니다.", 
            "trip_id": new_trip.id
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Save Error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500