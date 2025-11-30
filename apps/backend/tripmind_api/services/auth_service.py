# backend/tripmind_api/services/auth_service.py
from ..extensions import db
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token
from PIL import Image
import re, secrets, string, os

class AuthService:
    
    # 허용된 이미지 확장자
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 3 * 1024 * 1024  # 3MB
    PROFILE_IMAGE_SIZE = (200, 200)  # 리사이징 크기
    
    def allowed_file(self, filename):
        """파일 확장자 검증"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def register_user(self, username, email, password):
        """신규 사용자 등록 로직"""
        
        if not username or not email or not password:
            raise ValueError("사용자 이름, 이메일, 비밀번호는 필수입니다.")
        if len(password) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
             raise ValueError("올바른 이메일 형식이 아닙니다.")
        if User.query.filter_by(email=email).first():
            raise ValueError("이미 사용 중인 이메일입니다.")
        if User.query.filter_by(username=username).first():
            raise ValueError("이미 사용 중인 사용자 이름입니다.")
        password_hash = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        return new_user
            
    def login_user(self, email, password):
        """사용자 로그인 및 토큰 발급 로직"""
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=str(user.id))
            
            return {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile_image": user.profile_image
                }
            }
        else:
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")
        
    def reset_password_to_temp(self, email):
        """임시 비밀번호 발급"""
        user = User.query.filter_by(email=email).first()
        
        if not user:
            raise ValueError("해당 이메일로 가입된 계정이 없습니다.")

        chars = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(chars) for _ in range(8))

        user.password_hash = generate_password_hash(temp_password)
        db.session.commit()

        return temp_password

    def get_user_profile(self, user_id):
        """사용자 프로필 조회"""
        user = User.query.get(int(user_id))
        
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "profile_image": user.profile_image,
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }

    def update_user_profile(self, user_id, username=None, current_password=None, new_password=None):
        """사용자 프로필 수정"""
        user = User.query.get(int(user_id))
        
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")
        
        # 사용자 이름 변경
        if username and username != user.username:
            existing = User.query.filter_by(username=username).first()
            if existing and existing.id != user.id:
                raise ValueError("이미 사용 중인 사용자 이름입니다.")
            user.username = username
        
        # 비밀번호 변경
        if new_password:
            if not current_password:
                raise ValueError("현재 비밀번호를 입력해주세요.")
            
            if not check_password_hash(user.password_hash, current_password):
                raise ValueError("현재 비밀번호가 올바르지 않습니다.")
            
            if len(new_password) < 8:
                raise ValueError("새 비밀번호는 8자 이상이어야 합니다.")
            
            user.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        return user

    # ✅ [NEW] 프로필 이미지 업로드
    def upload_profile_image(self, user_id, file, upload_folder='static/profile_images'):
        """프로필 이미지 업로드 및 리사이징"""
        user = User.query.get(int(user_id))
        
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")
        
        # 1. 파일 검증
        if not file:
            raise ValueError("파일이 없습니다.")
        
        if not self.allowed_file(file.filename):
            raise ValueError("지원하지 않는 파일 형식입니다. (png, jpg, jpeg, gif, webp만 가능)")
        
        # 2. 파일 크기 검증 (3MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError("파일 크기는 3MB 이하여야 합니다.")
        
        # 3. 파일명 생성 (보안)
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"user_{user_id}_{secrets.token_hex(8)}.{ext}"
        
        # 4. 저장 경로 생성
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        
        # 5. 이미지 리사이징 (200x200)
        try:
            image = Image.open(file)
            
            # RGBA -> RGB 변환 (PNG 투명 배경 처리)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # 비율 유지하며 리사이징
            image.thumbnail(self.PROFILE_IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            # 정사각형으로 만들기 (crop)
            width, height = image.size
            if width != height:
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                image = image.crop((left, top, left + size, top + size))
            
            # 저장
            image.save(filepath, quality=85, optimize=True)
            
        except Exception as e:
            raise ValueError(f"이미지 처리 실패: {str(e)}")
        
        # 6. 이전 이미지 삭제 (선택)
        if user.profile_image:
            old_path = user.profile_image.lstrip('/')
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except:
                    pass
        
        # 7. DB 업데이트
        user.profile_image = f"/static/profile_images/{filename}"
        db.session.commit()
        
        return user.profile_image

# 싱글톤 인스턴스
auth_service_instance = AuthService()