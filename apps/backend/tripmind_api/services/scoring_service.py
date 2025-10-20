class ScoringService:
    """
    여행 경비를 계산하고, 사용자의 선호도에 따라 POI의 점수를 매기는 서비스.
    TripService에 필요한 분석 데이터를 제공합니다.
    """

    # 목적지별 하루 추정 비용 (1인 기준, KRW)
    # Mock Data 나중에 API로 교체
    COST_ESTIMATES_PER_DAY = {
        "도쿄": {"food": 80000, "transport": 15000, "activity": 30000},
        "오사카": {"food": 70000, "transport": 18000, "activity": 35000},
        "강릉": {"food": 60000, "transport": 20000, "activity": 25000},
        "default": {"food": 75000, "transport": 15000, "activity": 30000},
    }

    def calculate_total_cost(
        self,
        flight_quote: dict | None,
        hotel_quote: dict | None,
        duration_days: int,
        party_size: int,
        destination: str
    ) -> dict:
        """
        여행의 총 경비를 계산합니다.
        - 고정 비용: 항공, 숙소
        - 추정 비용: 식비, 현지 교통비, 액티비티 비용
        """
        flight_cost = flight_quote.get("price_total", 0) if flight_quote else 0
        hotel_cost = hotel_quote.get("priceTotal", 0) if hotel_quote else 0

        # 목적지에 맞는 하루 추정 비용 가져오기
        estimates = self.COST_ESTIMATES_PER_DAY.get(destination, self.COST_ESTIMATES_PER_DAY["default"])
        
        food_cost = estimates["food"] * duration_days * party_size
        transport_cost = estimates["transport"] * duration_days * party_size
        activity_cost = estimates["activity"] * duration_days * party_size
        
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
        (예: '맛집' 스타일이면 '맛집' 카테고리 POI에 높은 가중치 부여)
        """
        # 💡 스타일별 가중치를 더 명확하게 정의
        style_weights = {
            "맛집": {"맛집": 1.5, "음식점": 1.5, "카페": 1.2, "관광명소": 1.0},
            "관광": {"관광명소": 1.5, "문화시설": 1.3, "맛집": 0.8, "음식점": 0.8},
            "휴식": {"카페": 1.5, "공원": 1.3, "관광명소": 0.7},
            "default": {} # 기본 가중치는 모두 1.0
        }
        weights = style_weights.get(user_style, style_weights["default"])
        
        scored_pois = []
        for poi in poi_list:
            # API가 반환하는 다양한 카테고리 이름에 대응
            category = poi.get("category", "기타")
            rating = poi.get("rating", 3.0)
            
            # 해당 카테고리에 대한 가중치를 가져오고, 없으면 기본값 1.0 사용
            weight = weights.get(category, 1.0)
            
            # 기본 점수 = 평점 * 가중치
            score = rating * weight
            
            poi_with_score = poi.copy()
            poi_with_score['score'] = round(score, 2)
            scored_pois.append(poi_with_score)
            
        # 최종 점수가 높은 순으로 정렬하여 반환
        return sorted(scored_pois, key=lambda x: x['score'], reverse=True)

