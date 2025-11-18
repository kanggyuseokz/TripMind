# backend/tripmind_api/routes/auth_route.py
from flask import Blueprint, request, jsonify
from ..services.auth_service import auth_service_instance
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("auth", __name__)

@bp.post("/register")
def register():
    """회원가입 엔드포인트"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        new_user = auth_service_instance.register_user(username, email, password)
        
        return jsonify({
            "message": "회원가입 성공!",
            "user": {"id": new_user.id, "username": new_user.username}
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"서버 오류 발생: {e}"}), 500

@bp.post("/login")
def login():
    """로그인 엔드포인트"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        token_data = auth_service_instance.login_user(email, password)
        
        return jsonify(token_data), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 401 # 401 Unauthorized
    except Exception as e:
        return jsonify({"error": f"서버 오류 발생: {e}"}), 500

@bp.get("/protected")
@jwt_required() # 👈 이 엔드포인트는 유효한 토큰이 필요함
def protected():
    """(테스트용) 인증이 필요한 엔드포인트"""
    # 토큰에서 사용자 ID를 가져옵니다.
    current_user_id = get_jwt_identity()
    return jsonify(logged_in_as=current_user_id), 200