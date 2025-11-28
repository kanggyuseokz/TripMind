# backend/tripmind_api/services/llm_service.py
from __future__ import annotations
import json
import os
import google.generativeai as genai
from flask import current_app

class LLMServiceError(Exception):
    """LLM 서비스 관련 에러"""
    pass

class LLMService:
    """Google Gemini LLM을 사용하여 사용자 쿼리를 구조화된 JSON으로 파싱하거나,
    대화의 문맥을 이해하여 다음 질문을 생성하는 서비스입니다."""

    def __init__(self):
        # 초기화 시점에는 모델을 로드하지 않고(Lazy Loading), 
        # 실제 호출 시점에 current_app context를 통해 키를 가져옵니다.
        self.model = None

    def _get_model(self):
        """앱 설정에서 API 키를 로드하여 모델을 초기화합니다."""
        if self.model:
            return self.model

        # config.py에 설정된 GEMINI_API_KEY 사용
        api_key = current_app.config.get("GEMINI_API_KEY")
        
        if not api_key:
             # 개발 환경 편의를 위해 os.environ도 확인
             api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise LLMServiceError("GEMINI_API_KEY not found in app config or environment variables.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        return self.model

    def _get_system_prompt(self, spec_file_name: str) -> str:
        """지정된 spec 파일에서 시스템 프롬프트를 로드합니다."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # '..'을 사용하여 'services' 폴더 밖으로 나간 후 spec 파일 경로를 찾습니다.
            spec_path = os.path.join(current_dir, '..', spec_file_name)
            if not os.path.exists(spec_path):
                # 파일이 없을 경우를 대비해 빈 문자열 반환하거나 기본 프롬프트 사용 가능
                # 여기서는 에러를 발생시키되, 파일이 없으면 로직이 중단될 수 있으므로 주의
                return "" 
            with open(spec_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            # 파일 읽기 실패 시 로그를 남기고 빈 문자열 반환 (서비스 중단 방지)
            print(f"Warning: Failed to load system prompt {spec_file_name}: {e}")
            return ""

    def _call_model(self, prompt: str) -> str:
        """Gemini API를 호출하는 내부 메소드"""
        try:
            model = self._get_model()
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise LLMServiceError(f"Gemini API Call Failed: {e}")

    # --- 💡 1. '하이브리드' 방식을 위한 신규 함수 (흥미 추출) ---
    def extract_interests(self, text):
        """
        사용자 입력 텍스트에서 여행 관심사 키워드 추출
        """
        prompt = f"""
        Extract travel interest keywords from the text: "{text}"
        Return ONLY a JSON list of strings. Example: ["food", "history"]
        Do not include markdown formatting.
        """
        try:
            result = self._call_model(prompt)
            # JSON 파싱 시도
            cleaned_result = result.replace("```json", "").replace("```", "").strip()
            interests = json.loads(cleaned_result)
            
            # 딕셔너리 구조(예: {"keywords": [...]})가 올 경우 리스트로 명확히 변환
            if isinstance(interests, list):
                return interests
            elif isinstance(interests, dict):
                # "keywords" 또는 "interests" 키가 있으면 그 내부 리스트 반환
                if "keywords" in interests and isinstance(interests["keywords"], list):
                    return interests["keywords"]
                if "interests" in interests and isinstance(interests["interests"], list):
                    return interests["interests"]
                
                # 특정 키가 없으면 값들을 평탄화(Flatten)하여 리스트로 만듦
                flat_list = []
                for val in interests.values():
                    if isinstance(val, list):
                        flat_list.extend(val)
                    elif isinstance(val, str):
                        flat_list.append(val)
                return flat_list if flat_list else ["general"]
                
            return ["general"]
        except:
            return ["general"]

    # --- 💡 2. '하이브리드' 방식을 위한 신규 함수 (국내/해외 추론) ---
    def check_domestic(self, origin: str, destination: str) -> bool:
        """
        출발지와 도착지를 기반으로 국내/해외 여부를 JSON으로 추론합니다.
        """
        system_prompt = self._get_system_prompt('llm_domestic_spec.md')
        
        # Gemini는 messages 리스트 대신 하나의 프롬프트 문자열을 선호하므로 합칩니다.
        prompt = f"""
        {system_prompt}
        
        Analyze the following trip:
        Origin: {origin}
        Destination: {destination}
        
        Is this a domestic trip within the same country?
        Return JSON only: {{"is_domestic": true/false}}
        """
        
        try:
            result = self._call_model(prompt)
            cleaned_result = result.replace("```json", "").replace("```", "").strip()
            result_json = json.loads(cleaned_result)
            return result_json.get("is_domestic", False) 
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, LLMServiceError) as e:
            print(f"LLMService Error (check_domestic): {e}. Falling back to default (False).")
            # 추론 실패 시 '해외'로 간주 (안전한 기본값)
            return False 

    # --- 💡 3. (신규) 일반 채팅 함수 (llm.py 라우터용) ---
    def chat(self, messages: list[dict]) -> str:
        """
        /llm/complete 엔드포인트를 위한 범용 chat 함수입니다.
        """
        # messages 리스트를 Gemini 프롬프트 형식으로 변환
        prompt_parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            prompt_parts.append(f"{role}: {content}")
            
        full_prompt = "\n".join(prompt_parts)
        return self._call_model(full_prompt)
    
    # --- 💡 [NEW] 여행 계획 수정 기능 추가 (Gemini 사용) ---
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
        prompt = f"""
        You are a professional travel planner. 
        Your task is to modify a specific travel event based on the user's feedback.
        Return ONLY a valid JSON object representing the modified event.
        The JSON structure must match the 'Current Event' format.

        [Current Event]
        {json.dumps(target_event, ensure_ascii=False)}

        [User Request]
        "{user_prompt}"

        Please provide the modified event as a JSON object.
        Keys required: "time_slot", "description", "icon".
        - "icon" should be one of: "plane", "shopping", "utensils", "home", "coffee", "car".
        Do not include markdown formatting.
        """

        try:
            # 3. LLM 호출
            result = self._call_model(prompt)
            cleaned_result = result.replace("```json", "").replace("```", "").strip()
            
            # 4. JSON 파싱
            modified_event = json.loads(cleaned_result)
            
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