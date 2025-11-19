# backend/tripmind_api/models.py
from datetime import datetime
from .extensions import db
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    trips = db.relationship("Trip", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

class Trip(db.Model):
    __tablename__ = "trips"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # 여행 제목 (보관함 목록 표시용)
    title = db.Column(db.String(200), nullable=False, default="나만의 여행")
    
    origin = db.Column(db.String(100), nullable=True)
    destination = db.Column(db.String(100), nullable=False)
    
    # 날짜 정보 (Date 타입 사용)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    
    # 인원 수
    head_count = db.Column(db.Integer, default=1)
    
    preferred_style_text = db.Column(db.Text, nullable=True)
    
    # 요약 정보
    trip_summary = db.Column(db.String(500), nullable=True)
    total_cost = db.Column(db.Integer, nullable=True)
    
    # JSON 데이터 (일정표, 차트 데이터 등)
    # SQLAlchemy가 자동으로 Python 객체(list/dict) <-> JSON 변환을 처리함
    schedule_json = db.Column(JSON, nullable=True) 
    cost_chart_json = db.Column(JSON, nullable=True)
    raw_data_json = db.Column(JSON, nullable=True) 
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    user = db.relationship("User", back_populates="trips")