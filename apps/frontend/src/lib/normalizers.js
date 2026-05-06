const CHART_COLORS = ['#4F46E5', '#7C3AED', '#F59E0B', '#10B981'];

const STYLE_LABELS = {
  sightseeing: '관광형',
  relaxation: '휴양형',
  activity: '액티비티형',
  foodie: '미식형',
  shopping: '쇼핑형',
};

// API 응답 → UI에서 사용하는 일관된 여행 데이터 형태로 변환
export const normalizeTrip = (data) => {
  const budget = parseInt(data.budget || data.total_cost || 0, 10);
  const partySize = parseInt(data.pax || data.party_size || data.head_count || 1, 10);
  const totalCost = data.budget || data.total_cost || budget * partySize;

  let durationText = '';
  if (data.start_date && data.end_date) {
    const nights = Math.ceil((new Date(data.end_date) - new Date(data.start_date)) / 86400000);
    durationText = `${nights}박 ${nights + 1}일`;
  }

  const mcpData = (data.raw_data || {}).mcp_fetched_data || {};

  const flights =
    mcpData.flight_quote && Object.keys(mcpData.flight_quote).length > 0
      ? [mcpData.flight_quote]
      : (mcpData.flight_candidates || []).slice(0, 1);

  const hotels = Array.isArray(mcpData.hotel_quote)
    ? mcpData.hotel_quote.slice(0, 1)
    : (mcpData.hotel_candidates || []).slice(0, 1);

  const rawStyle =
    data.travel_style ||
    (data.raw_data || {}).travel_style ||
    mcpData.travel_style ||
    'sightseeing';

  const rawBreakdown = mcpData.cost_breakdown_chart || [];
  const activityDistribution =
    rawBreakdown.length > 0
      ? rawBreakdown.map((item, i) => ({
          name: item.category,
          value: item.percentage,
          color: CHART_COLORS[i % CHART_COLORS.length],
        }))
      : null;

  return {
    id: data.id,
    destination: data.destination || '',
    trip_summary: data.trip_summary || `${data.destination} 여행`,
    total_cost: totalCost,
    per_person_budget: budget,
    startDate: data.start_date,
    endDate: data.end_date,
    durationText: durationText || '기간 미정',
    head_count: partySize,
    activity_distribution: activityDistribution,
    flights,
    hotels,
    schedule: data.schedule || [],
    weatherByDate: mcpData.weather_by_date || {},
    poi_list: mcpData.poi_list || [],
    travel_style: STYLE_LABELS[rawStyle] || rawStyle,
    selected_flight_cost: data.selected_flight_cost || 0,
    selected_hotel_cost: data.selected_hotel_cost || 0,
    other_costs: data.other_costs || 0,
    cost_calculation: data.cost_calculation || null,
  };
};

// 유저 프로필 정규화
export const normalizeUser = (data) => ({
  id: data.id,
  username: data.username,
  email: data.email,
  profileImage: data.profile_image,
});
