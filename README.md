# TripMind — AI 여행 플래너

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Gemini-4285F4?logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/JWT-000000?logo=jsonwebtokens&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/kanggyuseokz/TripMind?style=flat-square" />
  <img src="https://img.shields.io/github/stars/kanggyuseokz/TripMind?style=flat-square" />
  <img src="https://img.shields.io/github/forks/kanggyuseokz/TripMind?style=flat-square" />
</p>

---

**TripMind**는 자연어 한 문장으로 항공·숙소·현지 일정을 포함한 맞춤형 여행 계획과 예산을 자동 생성하는 **LLM 기반 AI 여행 계획 서비스**입니다.

> "도쿄 3박 4일 맛집 여행" 같은 한 문장으로 완벽한 여행 일정을 만들어보세요.

---

## 주요 기능

- **AI 여행 계획 생성** — Google Gemini 기반 자연어 처리로 출발지·목적지·예산·여행 스타일을 반영한 일정 자동 생성
- **실시간 항공·숙소 검색** — Agoda RapidAPI를 통한 실시간 항공편·숙소 데이터 조회
- **예산 분석** — 항공료·숙박비·식비·교통비 종합 계산 및 1인당 예산 표시
- **일정 편집** — 저장된 여행 계획의 일정을 직접 수정·저장
- **여행 보관함** — 생성한 여행 계획 저장·조회·삭제

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| **프론트엔드** | React 19, React Router v7, Tailwind CSS, Lucide React |
| **백엔드** | Flask, Flask-JWT-Extended, Flask-SQLAlchemy, Flask-CORS |
| **MCP 서버** | FastAPI, uvicorn, httpx |
| **AI** | Google Gemini API (google-generativeai) |
| **외부 API** | RapidAPI (Agoda), 한국수출입은행 환율, OpenWeatherMap |
| **데이터베이스** | MySQL 8.0, SQLAlchemy |
| **인증** | JWT (Flask-JWT-Extended) |

---

## 시스템 구조

```
Frontend (React:3000)
    │
    └─> Backend (Flask:8080)
            │
            └─> MCP Server (FastAPI:7000)
                    │
                    ├─ Agoda API (항공·숙소)
                    ├─ Gemini API (일정 생성)
                    ├─ 환율 API
                    └─ 날씨 API
```

---

## 프로젝트 구조

```
TripMind/
├── apps/
│   ├── frontend/               # React 프론트엔드
│   │   └── src/
│   │       ├── components/     # Header, Layout, Toast, ScheduleEditor 등
│   │       ├── pages/          # LandingPage, PlannerPage, ResultPage 등
│   │       └── utils/
│   ├── backend/                # Flask 백엔드
│   │   └── tripmind_api/
│   │       ├── routes/         # auth, trip, llm, map, rates
│   │       ├── services/
│   │       └── models.py
│   └── mcp/                    # FastAPI MCP 서버
│       └── mcp_server/
│           ├── routers/
│           ├── clients/        # agoda_client 등
│           └── services/
└── README.md
```

---

## 시작하기

### 사전 요구사항

- Python 3.11+
- Node.js 18+
- MySQL 8.0+

### API 키 준비

| 서비스 | 용도 |
|--------|------|
| [Google Gemini API](https://ai.google.dev) | AI 일정 생성 |
| [RapidAPI (Agoda)](https://rapidapi.com) | 항공·숙소 검색 |
| [한국수출입은행](https://www.koreaexim.go.kr) | 환율 조회 |
| OpenWeatherMap | 날씨 정보 |

### 설치 및 실행

```bash
# 1. 저장소 클론
git clone https://github.com/kanggyuseokz/TripMind.git
cd TripMind

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. 백엔드 의존성 설치 및 .env 설정
cd apps/backend
pip install -r requirements.txt
cp .env.example .env            # API 키 입력

# 4. MCP 서버 의존성 설치 및 .env 설정
cd ../mcp
pip install -r requirements.txt
cp .env.example .env            # API 키 입력

# 5. 프론트엔드 의존성 설치
cd ../frontend
npm install
```

### 서버 실행 (터미널 3개)

```bash
# 터미널 1: 백엔드 (포트 8080)
cd apps/backend
flask run --port 8080

# 터미널 2: MCP 서버 (포트 7000)
cd apps/mcp
uvicorn mcp_server.main:app --reload --port 7000

# 터미널 3: 프론트엔드 (포트 3000)
cd apps/frontend
npm start
```

접속: http://localhost:3000

---

## API 엔드포인트

### 인증
```
POST /api/auth/register   # 회원가입
POST /api/auth/login      # 로그인
```

### 여행 계획
```
POST /api/trip/plan              # 여행 계획 생성
GET  /api/trip/saved             # 저장된 여행 목록
GET  /api/trip/saved/:id         # 여행 상세 조회
PATCH /api/trip/saved/:id        # 일정 수정
DELETE /api/trip/saved/:id       # 여행 삭제
POST /api/trip/save              # 여행 저장
```

---

## 개발자

**강규석** — [@kanggyuseokz](https://github.com/kanggyuseokz)

---

<p align="center">
  이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!
</p>
