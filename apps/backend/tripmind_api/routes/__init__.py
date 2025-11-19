# backend/tripmind_api/routes/__init__.py

# 1. 각 라우터 파일에서 'bp' (Blueprint) 변수를 임포트합니다.
# 모듈 자체를 import 합니다.
from . import trip_route
from . import llm_route
from . import auth_route
from . import rates
from . import map_route

# 2. (선택사항) __all__을 정의하여 이 폴더가 노출하는 변수들을 명시합니다.
__all__ = [
    'trip_route',
    'llm_route',
    'auth_route',
    'map_route',
    'rates'
]