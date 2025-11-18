import os, json
from tripmind_api import create_app

def test_llm_complete_route(monkeypatch):
    # DRY-RUN: 실제 API 호출 막고 가짜 응답 주입
    def fake_chat(messages, temperature=0.2):
        # 마지막 user 메시지를 그대로 돌려주는 흉내
        for m in reversed(messages):
            if m["role"] == "user":
                return f"ECHO: {m['content']}"
        return "ECHO"
    monkeypatch.setenv("OPENAI_API_KEY", "")  # 키 없어도 에러 안 나게
    # chat 함수를 패치하려면 import 경로에 맞게 모듈 교체
    import apps.backend.tripmind_api.routes.llm_route as llm_route
    llm_route.chat = fake_chat

    app = create_app()
    client = app.test_client()
    resp = client.post("/llm/complete", json={"prompt": "테스트 프롬프트"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["model"] == "gpt-oss-20b"
    assert data["output"].startswith("ECHO:")
