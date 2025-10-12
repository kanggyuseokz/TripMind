import random

class ScoringService:
    """
    여행 경비 계산 및 POI 후보 점수화를 담당하는 서비스 클래스.
    재정 및 추천 알고리즘의 핵심 엔진 역할을 합니다.
    """

    def calculate_total_cost(self, flight_quote, hotel_quote, trip_duration_days, num_travelers, budget_level, destination_info):
        """
        여행 총 경비를 계산합니다.

        Args:
            flight_quote (dict): 항공편 견적 정보 (e.g., {'price': 240000}).
            hotel_quote (dict): 숙소 견적 정보 (e.g., {'total_price': 270000}).
            trip_duration_days (int): 여행 기간 (일).
            num_travelers (int): 여행자 수.
            budget_level (str): 예산 수준 ('economical', 'moderate', 'luxury').
            destination_info (dict): 목적지 물가 정보 (미구현, 예시 데이터 사용).

        Returns:
            dict: 총 경비와 각 항목별 비용 정보.
        """
        # 1. 고정 비용 합산 (항공 + 숙소)
        flight_cost = flight_quote.get('price', 0) * num_travelers
        hotel_cost = hotel_quote.get('total_price', 0)
        fixed_costs = flight_cost + hotel_cost

        # 2. 추정 비용 계산 (식비, 교통, 액티비티)
        # 예산 수준 및 목적지 물가에 따라 일일 추정 비용을 설정합니다. (현재는 예시 값 사용)
        daily_spending_per_person = {
            'economical': 80000,
            'moderate': 150000,
            'luxury': 300000
        }.get(budget_level, 150000)

        # 각 항목별 가중치 적용
        estimated_food_cost = (daily_spending_per_person * 0.4) * trip_duration_days * num_travelers
        estimated_transport_cost = (daily_spending_per_person * 0.2) * trip_duration_days * num_travelers
        estimated_activity_cost = (daily_spending_per_person * 0.4) * trip_duration_days * num_travelers
        
        estimated_costs = estimated_food_cost + estimated_transport_cost + estimated_activity_cost

        # 3. 최종 총 경비
        total_cost = fixed_costs + estimated_costs

        return {
            "total_cost": total_cost,
            "costs_by_category": {
                "flight": flight_cost,
                "hotel": hotel_cost,
                "food": estimated_food_cost,
                "local_transport": estimated_transport_cost,
                "activities": estimated_activity_cost
            }
        }

    def calculate_cost_breakdown(self, costs_by_category):
        """
        항목별 비용 비중(백분율)을 계산하여 차트 데이터 구조로 반환합니다.

        Args:
            costs_by_category (dict): 항목별 비용 데이터.

        Returns:
            list: 프론트엔드 차트 렌더링을 위한 데이터.
                   e.g., [{"name": "항공", "value": 30.0}, ...]
        """
        total_cost = sum(costs_by_category.values())
        if total_cost == 0:
            return []

        category_map = {
            "flight": "항공",
            "hotel": "숙소",
            "food": "식비",
            "local_transport": "현지 교통",
            "activities": "액티비티"
        }

        breakdown = []
        for category, cost in costs_by_category.items():
            percentage = round((cost / total_cost) * 100, 1)
            breakdown.append({
                "name": category_map.get(category, category),
                "value": percentage
            })
        return breakdown

    def score_poi_candidates(self, poi_list, user_preferred_style):
        """
        사용자 선호도와 POI 데이터를 기반으로 각 POI에 점수를 매깁니다.

        Args:
            poi_list (list): MCP에서 수집된 POI 후보 리스트.
                             (e.g., [{'name': '오사카성', 'category': 'landmark', 'rating': 4.5}, ...])
            user_preferred_style (str): 사용자 선호 여행 스타일 ('휴식', '관광', '맛집').

        Returns:
            list: 점수가 매겨지고 내림차순으로 정렬된 POI 리스트.
        """
        style_category_map = {
            '관광': ['landmark', 'museum', 'park'],
            '맛집': ['restaurant', 'cafe', 'bar'],
            '휴식': ['park', 'cafe', 'spa']
        }
        
        preferred_categories = style_category_map.get(user_preferred_style, [])
        
        scored_pois = []
        for poi in poi_list:
            score = 0
            # 1. 선호도 점수: POI 카테고리가 사용자 선호 스타일과 일치하면 높은 점수 부여
            if poi.get('category') in preferred_categories:
                score += 50
            
            # 2. 평점 점수: 평점을 점수에 반영 (평점 1점당 10점)
            score += poi.get('rating', 3.0) * 10
            
            # 3. 인기도/무작위성 점수: 점수 다양성을 위해 약간의 무작위성 추가
            score += random.uniform(0, 10)
            
            poi['score'] = score
            scored_pois.append(poi)
            
        # 점수가 높은 순으로 정렬
        scored_pois.sort(key=lambda x: x['score'], reverse=True)
        return scored_pois
