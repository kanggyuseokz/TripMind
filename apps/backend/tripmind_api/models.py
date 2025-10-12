from . import db
from datetime import datetime

# SQLAlchemy의 db.Model을 상속받아 데이터베이스 테이블의 구조를 정의합니다.

class Trip(db.Model):
    """
    생성된 여행 계획 정보를 저장하는 테이블입니다.
    """
    __tablename__ = 'trips'  # 데이터베이스에 생성될 테이블 이름

    id = db.Column(db.Integer, primary_key=True)  # 고유 ID (자동 증가)
    
    # --- LLM 파싱 기본 정보 ---
    origin = db.Column(db.String(100), nullable=True)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    party_size = db.Column(db.Integer, nullable=True)
    
    # --- 계산된 정보 ---
    total_cost = db.Column(db.Float, nullable=True)
    
    # --- 복잡한 구조의 데이터 (JSON 문자열로 저장) ---
    # 비용 분석, 일정 등은 가변적인 구조를 가지므로 Text 타입으로 저장합니다.
    cost_breakdown_json = db.Column(db.Text, nullable=True)
    schedule_json = db.Column(db.Text, nullable=True)
    
    # --- 메타 정보 ---
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # 생성 시각 (자동 기록)

    # (향후 확장) 사용자(User) 모델과의 관계 설정
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # user = db.relationship('User', back_populates='trips')

    def __repr__(self):
        return f"<Trip {self.id}: {self.origin} to {self.destination}>"

# (향후 확장) 사용자 모델 예시
# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     preferred_style = db.Column(db.String(50), nullable=True, default='관광') # '휴식', '맛집' 등
#     trips = db.relationship('Trip', back_populates='user', lazy=True)

