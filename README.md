# 🌏 TripMind AI 여행 플래너 ✈️

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?logo=databricks&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI_API-412991?logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Gemini-4285F4?logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/RapidAPI-0066CC?logo=api&logoColor=white" />
  <img src="https://img.shields.io/badge/JWT-000000?logo=jsonwebtokens&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/kanggyuseokz/TripMind?style=flat-square" />
  <img src="https://img.shields.io/github/stars/kanggyuseokz/TripMind?style=flat-square" />
  <img src="https://img.shields.io/github/forks/kanggyuseokz/TripMind?style=flat-square" />
  <img src="https://img.shields.io/github/issues/kanggyuseokz/TripMind?style=flat-square" />
</p>

---

**TripMind**는 사용자의 간단한 자연어 요청만으로 **항공, 숙소, 현지 활동을 포함한 최적의 맞춤형 여행 계획과 예산**을 자동으로 생성해주는 **LLM 기반 AI 여행 계획 서비스**입니다.

> 🎯 **"도쿄 3박 4일 맛집 여행"** 같은 한 문장으로 완벽한 여행 일정을 만들어보세요!

---

## 🚀 데모

### 📹 시연 영상
<!-- 여기에 데모 영상 링크나 GIF 추가 -->

### 🖼️ 스크린샷
<!-- 주요 화면 스크린샷들 -->

