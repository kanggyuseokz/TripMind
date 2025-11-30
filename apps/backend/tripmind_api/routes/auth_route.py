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
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"서버 오류 발생: {e}"}), 500
    
@bp.post("/forgot-password")
def forgot_password():
    """임시 비밀번호 발급 요청"""
    try:
        data = request.get_json()
        email = data.get("email")
        
        if not email:
            return jsonify({"error": "이메일을 입력해주세요."}), 400

        temp_pw = auth_service_instance.reset_password_to_temp(email)
        
        return jsonify({
            "message": "임시 비밀번호가 발급되었습니다.",
            "temp_password": temp_pw 
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"서버 오류: {e}"}), 500
    
@bp.get("/protected")
@jwt_required()
def protected():
    """(테스트용) 인증이 필요한 엔드포인트"""
    current_user_id = get_jwt_identity()
    return jsonify(logged_in_as=current_user_id), 200


@bp.get("/profile")
@jwt_required()
def get_profile():
    """현재 로그인한 사용자의 프로필 조회"""
    try:
        user_id = get_jwt_identity()
        profile = auth_service_instance.get_user_profile(user_id)
        
        return jsonify(profile), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"서버 오류: {e}"}), 500


@bp.put("/profile")
@jwt_required()
def update_profile():
    """현재 로그인한 사용자의 프로필 수정"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "수정할 데이터가 없습니다."}), 400
        
        username = data.get('username')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        updated_user = auth_service_instance.update_user_profile(
            user_id=user_id,
            username=username,
            current_password=current_password,
            new_password=new_password
        )
        
        return jsonify({
            "message": "프로필이 성공적으로 수정되었습니다.",
            "user": {
                "id": updated_user.id,
                "username": updated_user.username,
                "email": updated_user.email,
                "profile_image": updated_user.profile_image
            }
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"서버 오류: {e}"}), 500


# ✅ [NEW] 프로필 이미지 업로드
@bp.post("/profile/image")
@jwt_required()
def upload_profile_image():
    """프로필 이미지 업로드"""
    try:
        user_id = get_jwt_identity()
        
        # 파일 체크
        if 'profile_image' not in request.files:
            return jsonify({"error": "파일이 없습니다."}), 400
        
        file = request.files['profile_image']
        
        if file.filename == '':
            return jsonify({"error": "파일이 선택되지 않았습니다."}), 400
        
        # 이미지 업로드
        image_url = auth_service_instance.upload_profile_image(user_id, file)
        
        return jsonify({
            "message": "프로필 이미지가 업로드되었습니다.",
            "image_url": image_url
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"이미지 업로드 에러: {e}")
        return jsonify({"error": f"서버 오류: {str(e)}"}), 500