import os, requests
MCP_BASE = os.getenv("MCP_BASE", "http://localhost:7000")

def get_quotes(payload):
    res = requests.post(f"{MCP_BASE}/quotes", json=payload, timeout=10)
    res.raise_for_status()
    j = res.json()
    return j.get("flights", []), j.get("hotels", [])