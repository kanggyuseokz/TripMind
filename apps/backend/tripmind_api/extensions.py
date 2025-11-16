# backend/tripmind_api/extensions.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .config import settings
from .models import Base # 👈 models.py에서 Base 클래스를 가져옵니다.

# 1. DB 엔진 생성 (MySQL 8.x)
# (settings.DB_URL이 "mysql+pymysql://user:pass@host:port/dbname" 형식이어야 함)
engine = create_engine(settings.DB_URL)

# 2. DB 세션 생성 (가장 중요!)
# ScopedSession은 Flask의 각 웹 요청마다 고유한 세션을 보장해줍니다.
# (이것 없이 세션을 전역 변수로 쓰면 데이터가 꼬입니다)
session_factory = sessionmaker(bind=engine)
db_session = scoped_session(session_factory)

def init_db():
    """
    app.py가 서버를 시작할 때 호출할 함수입니다.
    models.py에 정의된 모든 테이블을 DB에 생성합니다.
    """
    print("데이터베이스 테이블을 생성합니다...")
    # 3. 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("테이블 생성 완료.")