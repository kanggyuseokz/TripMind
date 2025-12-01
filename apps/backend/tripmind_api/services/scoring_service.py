# backend/tripmind_api/services/scoring_service.py

class ScoringService:
    """
    여행 경비를 계산하고, 사용자의 선호도에 따라 POI의 점수를 매기는 서비스.
    TripService에 필요한 분석 데이터를 제공합니다.
    """

    # 목적지별 하루 추정 비용 (1인 기준, KRW)
    # 실제 서비스 시에는 DB나 외부 API로 대체 권장
    COST_ESTIMATES_PER_DAY = {
        # 일본
        "도쿄": {"food": 80000, "transport": 15000, "activity": 30000},
        "오사카": {"food": 70000, "transport": 18000, "activity": 35000},
        "후쿠오카": {"food": 65000, "transport": 12000, "activity": 20000},
        "삿포로": {"food": 85000, "transport": 20000, "activity": 40000},
        "오키나와": {"food": 70000, "transport": 25000, "activity": 30000},
        
        # 동남아시아
        "다낭": {"food": 40000, "transport": 10000, "activity": 20000},
        "방콕": {"food": 45000, "transport": 10000, "activity": 25000},
        "세부": {"food": 45000, "transport": 12000, "activity": 30000},
        "발리": {"food": 50000, "transport": 15000, "activity": 35000},
        "싱가포르": {"food": 90000, "transport": 20000, "activity": 50000},
        
        # 유럽/미주
        "파리": {"food": 110000, "transport": 30000, "activity": 50000},
        "런던": {"food": 120000, "transport": 35000, "activity": 55000},
        "로마": {"food": 90000, "transport": 25000, "activity": 45000},
        "뉴욕": {"food": 130000, "transport": 30000, "activity": 60000},
        "LA": {"food": 120000, "transport": 40000, "activity": 50000},
        "하와이": {"food": 110000, "transport": 40000, "activity": 60000},

        # 국내
        "서울": {"food": 50000, "transport": 10000, "activity": 20000},
        "부산": {"food": 55000, "transport": 12000, "activity": 20000},
        "제주": {"food": 65000, "transport": 30000, "activity": 30000},
        "강릉": {"food": 60000, "transport": 20000, "activity": 25000},
        
        # 기본값 (데이터 없는 도시용)
        "default": {"food": 75000, "transport": 15000, "activity": 30000},
    }

    def calculate_total_cost(
        self,
        flight_quote: dict | None,
        hotel_quote: dict | None,
        duration_days: int,
        party_size: int,
        destination: str,
        user_style: str = "default"
    ) -> dict:
        """
        여행의 총 경비를 계산합니다.
        - 고정 비용: 항공, 숙소
        - 추정 비용: 식비, 현지 교통비, 액티비티 비용
        """
        # ✅ flight_quote 처리 (리스트 또는 딕셔너리)
        if isinstance(flight_quote, list):
            # 리스트인 경우: 첫 번째 항공편 사용
            if flight_quote:
                first_flight = flight_quote[0]
                flight_cost = first_flight.get("price_total", 0) or first_flight.get("price", 0)
            else:
                flight_cost = 0
        elif isinstance(flight_quote, dict):
            # 딕셔너리인 경우: 직접 사용
            flight_cost = flight_quote.get("price_total", 0) or flight_quote.get("price", 0)
        else:
            flight_cost = 0
        
        # ✅ hotel_quote 처리 (리스트 또는 딕셔너리)
        if isinstance(hotel_quote, list):
            # 리스트인 경우: 첫 번째 호텔 사용
            if hotel_quote:
                first_hotel = hotel_quote[0]
                hotel_cost = first_hotel.get("priceTotal", 0) or first_hotel.get("price", 0)
            else:
                hotel_cost = 0
        elif isinstance(hotel_quote, dict):
            # 딕셔너리인 경우: 직접 사용
            hotel_cost = hotel_quote.get("priceTotal", 0) or hotel_quote.get("price", 0)
        else:
            hotel_cost = 0

        # 목적지에 맞는 하루 추정 비용 가져오기 (부분 일치 검색 지원)
        estimates = self.COST_ESTIMATES_PER_DAY["default"]
        for city, cost in self.COST_ESTIMATES_PER_DAY.items():
            if city in destination:
                estimates = cost
                break
        
        # user_style에 따라 식비나 액티비티 비용을 조정
        adjusted_food = estimates["food"]
        adjusted_activity = estimates["activity"]

        if "맛집" in user_style or "식도락" in user_style:
            adjusted_food *= 1.3
        if "쇼핑" in user_style:
            adjusted_activity *= 1.5

        food_cost = adjusted_food * duration_days * party_size
        transport_cost = estimates["transport"] * duration_days * party_size
        activity_cost = adjusted_activity * duration_days * party_size
        
        costs_by_category = {
            "flight": flight_cost,
            "hotel": hotel_cost,
            "food": food_cost,
            "transport": transport_cost,
            "activity": activity_cost,
        }
        
        total_cost = sum(costs_by_category.values())

        return {
            "total_cost": round(total_cost),
            "costs_by_category": costs_by_category
        }

    def calculate_cost_breakdown(self, costs_by_category: dict) -> list[dict]:
        """프론트엔드 차트에 사용할 수 있도록 항목별 비용 비중(%)을 계산합니다."""
        total_cost = sum(costs_by_category.values())
        if total_cost == 0:
            return []

        breakdown = [
            {"category": "항공", "percentage": round((costs_by_category.get("flight", 0) / total_cost) * 100, 1)},
            {"category": "숙소", "percentage": round((costs_by_category.get("hotel", 0) / total_cost) * 100, 1)},
            {"category": "식비", "percentage": round((costs_by_category.get("food", 0) / total_cost) * 100, 1)},
            {"category": "교통/액티비티", "percentage": round(((costs_by_category.get("transport", 0) + costs_by_category.get("activity", 0)) / total_cost) * 100, 1)}
        ]
        
        # 비중이 0%인 항목은 제외
        return [item for item in breakdown if item["percentage"] > 0]

    def score_poi_candidates(self, poi_list: list[dict], user_style: str) -> list[dict]:
        """
        사용자의 여행 스타일에 따라 POI 목록의 점수를 매기고 정렬합니다.
        """
        style_weights = {
            "맛집": {"맛집": 1.5, "음식점": 1.5, "카페": 1.2, "관광명소": 1.0},
            "관광": {"관광명소": 1.5, "문화시설": 1.3, "맛집": 0.8, "음식점": 0.8},
            "휴식": {"카페": 1.5, "공원": 1.3, "관광명소": 0.7},
            "default": {} 
        }
        # 텍스트에 포함된 키워드로 스타일 매칭
        current_weight = style_weights["default"]
        for key in style_weights:
            if key in user_style:
                current_weight = style_weights[key]
                break
        
        scored_pois = []
        for poi in poi_list:
            category = poi.get("category", "기타")
            rating = poi.get("rating", 3.0)
            
            weight = current_weight.get(category, 1.0)
            score = rating * weight
            
            poi_with_score = poi.copy()
            poi_with_score['score'] = round(score, 2)
            scored_pois.append(poi_with_score)
            
        return sorted(scored_pois, key=lambda x: x['score'], reverse=True)