### 🔗 라이브 데모
- **웹사이트**: [tripmind.demo.com](https://tripmind.demo.com) (예시)
- **API 문서**: [api.tripmind.demo.com/docs](https://api.tripmind.demo.com/docs) (예시)

---

## ✨ 프로젝트 목표

복잡하고 시간이 많이 소요되는 여행 계획 과정을 AI를 통해 단순화하고, 사용자에게 다음과 같은 핵심 가치를 제공합니다.

- 🚀 **간편함**: `"도쿄 3박 4일 맛집 여행"`과 같은 간단한 문장만으로 전체 여행 계획 수립  
- 🎨 **개인화**: 사용자의 예산, 여행 스타일(휴식·관광·맛집 등)을 고려한 맞춤형 일정 추천  
- 🗺️ **최적화**: 지도 API를 활용한 동선 최적화로 시간과 비용 낭비 최소화  
- 📊 **투명성**: 항공, 숙소, 예상 식비 및 활동비를 포함한 전체 경비 분석을 통한 투명한 예산 관리  

---

## 🏆 주요 특징

### 🤖 **AI 기반 스마트 플래닝**
- **자연어 처리**: Google Gemini API로 사용자 의도 정확 파악
- **실시간 데이터**: Agoda, Booking.com 등 실시간 항공편·숙소 정보
- **동적 일정 조정**: 날씨, 교통, 예산에 따른 자동 일정 최적화

### 💰 **통합 예산 관리**
- 실시간 환율 적용 (한국수출입은행 API)
- 항공료, 숙박비, 식비, 교통비 종합 계산
- 예산 초과 시 대안 옵션 자동 제안

### 🌍 **글로벌 지원**
- 전세계 주요 여행지 지원
- 다국어 POI(관심 지점) 정보
- 현지 문화 및 팁 제공

### 📱 **사용자 경험**
- 직관적인 React 기반 웹 인터페이스
- 모바일 최적화된 반응형 디자인
- 다크모드 지원
- 실시간 검색 결과

---

## 🛠️ 기술 아키텍처

### 📐 **시스템 구조**
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Frontend  │ -> │   Backend    │ -> │ MCP Server  │
│   (React)   │    │   (Flask)    │    │ (FastAPI)   │
└─────────────┘    └──────────────┘    └─────────────┘
                            │                   │
                            v                   v
                    ┌──────────────┐    ┌─────────────┐
                    │   Database   │    │ External    │
                    │   (MySQL)    │    │   APIs      │
                    └──────────────┘    └─────────────┘
```

### 🔧 **기술 스택**

#### **프론트엔드**
- **React 18** - 컴포넌트 기반 UI
- **React Router** - SPA 라우팅
- **TailwindCSS** - 유틸리티 기반 스타일링
- **Axios** - HTTP 클라이언트

#### **백엔드**
- **Flask 2.3+** - 웹 프레임워크
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - JWT 인증
- **Flask-CORS** - CORS 처리

#### **MCP 서버**
- **FastAPI** - 비동기 API 프레임워크
- **asyncio** - 비동기 처리
- **httpx** - 비동기 HTTP 클라이언트
- **Pydantic** - 데이터 검증

#### **AI & 외부 API**
- **Google Gemini API** - LLM
- **RapidAPI (Agoda)** - 항공편·숙소
- **한국수출입은행 API** - 환율
- **OpenWeatherMap** - 날씨

#### **데이터베이스 & 인프라**
- **MySQL 8.0** - 메인 데이터베이스
- **Redis** (예정) - 캐싱
- **Docker** (예정) - 컨테이너화
- **AWS** (예정) - 클라우드 배포

---

## 🏗️ 프로젝트 구조

```
TripMind/
├── apps/
│   ├── frontend/          # React 프론트엔드
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── contexts/
│   │   │   └── styles/
│   │   └── public/
│   ├── backend/           # Flask 백엔드
│   │   ├── tripmind_api/
│   │   │   ├── routes/
│   │   │   ├── services/
│   │   │   ├── models/
│   │   │   └── config.py
│   │   └── requirements.txt
│   └── mcp/              # FastAPI MCP 서버
│       ├── mcp_server/
│       │   ├── clients/
│       │   ├── services/
│       │   └── main.py
│       └── requirements.txt
├── docs/                 # 프로젝트 문서
├── tests/               # 테스트 파일
└── README.md
```

---

## 🚀 빠른 시작

### 📋 사전 요구사항

- **Python 3.11+**
- **Node.js 18+**
- **MySQL 8.0+**
- **Git**

### 📝 API 키 준비

다음 서비스들의 API 키가 필요합니다:

1. **Google Gemini API** - [ai.google.dev](https://ai.google.dev)
2. **RapidAPI** - [rapidapi.com](https://rapidapi.com)
3. **한국수출입은행** - [www.koreaexim.go.kr](https://www.koreaexim.go.kr)

### ⚙️ 설치 및 실행

#### 1. 저장소 클론 및 환경 설정
```bash
# 저장소 클론
git clone https://github.com/kanggyuseokz/TripMind.git
cd TripMind

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 2. 환경 변수 설정
```bash
# backend/.env 파일 생성
cd apps/backend
cp .env.example .env
# .env 파일에 API 키 입력

# mcp/.env 파일 생성  
cd ../mcp
cp .env.example .env
# .env 파일에 API 키 입력
```

#### 3. 의존성 설치
```bash
# 백엔드 의존성 설치
cd apps/backend
pip install -r requirements.txt

# MCP 서버 의존성 설치
cd ../mcp
pip install -r requirements.txt

# 프론트엔드 의존성 설치
cd ../frontend
npm install
```

#### 4. 데이터베이스 설정
```bash
# MySQL 접속 후 데이터베이스 생성
CREATE DATABASE tripmind CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 테이블 생성 (백엔드 서버 최초 실행시 자동 생성)
cd apps/backend
flask db upgrade
```

#### 5. 서버 실행

**각각 별도의 터미널에서 실행하세요:**

```bash
# 터미널 1: 백엔드 서버 (포트 8080)
cd apps/backend
flask run --port 8080

# 터미널 2: MCP 서버 (포트 7000) 
cd apps/mcp
uvicorn mcp_server.main:app --reload --port 7000

# 터미널 3: 프론트엔드 서버 (포트 3000)
cd apps/frontend
npm start
```

#### 6. 접속 확인
- **웹 애플리케이션**: http://localhost:3000
- **백엔드 API**: http://localhost:8080
- **MCP API 문서**: http://localhost:7000/docs

---

## 📚 API 문서

### 🔐 인증 API
```http
POST /api/auth/login      # 로그인
POST /api/auth/register   # 회원가입
POST /api/auth/refresh    # 토큰 갱신
GET  /api/auth/profile    # 프로필 조회
```

### 🛫 여행 계획 API
```http
POST /api/trips/search    # 여행 검색
GET  /api/trips/{id}      # 여행 계획 조회
POST /api/trips/{id}/save # 여행 계획 저장
```

### 💱 환율 API
```http
GET  /api/rates/convert   # 환율 조회
```

### 📋 MCP API
```http
POST /mcp/search          # 통합 검색
GET  /mcp/flights         # 항공편 검색
GET  /mcp/hotels          # 숙소 검색
GET  /mcp/weather         # 날씨 조회
```

자세한 API 문서는 서버 실행 후 `/docs` 엔드포인트에서 확인하실 수 있습니다.

---

## 🧪 테스트

### 단위 테스트 실행
```bash
# 백엔드 테스트
cd apps/backend
pytest tests/

# MCP 서버 테스트
cd apps/mcp  
pytest tests/

# 프론트엔드 테스트
cd apps/frontend
npm test
```

### API 테스트
```bash
# Postman Collection 사용
# docs/postman/ 폴더의 컬렉션 파일 import
```

---

## 📊 성능 및 모니터링

### 🔍 로깅
- 구조화된 JSON 로깅
- 요청/응답 추적
- 에러 상세 기록

### 📈 성능 지표
- API 응답 시간: < 2초
- 동시 접속자: 100명 이상 지원
- 캐시 적중률: 80% 이상 목표

---

## 🌍 배포

### 🐳 Docker 배포 (예정)
```bash
# 전체 스택 실행
docker-compose up -d

# 개별 서비스 실행
docker-compose up backend mcp frontend
```

### ☁️ AWS 배포 아키텍처 (예정)
- **Frontend**: S3 + CloudFront
- **Backend**: ECS Fargate
- **Database**: RDS (MySQL)
- **Cache**: ElastiCache (Redis)
- **Load Balancer**: ALB

---

## 🤝 기여하기

### 🐛 버그 리포트
이슈가 있으시면 [GitHub Issues](https://github.com/kanggyuseokz/TripMind/issues)에 리포트해주세요.

### 💡 기능 제안
새로운 기능 아이디어가 있으시면 [Discussions](https://github.com/kanggyuseokz/TripMind/discussions)에서 논의해주세요.

### 🔧 개발 참여
1. Fork 후 브랜치 생성
2. 코드 작성 및 테스트
3. Pull Request 생성

### 📝 코딩 컨벤션
- **Python**: PEP 8 준수
- **JavaScript**: ESLint + Prettier
- **Commit**: Conventional Commits

---

### 🧑‍💻 개발자
- **강규석** - [@kanggyuseokz](https://github.com/kanggyuseokz)
  - 풀스택 개발, AI 통합, 아키텍처 설계


---

## 📈 로드맵

### 🎯 **v1.0 (현재)**
- [x] 기본 여행 계획 생성
- [x] 항공편·숙소 검색  
- [x] 예산 계산
- [x] 웹 인터페이스

### 🚀 **v1.1** (예정)
- [ ] 모바일 앱 (React Native)
- [ ] 소셜 로그인 (Google, Kakao)
- [ ] 여행 일정 공유 기능
- [ ] 즐겨찾기 및 위시리스트

### 🌟 **v2.0** (예정)
- [ ] 실시간 채팅 지원
- [ ] AI 여행 가이드
- [ ] 오프라인 지도
- [ ] 다국어 지원 (영어, 일본어, 중국어)

---

이 프로젝트는 다음 오픈소스 프로젝트들의 도움을 받았습니다:

- [Flask](https://flask.palletsprojects.com/) - 웹 프레임워크
- [FastAPI](https://fastapi.tiangolo.com/) - API 프레임워크  
- [React](https://reactjs.org/) - 프론트엔드 라이브러리
- [Google Gemini](https://ai.google.dev/) - AI 모델

---

<p align="center">
  <strong>🌟 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요! 🌟</strong>
</p>

<p align="center">
  Made with ❤️ by <a href="https://github.com/kanggyuseokz">kanggyuseokz</a>
</p>