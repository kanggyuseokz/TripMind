# backend/tripmind_api/routes/llm_route.py
from flask import Blueprint, request, jsonify
from ..services.llm_service import LLMService

bp = Blueprint("llm", __name__)
llm_service = LLMService()

@bp.get("/health")
def health():
    # 간단한 헬스 체크 (Gemini 호출)
    try:
        # Gemini 모델에게 간단한 인사를 건네 응답을 확인합니다.
        out = llm_service.chat([{"role":"user", "content":"pong만 출력해"}])
        return jsonify({"ok": True, "echo": out})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@bp.post("/complete")
def complete():
    # 범용 채팅 API
    body = request.get_json(force=True) or {}
    prompt = body.get("prompt", "서울→오사카 2박3일 커플 여행 요약")
    system_prompt = body.get("system", "You are a helpful travel planner.")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    try:
        out = llm_service.chat(messages)
        # 💡 [수정됨] 응답 모델명을 실제 사용 중인 모델명으로 변경
        return jsonify({"model": "gemini-pro", "output": out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500