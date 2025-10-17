from __future__ import annotations
import json
import os
import requests
from ..config import settings

class LLMServiceError(Exception):
    """LLM 서비스 관련 에러"""
    pass

class LLMService:
    """Hugging Face LLM을 사용하여 사용자 쿼리를 구조화된 JSON으로 파싱하거나,
    대화의 문맥을 이해하여 다음 질문을 생성하는 서비스입니다."""

    def __init__(self):
        self.session = requests.Session()
        self.hf_token = settings.HF_TOKEN
        self.api_url = f"{settings.HF_BASE_URL}/chat/completions"
        self.model = settings.HF_MODEL

    def _get_system_prompt(self, spec_file_name: str) -> str:
        """지정된 spec 파일에서 시스템 프롬프트를 로드합니다."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            spec_path = os.path.join(current_dir, '..', spec_file_name)
            with open(spec_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise LLMServiceError(f"LLM spec file '{spec_file_name}' not found.")

    def parse_conversation(self, messages: list[dict]) -> dict:
        """전체 대화 기록을 기반으로 정보를 파싱합니다."""
        system_prompt = self._get_system_prompt('llm_parser_spec_v2.md')
        
        # 시스템 프롬프트를 대화의 가장 앞에 추가
        full_conversation = [{"role": "system", "content": system_prompt}] + messages
        
        llm_response = self._call_llm(full_conversation, response_format={"type": "json_object"})
        
        # LLM 응답에서 JSON 콘텐츠를 추출하고 파싱합니다.
        try:
            content = llm_response['choices'][0]['message']['content']
            return json.loads(content)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise LLMServiceError(f"Failed to parse LLM's JSON response: {e}")

    def generate_clarifying_question(self, messages: list[dict], missing_fields: list[str]) -> str:
        """누락된 정보를 바탕으로 사용자에게 되물을 질문을 생성합니다."""
        fields_str = ", ".join(missing_fields)
        # LLM에게 역할을 명확히 지시하는 프롬프트
        question_prompt = f"여행 계획에 필요한 다음 정보({fields_str})를 얻기 위해, 친절한 여행 도우미가 되어 사용자에게 자연스러운 질문을 한 문장으로 해주세요. 인사나 부연 설명은 생략합니다."
        
        # 대화 기록에 AI의 역할을 지시하는 내용을 추가
        full_conversation = messages + [{"role": "user", "content": question_prompt}]
        
        response_json = self._call_llm(full_conversation)
        return response_json['choices'][0]['message']['content']

    def _call_llm(self, messages: list[dict], response_format: dict | None = None) -> dict:
        """LLM API를 호출하는 내부 메소드"""
        headers = {"Authorization": f"Bearer {self.hf_token}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": messages}
        if response_format:
            payload["response_format"] = response_format
        
        try:
            response = self.session.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            error_details = e.response.text if e.response else str(e)
            raise LLMServiceError(f"Failed to call LLM API: {error_details}")

