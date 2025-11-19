# backend/tripmind_api/services/auth_service.py
from ..extensions import db
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import re

class AuthService:
    
    def register_user(self, username, email, password):
        """신규 사용자 등록 로직"""
        
        # 1. 백엔드 유효성 검사
        if not username or not email or not password:
            raise ValueError("사용자 이름, 이메일, 비밀번호는 필수입니다.")
            
        if len(password) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
             raise ValueError("올바른 이메일 형식이 아닙니다.")

        # 2. 중복 사용자 검사
        if User.query.filter_by(email=email).first():
            raise ValueError("이미 사용 중인 이메일입니다.")
        if User.query.filter_by(username=username).first():
            raise ValueError("이미 사용 중인 사용자 이름입니다.")
            
        # 3. 비밀번호 해시
        password_hash = generate_password_hash(password)
        
        # 4. 새 사용자 객체 생성 및 DB 저장
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user

    def login_user(self, email, password):
        """사용자 로그인 및 토큰 발급 로직"""
        
        # 1. 사용자 찾기
        user = User.query.filter_by(email=email).first()
        
        # 2. 비밀번호 검증
        if user and check_password_hash(user.password_hash, password):
            # 3. JWT 토큰 생성
            access_token = create_access_token(identity=user.id) 
            
            # 💡 [개선] 프론트엔드에서 활용하기 쉽도록 사용자 상세 정보를 함께 반환
            return {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }
        else:
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

# 싱글톤 인스턴스
auth_service_instance = AuthService()