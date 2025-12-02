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

    # --- ✅ [NEW] 사용자 요청 전체 파싱 ---
    def parse_user_request(self, user_request: str) -> dict:
        """
        사용자 요청을 파싱하여 구조화된 여행 정보 추출
        - destination, start_date, end_date, party_size, interests 등
        
        Args:
            user_request: 전체 여행 정보 텍스트
        
        Returns:
            {
                'origin': '서울/인천 (ICN)',
                'destination': '도쿄/나리타',
                'start_date': '2025-12-04',
                'end_date': '2025-12-08',
                'party_size': 2,
                'is_domestic': False,
                'interests': ['맛집']
            }
        """
        try:
            prompt = f"""
다음 사용자 요청을 분석하여 JSON 형식으로 변환하세요.

사용자 요청:
{user_request}

JSON 형식:
{{
  "origin": "출발지 (IATA 코드 포함)",
  "destination": "도착지/공항명",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "party_size": 숫자,
  "is_domestic": true/false,
  "budget_per_person": {{"amount": 숫자, "currency": "KRW"}},
  "interests": ["키워드1", "키워드2"],
  "schedule": [
    {{
      "day": 1,
      "date": "Day 1",
      "full_date": "YYYY-MM-DD",
      "events": [
        {{"time_slot": "09:00", "description": "활동 내용", "icon": "car"}},
        {{"time_slot": "12:00", "description": "점심 식사", "icon": "utensils"}},
        {{"time_slot": "14:00", "description": "오후 활동", "icon": "camera"}},
        {{"time_slot": "18:00", "description": "저녁 식사", "icon": "utensils"}},
        {{"time_slot": "21:00", "description": "호텔 복귀", "icon": "home"}}
      ]
    }}
  ]
}}

중요:
1. schedule 배열은 start_date부터 end_date까지 모든 날짜를 포함해야 합니다.
2. 각 날의 events는 최소 3~5개 포함하세요.
3. icon은 다음 중 하나: "plane", "car", "shopping", "utensils", "coffee", "home", "camera"
4. 반드시 JSON만 출력하세요. 다른 설명은 하지 마세요.

"""
            
            print(f"[LLMService] 📝 Parsing user request...")
            
            result = self._call_model(prompt)
            cleaned_result = result.replace("```json", "").replace("```", "").strip()
            
            parsed = json.loads(cleaned_result)

            if not parsed.get('schedule'):
                print(f"[LLMService] ⚠️ No schedule from LLM, will be generated by MCP")
            else:
                print(f"[LLMService] ✅ Schedule generated: {len(parsed['schedule'])} days")

            print(f"[LLMService] ✅ Parsed Request: {parsed}")
            
            return parsed
            
        except Exception as e:
            print(f"[LLMService] ❌ parse_user_request error: {e}")
            # 파싱 실패 시 기본값 반환
            return {
                'destination': '도쿄',
                'start_date': '2025-12-04',
                'end_date': '2025-12-08',
                'party_size': 2,
                'is_domestic': False,
                'interests': ['관광']
            }

    # --- 💡 1. '하이브리드' 방식을 위한 신규 함수 (흥미 추출) ---
    def extract_interests(self, text: str) -> list:
        """
        ✅ MD 파일(llm_interests_spec.md)을 사용하여 여행 스타일 키워드 추출
        
        Args:
            text: "맛집 위주, 휴양 선호, 빡빡한 일정..."
        
        Returns:
            ["맛집", "휴양"]
        """
        try:
            # ✅ MD 파일 로드
            system_prompt = self._get_system_prompt('llm_interests_spec.md')
            
            if not system_prompt:
                # 폴백: 기본 프롬프트
                system_prompt = """당신은 여행 스타일 키워드 추출 전문가입니다.
사용자의 여행 스타일 텍스트가 주어지면, ['관광', '맛집', '쇼핑', '휴양', '액티비티', '문화/예술', '역사', '자연'] 중에서
가장 관련 있는 키워드를 JSON 리스트 형식으로 반환합니다.
만약 특별한 키워드가 없으면 ['관광']을 반환합니다."""
            
            # ✅ 전체 프롬프트 생성
            full_prompt = f"""{system_prompt}

사용자 입력: "{text}"

JSON 리스트만 출력하세요. 예: ["관광", "맛집"]
"""
            
            print(f"[LLMService] 🎨 Extracting interests: {text}")
            
            result = self._call_model(full_prompt)
            cleaned_result = result.replace("```json", "").replace("```", "").strip()
            
            interests = json.loads(cleaned_result)
            
            # ✅ 다양한 응답 형식 처리
            if isinstance(interests, list):
                print(f"[LLMService] ✅ Extracted Interests: {interests}")
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
                return flat_list if flat_list else ["관광"]
                
            return ["관광"]
            
        except Exception as e:
            print(f"[LLMService] ❌ extract_interests error: {e}. Falling back to ['관광']")
            return ["관광"]

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
            
            is_domestic = result_json.get("is_domestic", False)
            print(f"[LLMService] 🌍 check_domestic: {origin} → {destination} = {is_domestic}")
            
            return is_domestic
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