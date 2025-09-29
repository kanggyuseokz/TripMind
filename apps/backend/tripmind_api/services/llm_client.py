import os, requests

BASE  = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
KEY   = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-oss-20b")

def chat(messages, temperature=0.2):
    """
    messages: [{"role":"system","content":"..."},{"role":"user","content":"..."}]
    """
    if not KEY:
        return "(DRY-RUN) OPENAI_API_KEY 미설정"
    url = f"{BASE}/responses"
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "input": messages, "temperature": temperature}
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    j = r.json()
    return j.get("output_text") or j["output"][0]["content"][0]["text"]
