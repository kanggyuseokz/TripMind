from __future__ import annotations
import json
import os
import requests
from tripmind_api.config import settings

class LlmServiceError(Exception):
    """LLM 서비스 관련 에러"""
    pass

class LlmService:
    """LLM을 사용하여 사용자의 자연어 입력을 파싱하는 서비스"""

    def __init__(self):
        self.hf_token = settings.HF_TOKEN
        self.hf_model_url = settings.HF_BASE_URL
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """프로젝트 루트의 llm_parser_spec_v2.md 파일에서 시스템 프롬프트를 로드합니다."""
        try:
            # Note: Adjust the path if necessary based on your project structure
            prompt_path = os.path.join(os.path.dirname(__file__), '..', 'llm_parser_spec_v2.md')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise LlmServiceError("LLM parser spec file not found.")

    def parse_user_request(self, user_prompt: str) -> dict:
        """
        시스템 프롬프트와 사용자 입력을 결합하여 LLM API를 호출하고,
        구조화된 JSON 응답을 반환합니다.
        """
        # TODO: 실제 Hugging Face API 호출 로직으로 교체해야 합니다.
        # 아래는 실제 API 연동을 위한 예시 코드입니다. (현재는 Mock 반환)
        """
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {
            "inputs": f"{self.system_prompt}\n\n입력: \"{user_prompt}\"\n\n출력:",
            "parameters": {"return_full_text": False, "max_new_tokens": 512}
        }
        
        try:
            response = requests.post(self.hf_model_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            # LLM 응답에서 JSON 부분만 추출하는 후처리 필요
            # result_text = response.json()[0]['generated_text']
            # return json.loads(result_text)
        except requests.RequestException as e:
            raise LlmServiceError(f"LLM API request failed: {e}")
        except json.JSONDecodeError:
            raise LlmServiceError("Failed to parse LLM response as JSON.")
        """

        # --- Mock Response ---
        # 실제 API 연동 전까지 테스트를 위한 Mock 응답
        if "강릉" in user_prompt:
            return {
              "origin": "서울", "destination": "강릉", "is_domestic": True,
              "start_date": "2025-10-18", "end_date": "2025-10-19",
              "party_size": 2, "budget_per_person": {"amount": 200000, "currency": "KRW"},
              "meta": {"language": "ko", "inferred_fields": ["start_date", "end_date", "budget_per_person"]}
            }
        else: # Default mock for overseas
            return {
              "origin": "부산", "destination": "도쿄", "is_domestic": False,
              "start_date": "2025-11-02", "end_date": "2025-11-05",
              "party_size": 2, "budget_per_person": {"amount": 600000, "currency": "KRW"},
              "meta": {"language": "ko", "inferred_fields": ["budget_per_person"]}
            }
