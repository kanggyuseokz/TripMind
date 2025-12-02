# backend/tripmind_api/routes/trip_route.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.llm_service import LLMService
from ..services.trip_service import TripService
from ..models import Trip
from ..extensions import db

bp = Blueprint("trip", __name__)
llm_service = LLMService()
trip_service = TripService()

@bp.post("/plan")
def plan_trip():
    """
    프론트엔드에서 사용자 입력을 받아 LLM으로 파싱
    - origin/destination: IATA 코드 추출
    - preferred_style_text: interests 추출
    """
    try:
        data = request.get_json()
        
        # ✅ 프론트엔드에서 보낸 원본 데이터
        origin = data.get('origin', '')
        destination = data.get('destination', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        party_size = data.get('party_size', 1)
        budget = data.get('budget', 0)
        preferred_style_text = data.get('preferred_style_text', '')

        # ✅ 유효성 검사
        if not all([destination, start_date, end_date]):
            return jsonify({"error": "도착지와 날짜는 필수입니다."}), 400

        # ✅ LLM으로 전체 데이터 파싱
        user_request = f"""
출발지: {origin}
도착지: {destination}
여행 기간: {start_date} ~ {end_date}
인원: {party_size}명
1인 예산: {budget}원
여행 스타일: {preferred_style_text}
"""
        
        print(f"[TripRoute] 📝 User Request:\n{user_request}")
        
        # LLM 파싱
        parsed_data = llm_service.parse_user_request(user_request)
        
        print(f"[TripRoute] 🎯 LLM Parsed Data: {parsed_data}")

        # ✅ 프론트엔드에서 받은 확정된 값으로 덮어쓰기
        parsed_data['start_date'] = start_date
        parsed_data['end_date'] = end_date
        parsed_data['party_size'] = int(party_size)
        parsed_data['budget_per_person'] = {
            'amount': int(budget),
            'currency': 'KRW'
        }
        
        # origin이 명확하면 그대로 사용
        if origin and '(' in origin:
            parsed_data['origin'] = origin
        
        request_data = {
            'preferred_style': parsed_data.get('interests', ['관광'])[0] if parsed_data.get('interests') else '관광',
            'user_input': preferred_style_text
        }

        print(f"[TripRoute] ✅ Final Parsed Data: {parsed_data}")

        # ✅ TripService로 여행 계획 생성
        trip_plan = trip_service.create_personalized_trip(request_data, parsed_data)

        return jsonify(trip_plan), 200

    except Exception as e:
        print(f"[TripRoute] ❌ Error in /plan: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@bp.post("/save")
@jwt_required()
def save_trip():
    """여행 계획 저장"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        new_trip = Trip(
            user_id=int(user_id),
            trip_summary=data.get('trip_summary'),
            destination=data.get('destination'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            head_count=data.get('pax') or data.get('party_size') or data.get('head_count') or 2,
            total_cost=data.get('budget') or data.get('total_cost'),
            schedule_json=data.get('schedule'),
            raw_data_json=data.get('raw_data')
        )

        db.session.add(new_trip)
        db.session.commit()

        return jsonify({
            "message": "여행 계획이 저장되었습니다.",
            "trip_id": new_trip.id
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"[TripRoute] ❌ Error in /save: {e}")
        return jsonify({"error": str(e)}), 500


@bp.get("/saved")
@jwt_required()
def get_saved_trips():
    """저장된 여행 목록 조회"""
    try:
        user_id = get_jwt_identity()
        trips = Trip.query.filter_by(user_id=int(user_id)).order_by(Trip.created_at.desc()).all()

        result = []
        for trip in trips:
            result.append({
                "id": trip.id,
                "trip_summary": trip.trip_summary,
                "destination": trip.destination,
                "start_date": trip.start_date.isoformat() if trip.start_date else None,
                "end_date": trip.end_date.isoformat() if trip.end_date else None,
                "pax": trip.head_count,  # ← 수정!
                "party_size": trip.head_count,  # 추가
                "budget": trip.total_cost,  # ← 수정!
                "total_cost": trip.total_cost,  # 추가
                "schedule": trip.schedule_json,
                "raw_data": trip.raw_data_json,
                "created_at": trip.created_at.isoformat()
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"[TripRoute] ❌ Error in /saved: {e}")
        return jsonify({"error": str(e)}), 500

@bp.get("/saved/<int:trip_id>")
@jwt_required()
def get_trip_detail(trip_id):
    """특정 여행 상세 조회"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.filter_by(id=trip_id, user_id=int(user_id)).first()
        
        if not trip:
            return jsonify({"error": "Trip not found"}), 404
        
        return jsonify({
            "id": trip.id,
            "trip_summary": trip.trip_summary,
            "destination": trip.destination,
            "start_date": trip.start_date.isoformat() if trip.start_date else None,
            "end_date": trip.end_date.isoformat() if trip.end_date else None,
            "pax": trip.head_count,
            "party_size": trip.head_count,
            "head_count": trip.head_count,
            "budget": trip.total_cost,
            "total_cost": trip.total_cost,
            "schedule": trip.schedule_json,
            "raw_data": trip.raw_data_json
        }), 200

    except Exception as e:
        print(f"[TripRoute] ❌ Error in /saved/<id>: {e}")
        return jsonify({"error": str(e)}), 500

@bp.delete("/saved/<int:trip_id>")
@jwt_required()
def delete_trip(trip_id):
    """여행 계획 삭제"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.filter_by(id=trip_id, user_id=int(user_id)).first()

        if not trip:
            return jsonify({"error": "Trip not found"}), 404

        db.session.delete(trip)
        db.session.commit()

        return jsonify({"message": "여행 계획이 삭제되었습니다."}), 200

    except Exception as e:
        db.session.rollback()
        print(f"[TripRoute] ❌ Error in /delete: {e}")
        return jsonify({"error": str(e)}), 500