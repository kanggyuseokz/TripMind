# backend/tripmind_api/routes/trip_route.py
from flask import Blueprint, request, jsonify
from ..services.trip_service import TripService
from ..services.llm_service import LLMService, LLMServiceError
import httpx
from datetime import datetime
from ..extensions import db
from ..models import Trip, User
from flask_jwt_extended import jwt_required, get_jwt_identity

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
@jwt_required() # 💡 이 API는 토큰이 있어야 호출 가능
def save_trip():
    """
    프론트엔드에서 확정된 여행 계획을 받아 DB에 저장합니다.
    """
    # 💡 토큰에서 현재 로그인한 사용자의 ID를 자동으로 추출
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # 날짜 문자열 처리
        start_date_str = data.get('startDate')
        end_date_str = data.get('endDate')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        # 1. DB 모델 객체 생성
        new_trip = Trip(
            user_id=current_user_id, # 💡 토큰에서 가져온 ID 사용 (보안 강화)
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
    
@bp.post("/modify")
def modify_trip_plan():
    """
    사용자의 피드백을 받아 특정 일정(Slot)을 수정합니다.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        current_plan = data.get("current_plan")
        target_slot = data.get("target_slot") # { dayIndex: 0, eventIndex: 1 }
        user_prompt = data.get("user_prompt")

        if not current_plan or not target_slot or not user_prompt:
            return jsonify({"error": "Missing required fields"}), 400

        # 1. LLM 서비스에 수정 요청 위임
        # (llm_service.modify_plan 메서드는 새로 구현해야 함)
        modified_event = llm_service.modify_plan(current_plan, target_slot, user_prompt)
        
        # 2. 수정된 이벤트 반환
        # 프론트엔드에서는 이 응답을 받아 해당 Slot만 갈아끼웁니다.
        return jsonify({
            "ok": True,
            "modified_event": modified_event
        }), 200

    except LLMServiceError as e:
        return jsonify({"error": f"LLM modification failed: {e}"}), 500
    except Exception as e:
        print(f"Modify Error: {e}")
        return jsonify({"error": str(e)}), 500