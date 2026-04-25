# backend/tripmind_api/models.py
import uuid as _uuid
from datetime import datetime
from .extensions import db
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(400), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    trips = db.relationship("Trip", back_populates="user", cascade="all, delete-orphan")

    profile_image = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Trip(db.Model):
    __tablename__ = "trips"
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(_uuid.uuid4()), server_default=db.text("(UUID())"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    title = db.Column(db.String(200), nullable=False, default="나만의 여행")
    origin = db.Column(db.String(100), nullable=True)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    head_count = db.Column(db.Integer, default=1)
    preferred_style_text = db.Column(db.Text, nullable=True)
    trip_summary = db.Column(db.String(500), nullable=True)
    total_cost = db.Column(db.Integer, nullable=True)
    
    schedule_json = db.Column(JSON, nullable=True) 
    cost_chart_json = db.Column(JSON, nullable=True)
    raw_data_json = db.Column(JSON, nullable=True) 
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now(), nullable=True)

    user = db.relationship("User", back_populates="trips")