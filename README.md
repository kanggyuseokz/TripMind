# 🌍 TripMind AI 여행 플래너 ✈️

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?logo=databricks&logoColor=white" />
  <img src="https://img.shields.io/badge/HuggingFace-FFAE1A?logo=huggingface&logoColor=black" />
  <img src="https://img.shields.io/badge/OpenAI_API-412991?logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Maps-4285F4?logo=googlemaps&logoColor=white" />
  <img src="https://img.shields.io/badge/Kakao%20API-FFCD00?logo=kakao&logoColor=black" />
  <img src="https://img.shields.io/badge/OpenWeatherMap-F29C00?logo=cloudflare&logoColor=white" />
  <img src="https://img.shields.io/badge/AWS-232F3E?logo=amazonaws&logoColor=white" />
  <img src="https://img.shields.io/badge/Postman-FF6C37?logo=postman&logoColor=white" />
</p>

---

**TripMind**는 사용자의 간단한 자연어 요청만으로 **항공, 숙소, 현지 활동을 포함한 최적의 맞춤형 여행 계획과 예산**을 자동으로 생성해주는 **LLM 기반 AI 여행 계획 서비스**입니다.

---

## ✨ 프로젝트 목표

복잡하고 시간이 많이 소요되는 여행 계획 과정을 AI를 통해 단순화하고, 사용자에게 다음과 같은 핵심 가치를 제공합니다.

- 🚀 **간편함**: `"도쿄 3박 4일 맛집 여행"`과 같은 간단한 문장만으로 전체 여행 계획 수립  
- 🎨 **개인화**: 사용자의 예산, 여행 스타일(휴식·관광·맛집 등)을 고려한 맞춤형 일정 추천  
- 🗺️ **최적화**: 지도 API를 활용한 동선 최적화로 시간과 비용 낭비 최소화  
- 📊 **투명성**: 항공, 숙소, 예상 식비 및 활동비를 포함한 전체 경비 분석을 통한 투명한 예산 관리  

---

## 🏛️ 아키텍처 개요

TripMind는 **역할과 책임을 명확히 분리한 두 개의 독립 서버 구조**를 기반으로 하는  
**서비스 지향 아키텍처 (SOA: Service-Oriented Architecture)** 를 채택했습니다.

### 🧩 전체 구조
사용자 ➜ Backend (Flask) ➜ MCP (FastAPI) ➜ 외부 API (항공, 숙소, 날씨 등)

---

## 🖥️ 1. 백엔드 서버 (Backend - Flask)

**역할:** 프로젝트의 총괄 지휘자(Orchestrator).  
사용자 요청을 받아 전체 비즈니스 로직을 순차적으로 실행하고,  
최종 여행 계획을 조립하는 핵심 서버입니다.

### 🔧 주요 책임

| 모듈 | 역할 |
|------|------|
| 🧠 **LLMService** | 사용자 자연어 요청 파싱 |
| 📡 **MCPService** | MCP 서버에 데이터 요청 |
| 🧭 **TripService** | 전체 프로세스 조율 및 동선 최적화 |
| 💰 **ScoringService** | 비용 계산 및 POI 점수화 |
| 💾 **DB 연동** | 최종 여행 계획 데이터 저장 |

---

## 🌐 2. MCP 서버 (Multi-Content Provider - FastAPI)

**역할:** 외부 세계와의 데이터 허브(Data Hub).  
백엔드의 요청에 따라 항공, 숙소, 날씨, 관광지(POI) 등  
여러 외부 API를 **동시에 호출하여 수집 및 정규화**하는 서버입니다.

### ⚙️ 주요 책임

- ⚡ **asyncio** 기반의 비동기 외부 API 호출  
- 🤝 `BookingClient`, `FlightClient`, `WeatherClient` 등 각 API 클라이언트 관리  
- 📦 수집된 데이터를 백엔드가 사용하기 쉬운 통합 스키마로 가공  

---

## 🛠️ 기술 스택

| 구분 | 기술 |
|------|------|
| **Backend & MCP** | Python 3.11+, Flask, FastAPI, MySQL, SQLAlchemy |
| **AI / LLM** | Hugging Face Router (LLM API 연동) |
| **External APIs** | Google Maps, Kakao Maps, Booking.com, OpenWeatherMap, 한국수출입은행 |
| **Tools** | Postman, python-dotenv |

---

## 🚀 시작하기

### 1️⃣ 환경 설정

```bash
# 1. 저장소를 클론합니다.
git clone https://github.com/your-username/TripMind.git
cd TripMind

# 2. 가상환경을 생성하고 활성화합니다.
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 필요한 패키지를 설치합니다.
pip install -r requirements.txt
```

2️⃣ 서버 실행

각 서버는 별도의 터미널에서 실행해야 합니다.

```bash
# 터미널 1: 백엔드 서버 실행
cd apps/backend
flask run --port 8080

# 터미널 2: MCP 서버 실행
cd apps/mcp
uvicorn mcp_server.main:app --reload --port 7000
```

---

## 🌏 주요 특징 요약

✅ LLM 기반 자연어 입력 파싱

✅ AI 점수화 알고리즘 (평점·거리·가격·성향 기반)

✅ 하루 4개 슬롯 (아침·점심·오후·저녁) 단위 일정 구성

✅ 비동기 외부 API 병렬 호출 (FastAPI + asyncio)

✅ 예산·거리·날씨 기반 일정 자동 조정

✅ Flask–MCP 간 표준 스키마 연동

✅ AWS 배포 고려 구조 (S3 + CloudFront + EC2/Fargate + Route53)
