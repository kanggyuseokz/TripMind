# backend/tripmind_api/models.py
from datetime import datetime
# 💡 1. extensions.py에서 공용 'db' 객체를 임포트합니다.
from .extensions import db
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.sql import func

# 💡 2. 'DeclarativeBase' 대신 'db.Model'을 Base로 사용합니다.
class User(db.Model):
    __tablename__ = "users"
    # 💡 3. Column, String 등 모든 SQLAlchemy 타입을 'db.' 접두어로 변경합니다.
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
    
    origin = db.Column(db.String(100), nullable=True)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    party_size = db.Column(db.Integer, default=1)
    preferred_style_text = db.Column(db.Text, nullable=True)
    
    trip_summary = db.Column(db.String(500), nullable=True)
    total_cost = db.Column(db.Float, nullable=True)
    
    # MySQL 8.x의 네이티브 JSON 타입 사용
    schedule_json = db.Column(JSON, nullable=True) 
    cost_chart_json = db.Column(JSON, nullable=True)
    raw_data_json = db.Column(JSON, nullable=True) 
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    user = db.relationship("User", back_populates="trips")

    # 💡 4. set/get 헬퍼는 SQLAlchemy가 JSON을 자동 변환해주므로 그대로 둡니다.
    def set_schedule(self, schedule_data: list):
        self.schedule_json = schedule_data
    
    def get_schedule(self) -> list:
        return self.schedule_json or []

    def set_raw_data(self, raw_data: dict):
        self.raw_data_json = raw_data

    def get_raw_data(self) -> dict:
        return self.raw_data_json or {}
        
    def set_cost_chart(self, chart_data: list):
        self.cost_chart_json = chart_data
        
    def get_cost_chart(self) -> list:
        return self.cost_chart_json or []