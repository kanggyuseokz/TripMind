import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { Plane, Calendar, Users, Wallet, MapPin, ShoppingBag, Coffee, Car, Utensils, Home, ArrowRight, Check, Star, ChevronRight } from 'lucide-react';

// [UI 컴포넌트] 진행 단계 표시줄 (Wizard Steps)
const StepIndicator = ({ currentStep }) => {
  const steps = ['항공권 선택', '숙소 선택', '여행 일정 생성'];
  return (
    <div className="flex items-center justify-center mb-8">
      {steps.map((step, idx) => (
        <div key={idx} className="flex items-center">
          <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold text-sm ${idx <= currentStep ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-500'}`}>
            {idx + 1}
          </div>
          <div className={`ml-3 mr-3 font-medium ${idx <= currentStep ? 'text-blue-800' : 'text-gray-400'}`}>{step}</div>
          {idx < steps.length - 1 && <ChevronRight className="text-gray-300 mr-3" size={20} />}
        </div>
      ))}
    </div>
  );
};

export default function ResultPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const tripData = location.state?.tripData;

  // 상태 관리: 현재 단계, 선택된 항목
  const [currentStep, setCurrentStep] = useState(0); // 0: Flight, 1: Hotel, 2: Result
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [selectedHotel, setSelectedHotel] = useState(null);
  
  // 원본 데이터 저장
  const [flightList, setFlightList] = useState([]);
  const [hotelList, setHotelList] = useState([]);
  const [finalPlan, setFinalPlan] = useState(null);

  // [핵심] 데이터 찾기 헬퍼 함수
  const findDataKey = (obj, keyToFind) => {
    if (!obj || typeof obj !== 'object') return null;
    if (Array.isArray(obj)) return null;
    if (keyToFind in obj && obj[keyToFind]) return obj[keyToFind];
    
    const commonWrappers = ['data', 'mcp_fetched_data', 'raw_data', 'result', 'content'];
    for (const wrapper of commonWrappers) {
        if (obj[wrapper]) {
            const found = findDataKey(obj[wrapper], keyToFind);
            if (found) return found;
        }
    }
    return null;
  };

  // ResultPage.jsx의 useEffect 부분만 교체하세요

useEffect(() => {
    if (!tripData) { 
        console.error("❌ [DEBUG] tripData가 없습니다.");
        navigate('/planner'); 
        return; 
    }

    console.log("🔍 [DEBUG] RAW tripData:", tripData);
    console.log("🔍 [DEBUG] raw_data 존재:", !!tripData.raw_data);
    console.log("🔍 [DEBUG] mcp_fetched_data 존재:", !!tripData.raw_data?.mcp_fetched_data);

    // ✅ 안전한 접근: raw_data가 없을 수도 있음
    const mcpData = tripData.raw_data?.mcp_fetched_data || tripData.mcp_fetched_data;
    
    if (!mcpData) {
        console.error("❌ [DEBUG] mcp_fetched_data가 없습니다!");
        console.log("🔍 [DEBUG] tripData 전체 구조:", Object.keys(tripData));
        
        // ✅ 폴백: tripData에 직접 있을 수도 있음
        const flights = tripData.flight_candidates || tripData.flights || [];
        const hotels = tripData.hotel_candidates || tripData.hotels || [];
        const schedule = tripData.schedule || [];
        
        console.log("✈️ [DEBUG] Fallback Flights:", flights.length, "개");
        console.log("🏨 [DEBUG] Fallback Hotels:", hotels.length, "개");
        
        setFlightList(flights);
        setHotelList(hotels);
        setFinalPlan({
            destination: tripData.destination || "여행지",
            schedule: schedule,
            startDate: tripData.start_date,
            endDate: tripData.end_date,
            total_cost: tripData.total_cost || tripData.budget,
            pax: tripData.pax || tripData.party_size || 2
        });
        return;
    }

    // ✅ 항공/호텔 직접 추출
    const flights = mcpData.flight_candidates || [];
    const hotels = mcpData.hotel_candidates || [];
    const schedule = mcpData.schedule || tripData.schedule || [];

    console.log("✈️ [DEBUG] Extracted Flights:", flights.length, "개");
    console.log("🏨 [DEBUG] Extracted Hotels:", hotels.length, "개");
    console.log("📅 [DEBUG] Schedule:", schedule.length, "개");

    // ✅ 상태 업데이트
    setFlightList(flights);
    setHotelList(hotels);

    // ✅ finalPlan 설정
    setFinalPlan({
        destination: tripData.destination || "여행지",
        schedule: schedule,
        startDate: tripData.start_date,
        endDate: tripData.end_date,
        total_cost: tripData.total_cost || tripData.budget,
        pax: tripData.pax || tripData.party_size || 2
    });

}, [tripData, navigate]);

  // [Step 1] 항공권 선택 핸들러
  const handleSelectFlight = (flight) => {
    console.log("✅ Selected Flight:", flight);
    setSelectedFlight(flight);
    setCurrentStep(1);
    window.scrollTo(0, 0);
  };

  // [Step 2] 호텔 선택 핸들러
  const handleSelectHotel = (hotel) => {
    console.log("✅ Selected Hotel:", hotel);
    setSelectedHotel(hotel);
    setCurrentStep(2);
    window.scrollTo(0, 0);
  };

  // 가격 포맷팅
  const formatPrice = (price) => (price ? Number(price).toLocaleString() : '0');

  // 활동 비율 데이터
  const activityData = [
    { name: '관광', value: 40, color: '#6366F1' },
    { name: '쇼핑', value: 30, color: '#A855F7' },
    { name: '휴식', value: 30, color: '#EC4899' }
  ];

  // ------------------------------------------------------------------
  // [렌더링] Step 1: 항공권 선택 화면
  // ------------------------------------------------------------------
  if (currentStep === 0) {
    return (
      <div className="w-full max-w-5xl mx-auto p-6 min-h-screen bg-gray-50">
        <StepIndicator currentStep={0} />
        <h2 className="text-2xl font-bold mb-6 text-gray-800 text-center">🛫 최적의 항공권을 선택해주세요</h2>
        
        {flightList.length === 0 && (
            <div className="mb-4 p-4 bg-yellow-50 text-yellow-800 text-xs rounded overflow-auto max-h-40">
                <p className="font-bold">⚠️ 데이터가 비어있습니다. Console을 확인하세요.</p>
                <pre>{JSON.stringify(tripData, null, 2)}</pre>
            </div>
        )}

        <div className="space-y-4">
          {flightList.length > 0 ? (
            flightList.map((flight, idx) => (
              <div key={idx} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:border-blue-500 hover:shadow-md transition-all flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-4 flex-1">
                  <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center text-blue-600"><Plane size={32}/></div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{flight.airline || "항공사 미정"}</h3>
                    <p className="text-gray-500 text-sm">{flight.route}</p>
                    <div className="flex gap-4 mt-2 text-sm text-gray-600">
                      <span>⏱ {flight.duration || '정보 없음'}</span>
                      <span>🚀 {flight.departure_time ? flight.departure_time.split('T')[1].slice(0,5) : '-'} 출발</span>
                      <span>🛬 {flight.arrival_time ? flight.arrival_time.split('T')[1].slice(0,5) : '-'} 도착</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-blue-600 mb-2">{formatPrice(flight.price || flight.price_total)}원</p>
                  <button onClick={() => handleSelectFlight(flight)} className="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-700 transition-colors flex items-center gap-2">
                    선택하기 <ArrowRight size={18} />
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-20 text-gray-500 bg-white rounded-xl shadow-sm">
              <p className="text-lg">검색된 항공권이 없습니다.</p>
              <button onClick={() => setCurrentStep(1)} className="mt-4 text-blue-600 underline">항공권 없이 진행하기</button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // ------------------------------------------------------------------
  // [렌더링] Step 2: 호텔 선택 화면
  // ------------------------------------------------------------------
  if (currentStep === 1) {
    return (
      <div className="w-full max-w-5xl mx-auto p-6 min-h-screen bg-gray-50">
        <StepIndicator currentStep={1} />
        <h2 className="text-2xl font-bold mb-6 text-gray-800 text-center">🏨 마음에 드는 숙소를 골라보세요</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {hotelList.length > 0 ? (
            hotelList.map((hotel, idx) => (
              <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-all group flex flex-col">
                <div className="h-48 bg-gray-200 relative">
                  <img src={hotel.image || "https://via.placeholder.com/400x300?text=Hotel"} alt={hotel.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                  <div className="absolute top-3 right-3 bg-white/90 px-2 py-1 rounded-lg text-sm font-bold text-yellow-600 flex items-center gap-1">
                    <Star size={14} fill="currentColor" /> {hotel.rating}
                  </div>
                </div>
                <div className="p-5 flex-1 flex flex-col">
                  <h3 className="text-lg font-bold text-gray-900 mb-1 line-clamp-1">{hotel.name}</h3>
                  <p className="text-gray-500 text-sm flex items-center gap-1 mb-4"><MapPin size={14} /> {hotel.location}</p>
                  <div className="mt-auto flex items-center justify-between pt-4 border-t border-gray-100">
                    <p className="text-xl font-bold text-blue-600">{formatPrice(hotel.price)}원 <span className="text-xs text-gray-400 font-normal">/1박</span></p>
                    <button onClick={() => handleSelectHotel(hotel)} className="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-800 transition-colors">
                      선택
                    </button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center py-20 text-gray-500 bg-white rounded-xl shadow-sm">
              <p className="text-lg">검색된 숙소가 없습니다.</p>
              <button onClick={() => setCurrentStep(2)} className="mt-4 text-blue-600 underline">숙소 없이 진행하기</button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // ------------------------------------------------------------------
  // [렌더링] Step 3: 최종 결과 화면 (새 UI)
  // ------------------------------------------------------------------
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {finalPlan?.destination} 여행 계획
          </h1>
          <p className="text-gray-600">
            {finalPlan?.startDate} ~ {finalPlan?.endDate}
          </p>
        </div>

        {/* 메인 컨텐츠: 2열 그리드 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 왼쪽 사이드바 */}
          <div className="lg:col-span-1 space-y-6">
            {/* 활동 비율 카드 */}
            <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
              <h2 className="text-lg font-bold text-gray-900 mb-6">활동 비율</h2>
              
              {/* 도넛 차트 */}
              <div className="relative mb-6">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={activityData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {activityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                
                {/* 중앙 텍스트 */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <div className="text-4xl font-bold text-gray-900">100%</div>
                  <div className="text-sm text-gray-500">완료</div>
                </div>
              </div>

              {/* 범례 */}
              <div className="space-y-3">
                {activityData.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-sm text-gray-700">{item.name}</span>
                    </div>
                    <span className="text-sm font-bold text-gray-900">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* 인원 카드 */}
            <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center flex-shrink-0">
                  <Users className="text-blue-600" size={24} />
                </div>
                <div>
                  <div className="text-sm text-gray-500">인원</div>
                  <div className="text-2xl font-bold text-gray-900">{finalPlan?.pax || 2}명</div>
                </div>
              </div>
            </div>

            {/* 여행 기간 카드 */}
            <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-purple-50 rounded-full flex items-center justify-center flex-shrink-0">
                  <Calendar className="text-purple-600" size={24} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-500">여행 기간</div>
                  <div className="text-lg font-bold text-gray-900">
                    {(() => {
                      if (!finalPlan?.startDate || !finalPlan?.endDate) return '정보 없음';
                      const start = new Date(finalPlan.startDate);
                      const end = new Date(finalPlan.endDate);
                      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
                      return `${days - 1}박 ${days}일`;
                    })()}
                  </div>
                  <div className="text-xs text-gray-400 mt-1 truncate">
                    {finalPlan?.startDate} ~ {finalPlan?.endDate}
                  </div>
                </div>
              </div>
            </div>

            {/* 1인 예산 카드 */}
            <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-green-50 rounded-full flex items-center justify-center flex-shrink-0">
                  <Wallet className="text-green-600" size={24} />
                </div>
                <div>
                  <div className="text-sm text-gray-500">1인 예산</div>
                  <div className="text-xl font-bold text-gray-900">
                    {Math.floor((finalPlan?.total_cost || 1000000) / (finalPlan?.pax || 2)).toLocaleString()} KRW
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 오른쪽: 일정표 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm p-6 sm:p-8 border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">일정표</h2>
              </div>

              {/* 탭 */}
              <div className="flex gap-6 border-b border-gray-200 mb-6 overflow-x-auto">
                <button className="pb-3 px-1 border-b-2 border-blue-600 text-blue-600 font-medium whitespace-nowrap">
                  상세 일정
                </button>
                <button className="pb-3 px-1 text-gray-500 hover:text-gray-700 transition-colors whitespace-nowrap">
                  항공권 추천
                </button>
                <button className="pb-3 px-1 text-gray-500 hover:text-gray-700 transition-colors whitespace-nowrap">
                  숙소 추천
                </button>
              </div>

              {/* 일정 타임라인 */}
              {(!finalPlan?.schedule || finalPlan.schedule.length === 0) ? (
                <div className="p-8 bg-red-50 text-red-600 rounded-xl border border-red-200">
                  <p className="font-bold">⚠️ 일정 데이터가 없습니다.</p>
                  <p className="text-sm mt-1">콘솔 로그를 확인해주세요.</p>
                </div>
              ) : (
                <div className="space-y-8">
                  {finalPlan.schedule.map((day, idx) => (
                    <div key={idx} className="relative pl-8 border-l-2 border-blue-200">
                      <div className="absolute -left-4 top-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md">
                        {day.day}
                      </div>

                      <div className="mb-4">
                        <div className="text-lg font-bold text-gray-900">{day.day}일차</div>
                        <div className="text-sm text-gray-500">{day.date}</div>
                      </div>

                      <div className="space-y-3">
                        {day.events?.map((event, eIdx) => (
                          <div key={eIdx} className="bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors">
                            <div className="flex gap-4">
                              <div className="flex-shrink-0">
                                {event.time_slot === '오전' && <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center text-xl">☀️</div>}
                                {event.time_slot === '점심' && <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center text-xl">🍽️</div>}
                                {event.time_slot === '오후' && <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-xl">☕</div>}
                                {event.time_slot === '저녁' && <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center text-xl">🌙</div>}
                              </div>

                              <div className="flex-1 min-w-0">
                                <div className="font-bold text-gray-700 text-sm mb-1">{event.time_slot}</div>
                                <div className="font-bold text-gray-900">{event.place_name || event.description}</div>
                                {event.place_name && <div className="text-sm text-gray-500 mt-1">{event.description}</div>}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}