# backend/tripmind_api/services/llm_service.py
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
            # 💡 '..'을 사용하여 'services' 폴더 밖으로 나간 후 spec 파일 경로를 찾습니다.
            spec_path = os.path.join(current_dir, '..', spec_file_name)
            with open(spec_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise LLMServiceError(f"LLM spec file '{spec_file_name}' not found at {spec_path}")

    def parse_conversation(self, messages: list[dict]) -> dict:
        """
        [사용 안 함 - '하이브리드' 방식으로 대체됨]
        전체 대화 기록을 기반으로 정보를 파싱합니다.
        """
        # (이 함수는 'trip_route.py'의 하이브리드 방식에서는 더 이상 호출되지 않습니다)
        system_prompt = self._get_system_prompt('llm_parser_spec_v2.md')
        
        full_conversation = [{"role": "system", "content": system_prompt}] + messages
        
        llm_response = self._call_llm(full_conversation, response_format={"type": "json_object"})
        
        try:
            content = llm_response['choices'][0]['message']['content']
            return json.loads(content)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise LLMServiceError(f"Failed to parse LLM's JSON response: {e}")

    def generate_clarifying_question(self, messages: list[dict], missing_fields: list[str]) -> str:
        """
        [사용 안 함 - '하이브리드' 방식으로 대체됨]
        누락된 정보를 바탕으로 사용자에게 되물을 질문을 생성합니다.
        """
        # (이 함수는 'trip_route.py'의 하이브리드 방식에서는 더 이상 호출되지 않습니다)
        fields_str = ", ".join(missing_fields)
        question_prompt = f"여행 계획에 필요한 다음 정보({fields_str})를 얻기 위해, 친절한 여행 도우미가 되어 사용자에게 자연스러운 질문을 한 문장으로 해주세요. 인사나 부연 설명은 생략합니다."
        
        full_conversation = messages + [{"role": "user", "content": question_prompt}]
        
        response_json = self._call_llm(full_conversation)
        return response_json['choices'][0]['message']['content']

    # --- 💡 1. '하이브리드' 방식을 위한 신규 함수 (흥미 추출) ---
    def extract_interests(self, style_text: str) -> list[str]:
        """
        사용자가 입력한 '여행 스타일 텍스트'를 기반으로 흥미 키워드 리스트를 추론합니다.
        """
        system_prompt = self._get_system_prompt('llm_interests_spec.md')
        
        # 'parse_conversation'과 달리, 전체 대화가 아닌 'style_text'만 사용합니다.
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": style_text}
        ]
        
        # JSON 형식으로 응답 요청
        llm_response = self._call_llm(messages, response_format={"type": "json_object"})
        
        try:
            content = llm_response['choices'][0]['message']['content']
            # LLM이 JSON 문자열(예: '["휴양", "맛집"]')을 반환하면, 이를 파싱하여 리스트로 반환
            return json.loads(content) 
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            print(f"LLMService Error (extract_interests): {e}. Falling back to default.")
            return ["관광"] # 실패 시 기본값 반환

    # --- 💡 2. '하이브리드' 방식을 위한 신규 함수 (국내/해외 추론) ---
    def check_domestic(self, origin: str, destination: str) -> bool:
        """
        출발지와 도착지를 기반으로 국내/해외 여부를 JSON으로 추론합니다.
        """
        system_prompt = self._get_system_prompt('llm_domestic_spec.md')
        
        user_prompt = f"({origin}, {destination})"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # JSON 형식으로 응답 요청
        llm_response = self._call_llm(messages, response_format={"type": "json_object"})
        
        try:
            content = llm_response['choices'][0]['message']['content']
            # LLM이 JSON 문자열(예: '{"is_domestic": false}')을 반환하면, 파싱함
            result_json = json.loads(content)
            return result_json.get("is_domestic", False) # is_domestic 값을 bool로 반환
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            print(f"LLMService Error (check_domestic): {e}. Falling back to default (False).")
            # 💡 추론 실패 시 '해외'로 간주 (안전한 기본값)
            return False 

    # --- 💡 3. (신규) 일반 채팅 함수 (llm.py 라우터용) ---
    def chat(self, messages: list[dict]) -> str:
        """
        /llm/complete 엔드포인트를 위한 범용 chat 함수입니다. (동기)
        """
        # 이 함수는 JSON 모드가 아닌 일반 텍스트 응답을 가정합니다.
        response_json = self._call_llm(messages)
        try:
            return response_json['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            raise LLMServiceError(f"Failed to parse LLM's chat response: {e}")
    
    # --- 💡 [NEW] 여행 계획 수정 기능 추가 (Hugging Face 사용) ---
    def modify_plan(self, current_plan: dict, target_slot: dict, user_prompt: str) -> dict:
        """
        기존 계획과 사용자의 요청을 바탕으로 특정 일정을 수정합니다.
        """
        day_idx = target_slot.get('dayIndex')
        event_idx = target_slot.get('eventIndex')
        
        # 1. 수정 대상 일정 가져오기
        try:
            target_event = current_plan['schedule'][day_idx]['events'][event_idx]
        except (IndexError, KeyError, TypeError):
            raise LLMServiceError("Invalid target slot index or plan structure")

        # 2. 프롬프트 구성
        system_prompt = """
        You are a professional travel planner. 
        Your task is to modify a specific travel event based on the user's feedback.
        Return ONLY a valid JSON object representing the modified event.
        The JSON structure must match the 'Current Event' format.
        """

        user_message = f"""
        [Current Event]
        {json.dumps(target_event, ensure_ascii=False)}

        [User Request]
        "{user_prompt}"

        Please provide the modified event as a JSON object.
        Keys required: "time_slot", "description", "icon".
        - "icon" should be one of: "plane", "shopping", "utensils", "home", "coffee", "car".
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            # 3. LLM 호출 (JSON 모드)
            llm_response = self._call_llm(messages, response_format={"type": "json_object"})
            content = llm_response['choices'][0]['message']['content']
            
            # 4. JSON 파싱
            modified_event = json.loads(content)
            
            # 필수 필드 보정 (LLM이 누락했을 경우 원본 값 사용)
            if 'time_slot' not in modified_event:
                modified_event['time_slot'] = target_event.get('time_slot')
            if 'icon' not in modified_event:
                modified_event['icon'] = target_event.get('icon', 'map-pin')
                
            return modified_event

        except (json.JSONDecodeError, KeyError, IndexError, LLMServiceError) as e:
            print(f"LLM Modify Error: {e}")
            # 실패 시 기본 응답 생성 (에러를 내지 않고 텍스트만 변경)
            fallback_event = target_event.copy()
            fallback_event['description'] = f"[수정됨] {user_prompt} (AI 응답 실패로 단순 반영)"
            return fallback_event

    # --- 내부 LLM 호출 함수 (기존 코드 유지) ---
    def _call_llm(self, messages: list[dict], response_format: dict | None = None) -> dict:
        """LLM API를 호출하는 내부 메소드 (동기)"""
        # 💡 기존의 HF_TOKEN 인증 방식 유지
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7, # 창의성 조절
            "max_tokens": 500
        }
        if response_format:
            payload["response_format"] = response_format
        
        try:
            response = self.session.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            error_details = e.response.text if e.response else str(e)
            # 401 Unauthorized 에러가 여기서 발생하면 .env의 HF_TOKEN을 확인해야 합니다.
            raise LLMServiceError(f"Failed to call LLM API: {error_details}")