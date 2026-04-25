# backend/tripmind_api/routes/trip_route.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.llm_service import LLMService
from ..services.trip_service import TripService
from ..models import Trip
from ..extensions import db
from datetime import datetime

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
        explicit_travel_style = data.get('travel_style', '')   # 체크박스에서 직접 전달
        secondary_styles = data.get('secondary_styles', [])

        # ✅ 유효성 검사
        if not all([destination, start_date, end_date]):
            return jsonify({"error": "도착지와 날짜는 필수입니다."}), 400

        valid_styles = ['relaxation', 'sightseeing', 'foodie', 'activity', 'shopping']

        # 국내 여행 판별 (목적지 이름 기반)
        DOMESTIC_KEYWORDS = [
            '서울', '부산', '제주', '인천', '대구', '광주', '대전', '울산', '수원',
            '강릉', '경주', '전주', '여수', '순천', '춘천', '속초', '포항', '거제',
            '통영', '남해', '가평', '양평', '홍천', '고성', '설악', '한라', '백두',
            'seoul', 'busan', 'jeju', 'incheon', 'daegu', 'gwangju', 'daejeon'
        ]
        is_domestic = any(kw in destination.lower() for kw in DOMESTIC_KEYWORDS)
        print(f"[TripRoute] 🗺️ is_domestic: {is_domestic} (destination: '{destination}')")

        # ✅ 명시적 travel_style이 있으면 LLM 파싱 스킵
        if explicit_travel_style and explicit_travel_style in valid_styles:
            print(f"[TripRoute] ✅ 명시적 travel_style 사용: '{explicit_travel_style}' (LLM 파싱 스킵)")
            all_styles = [explicit_travel_style] + [s for s in secondary_styles if s in valid_styles]
            parsed_data = {
                'origin': origin,
                'destination': destination,
                'start_date': start_date,
                'end_date': end_date,
                'party_size': int(party_size),
                'budget_per_person': {'amount': int(budget), 'currency': 'KRW'},
                'is_domestic': is_domestic,
                'travel_style': explicit_travel_style,
                'interests': all_styles,
                'preferred_style_text': preferred_style_text,
            }
        else:
            # ✅ 기존 LLM 파싱 (명시적 스타일 없을 때 fallback)
            user_request = f"""
출발지: {origin}
도착지: {destination}
여행 기간: {start_date} ~ {end_date}
인원: {party_size}명
1인 예산: {budget}원
여행 스타일: {preferred_style_text}
"""
            print(f"[TripRoute] 📝 LLM 파싱 진행:\n{user_request}")
            parsed_data = llm_service.parse_user_request(user_request)
            parsed_data['start_date'] = start_date
            parsed_data['end_date'] = end_date
            parsed_data['party_size'] = int(party_size)
            parsed_data['budget_per_person'] = {'amount': int(budget), 'currency': 'KRW'}
            parsed_data['is_domestic'] = is_domestic  # 키워드 판별값으로 덮어쓰기
            if origin and '(' in origin:
                parsed_data['origin'] = origin

        request_data = {
            'preferred_style': parsed_data.get('travel_style', 'sightseeing'),
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

        start_date_raw = data.get('start_date')
        end_date_raw = data.get('end_date')

        start_date = None
        end_date = None

        if start_date_raw:
            try:
                if 'T' in str(start_date_raw):
                    start_date = datetime.fromisoformat(start_date_raw.replace('Z', '+00:00')).date()
                else:
                    start_date = datetime.strptime(start_date_raw, '%Y-%m-%d').date()
                print(f"[SAVE] ✅ start_date converted: {start_date}")
            except ValueError as e:
                print(f"[SAVE] ❌ start_date conversion failed: {e}")

            if end_date_raw:
                try:
                    if 'T' in str(end_date_raw):
                        end_date = datetime.fromisoformat(end_date_raw.replace('Z', '+00:00')).date()
                    else: 
                        end_date = datetime.strptime(end_date_raw, '%Y-%m-%d').date()
                    print(f"[SAVE] ✅ end_date converted: {end_date}")
                except ValueError as e:
                    print(f"[SAVE] ❌ end_date conversion failed: {e}")

        new_trip = Trip(
            user_id=int(user_id),
            trip_summary=data.get('trip_summary'),
            destination=data.get('destination'),
            start_date=start_date,
            end_date=end_date,
            head_count=data.get('pax') or data.get('party_size') or data.get('head_count') or 2,
            total_cost=data.get('budget') or data.get('total_cost'),
            schedule_json=data.get('schedule'),
            raw_data_json=data.get('raw_data')
        )

        db.session.add(new_trip)
        db.session.commit()

        return jsonify({
            "message": "여행 계획이 저장되었습니다.",
            "trip_id": new_trip.uuid
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
                "id": trip.uuid,
                "trip_summary": trip.trip_summary,
                "destination": trip.destination,
                "start_date": trip.start_date.isoformat() if trip.start_date else None,
                "end_date": trip.end_date.isoformat() if trip.end_date else None,
                "pax": trip.head_count,
                "party_size": trip.head_count,
                "budget": trip.total_cost,
                "total_cost": trip.total_cost,
                "schedule": trip.schedule_json,
                "raw_data": trip.raw_data_json,
                "created_at": trip.created_at.isoformat()
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"[TripRoute] ❌ Error in /saved: {e}")
        return jsonify({"error": str(e)}), 500

@bp.get("/saved/<string:trip_uuid>")
@jwt_required()
def get_trip_detail(trip_uuid):
    """특정 여행 상세 조회"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.filter_by(uuid=trip_uuid, user_id=int(user_id)).first()

        if not trip:
            return jsonify({"error": "Trip not found"}), 404

        return jsonify({
            "id": trip.uuid,
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
        print(f"[TripRoute] ❌ Error in /saved/<uuid>: {e}")
        return jsonify({"error": str(e)}), 500

@bp.delete("/saved/<string:trip_uuid>")
@jwt_required()
def delete_trip(trip_uuid):
    """여행 계획 삭제"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.filter_by(uuid=trip_uuid, user_id=int(user_id)).first()

        if not trip:
            return jsonify({"error": "Trip not found"}), 404

        db.session.delete(trip)
        db.session.commit()

        return jsonify({"message": "여행 계획이 삭제되었습니다."}), 200

    except Exception as e:
        db.session.rollback()
        print(f"[TripRoute] ❌ Error in /delete: {e}")
        return jsonify({"error": str(e)}), 500

@bp.patch("/saved/<string:trip_uuid>")
@jwt_required()
def update_trip(trip_uuid):
    """여행 계획 수정"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        trip = Trip.query.filter_by(uuid=trip_uuid, user_id=int(user_id)).first()
        
        if not trip:
            return jsonify({"error": "Trip not found"}), 404
        
        # ✅ 일정 업데이트
        if 'schedule_json' in data:
            trip.schedule_json = data['schedule_json']
        if 'schedule' in data:
            trip.schedule_json = data['schedule']
            
        # 기타 필드 업데이트
        if 'trip_summary' in data:
            trip.trip_summary = data['trip_summary']
        if 'total_cost' in data:
            trip.total_cost = data['total_cost']
            
        trip.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({"message": "여행 계획이 수정되었습니다."}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[TripRoute] ❌ Error in /update: {e}")
        return jsonify({"error": str(e)}), 500
    