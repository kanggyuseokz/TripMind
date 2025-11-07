# mcp/mcp_server/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

# 💡 1. 우리가 작업한 plan_router를 임포트합니다.
from .routers import plan_router
# 💡 2. (선택사항) 나중에 클라이언트 인스턴스 관리를 위해 추가
from .clients.agoda_client import AgodaClient
from .clients.flight_client import FlightClient
# ... (다른 클라이언트들)

# (참고) FastAPI의 최신 권장 방식은 lifespan을 사용하는 것입니다.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # -----------------------------------------------------------------
    # (선택사항) 서버 시작 시 클라이언트 인스턴스를 미리 생성합니다.
    # 이렇게 하면 요청이 올 때마다 클라이언트를 새로 만들지 않아 효율적입니다.
    # app.state.agoda_client = AgodaClient()
    # app.state.flight_client = FlightClient()
    # (mcp_service.py에서 생성하는 대신, 여기서 생성한 것을 주입(DI)할 수 있습니다)
    # -----------------------------------------------------------------
    
    print("MCP 서버가 시작되었습니다.")
    yield
    # (서버 종료 시 리소스 정리 로직)
    print("MCP 서버가 종료됩니다.")

# 💡 3. FastAPI 앱 생성 (lifespan은 선택사항)
app = FastAPI(
    title="TripMind MCP - Multi-Content Provider",
    lifespan=lifespan 
)

@app.get("/health")
def health():
    """메인 백엔드가 MCP 서버가 살아있는지 확인하는 엔드포인트"""
    return {"status": "ok", "message": "MCP server is running."}

# 💡 4. 가장 중요한 부분: plan_router.py에 정의된 모든 엔드포인트(/plan/generate)를 앱에 포함시킵니다.
app.include_router(plan_router.router)