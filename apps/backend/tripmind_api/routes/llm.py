# backend/tripmind_api/routes/llm.py
import asyncio  # 👈 1. asyncio 임포트
from flask import Blueprint, request
from ..services.llm_service import chat  # 👈 'chat' 함수가 async def라고 가정

bp = Blueprint("llm", __name__)

@bp.get("/health")
def health():
    # 👈 2. chat 함수를 asyncio.run()으로 호출
    out = asyncio.run(chat([{"role":"user","content":"pong만 출력해"}]))
    return {"ok": True, "echo": out}

@bp.post("/complete")
def complete():
    body = request.get_json(force=True) or {}
    prompt = body.get("prompt", "서울→오사카 2박3일 커플 여행 요약")
    sys = body.get("system", "You are a helpful travel planner.")
    # 👈 3. chat 함수를 asyncio.run()으로 호출
    out = asyncio.run(chat([{"role":"system","content":sys},{"role":"user","content":prompt}]))
    return {"model": "gpt-oss-20b", "output": out}
