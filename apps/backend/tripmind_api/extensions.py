# backend/tripmind_api/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# 1. 데이터베이스 ORM
db = SQLAlchemy()

# 2. DB 마이그레이션 관리 도구
migrate = Migrate()

# 3. JWT 토큰 인증 관리 도구
jwt = JWTManager()

# 4. CORS (Cross-Origin Resource Sharing) 보안 설정 도구
cors = CORS()