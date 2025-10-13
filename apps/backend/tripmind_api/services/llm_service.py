from __future__ import annotations
import json
import requests
from ..config import settings
import os

class LLMServiceError(Exception):
    """LLM 서비스 관련 에러"""
    pass

class LLMService:
    """Hugging Face LLM을 사용하여 사용자 쿼리를 구조화된 JSON으로 파싱하는 서비스입니다."""

    def __init__(self):
        self.session = requests.Session()
        self.hf_token = settings.HF_TOKEN
        self.api_url = f"{settings.HF_BASE_URL}/chat/completions"
        self.model = settings.HF_MODEL

    def parse_query(self, user_query: str) -> dict:
        """
        주어진 사용자 쿼리를 구조화된 JSON으로 파싱합니다.
        오직 LLM API만을 사용합니다.
        """
        # llm_parser_spec_v2.md의 내용을 시스템 프롬프트로 사용합니다.
        try:
            # llm_parser_spec_v2.md 파일은 Flask 앱이 실행되는 위치를 기준으로
            # 정확한 상대 경로 또는 절대 경로를 지정해야 합니다.
            with open('backend/tripmind_api/llm_parser_spec_v2.md', 'r', encoding='utf-8') as f:
                system_prompt = f.read()
            current_dir = os.path.dirname(os.path.abspath(__file__))
            spec_path = os.path.join(current_dir, '..', 'llm_parser_spec_v2.md')
            
            with open(spec_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        except FileNotFoundError:
            raise LLMServiceError("LLM parser specification file not found.")

        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = self.session.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # LLM이 반환한 JSON 문자열을 실제 JSON 객체로 파싱합니다.
            content = result['choices'][0]['message']['content']
            parsed_json = json.loads(content)
            return parsed_json
            
        except (requests.RequestException, json.JSONDecodeError, KeyError, IndexError) as e:
            raise LLMServiceError(f"Failed to parse query with LLM: {e}")

