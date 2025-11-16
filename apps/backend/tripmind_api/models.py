# backend/tripmind_api/models.py
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import JSON 

# SQLAlchemy 2.0 스타일의 Base 클래스 정의
class Base(DeclarativeBase):
    pass

class User(Base):
    """
    사용자 정보 테이블
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

class Trip(Base):
    """
    생성된 여행 계획의 요약 정보 테이블
    """
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 1. 여행 기본 정보
    origin = Column(String(100), nullable=True)
    destination = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    party_size = Column(Integer, default=1)
    preferred_style_text = Column(Text, nullable=True)
    
    # 2. 생성된 여행 요약 정보
    trip_summary = Column(String(500), nullable=True)
    total_cost = Column(Float, nullable=True)
    
    # 💡 3. JSON 타입을 네이티브 MySQL JSON 타입으로 변경
    # SQLAlchemy가 자동으로 Python dict/list <-> JSON 변환을 처리합니다.
    schedule_json = Column(JSON, nullable=True) 
    cost_chart_json = Column(JSON, nullable=True)
    raw_data_json = Column(JSON, nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="trips")

    def __repr__(self):
        return f'<Trip {self.id}: {self.destination}>'
        
    # --- 💡 4. Helper Methods에서 json.dumps/loads 제거 ---
    
    def set_schedule(self, schedule_data: list):
        # SQLAlchemy가 알아서 JSON으로 변환하므로, Python 리스트를 그대로 할당합니다.
        self.schedule_json = schedule_data
        
    def get_schedule(self) -> list:
        # SQLAlchemy가 알아서 Python 리스트로 변환하므로, 그대로 반환합니다.
        return self.schedule_json or []

    def set_raw_data(self, raw_data: dict):
        self.raw_data_json = raw_data

    def get_raw_data(self) -> dict:
        return self.raw_data_json or {}
        
    def set_cost_chart(self, chart_data: list):
        self.cost_chart_json = chart_data
        
    def get_cost_chart(self) -> list:
        return self.cost_chart_json or []

# --- (참고) 데이터베이스 연결 및 테이블 생성 ---
# 이 코드는 메인 app.py 또는 config.py에서 실행되어야 합니다.
# 
# from .config import settings 
# 
# # 💡 5. MySQL 8.x 연결 문자열 예시로 변경
# # (settings.DB_URL이 "mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>" 형식이 되어야 함)
# # (예: "mysql+pymysql://root:password@localhost:3306/tripmind_db")
# # (MySQL을 사용하려면 'pymysql' 라이브러리 설치가 필요합니다: pip install pymysql)
# 
# SQLALCHEMY_DATABASE_URI = settings.DB_URL # 👈 settings.DATABASE_URL -> settings.DB_URL
# engine = create_engine(SQLALCHEMY_DATABASE_URI)
# 
# def init_db():
#     # Base.metadata.drop_all(bind=engine) # 개발 중 테이블 리셋 시 사용
#     Base.metadata.create_all(bind=engine)
# 
# if __name__ == "__main__":
#     print("데이터베이스 테이블을 생성합니다...")
#     init_db()
#     print("테이블 생성 완료.")
# ---