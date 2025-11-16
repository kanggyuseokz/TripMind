# backend/tripmind_api/extensions.py
from flask_sqlalchemy import SQLAlchemy

# 1. SQLAlchemy 인스턴스를 여기서 생성합니다.
# 이 'db' 객체를 __init__.py와 models.py에서 공통으로 import하여 사용합니다.
db = SQLAlchemy()