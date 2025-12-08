import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { Plane, Calendar, Users, Wallet, MapPin, ShoppingBag, Coffee, Car, Utensils, Home, ArrowRight, Check, Star, ChevronRight, Clock, BedDouble } from 'lucide-react';
import { adjustScheduleWithFlightTimes } from '../utils/scheduleUtils';
import ScheduleEditor from '../components/ScheduleEditor';

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

// ✅ 시간 포맷팅 함수
const formatTime = (isoString) => {
  if (!isoString) return '-';
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
  } catch {
    return '-';
  }
};

// ✅ 날짜 포맷팅 함수
const formatDate = (isoString) => {
  if (!isoString) return '-';
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  } catch {
    return '-';
  }
};

export default function ResultPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const tripData = location.state?.tripData;

  // 상태 관리: 현재 단계, 선택된 항목
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [selectedHotel, setSelectedHotel] = useState(null);
  
  // 원본 데이터 저장
  const [flightList, setFlightList] = useState([]);
  const [hotelList, setHotelList] = useState([]);
  const [finalPlan, setFinalPlan] = useState(null);
  const [tripDates, setTripDates] = useState(null);
  
  // 탭 상태 관리 (ViewTripPage 스타일)
  const [activeTab, setActiveTab] = useState('schedule');

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

useEffect(() => {
    if (!tripData) { 
        console.error("❌ [DEBUG] tripData가 없습니다.");
        navigate('/planner'); 
        return; 
    }

    console.log("🔍 [DEBUG] RAW tripData:", tripData);

    const mcpData = tripData.raw_data?.mcp_fetched_data || tripData.mcp_fetched_data;
    
    if (!mcpData) {
        console.error("❌ [DEBUG] mcp_fetched_data가 없습니다!");
        
        const flights = tripData.flight_candidates || tripData.flights || [];
        const hotels = tripData.hotel_candidates || tripData.hotels || [];
        const schedule = tripData.schedule || [];
        
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

    // ✅ 날짜 정보 추출
    const dates = mcpData.dates || { start: tripData.start_date, end: tripData.end_date };
    setTripDates(dates);
    console.log("📅 [DEBUG] Dates:", dates);

    // ✅ 항공/호텔 추출
    const flights = mcpData.flight_candidates || [];
    const hotels = mcpData.hotel_candidates || [];
    const schedule = mcpData.schedule || tripData.schedule || [];

    console.log("✈️ [DEBUG] Extracted Flights:", flights);
    console.log("🏨 [DEBUG] Extracted Hotels:", hotels.length, "개");

    setFlightList(flights);
    setHotelList(hotels);

    const planData = {
        destination: tripData.destination || "여행지",
        schedule: schedule,
        startDate: dates.start,
        endDate: dates.end,
        total_cost: tripData.total_cost || tripData.budget,
        pax: tripData.pax || tripData.party_size || 2,
        weatherByDate: mcpData.weather_by_date || {} // ✅ 날씨 추가
    };

    setFinalPlan(planData);

    // ✅ window 객체에 저장용 데이터 준비 (초기)
    window.currentTripData = {
        destination: planData.destination,
        start_date: dates.start || planData.startDate,
        end_date: dates.end || planData.endDate,
        pax: planData.pax,
        total_cost: planData.total_cost,
        trip_summary: `${planData.destination} 여행`,
        schedule: planData.schedule,
        raw_data: {
            mcp_fetched_data: mcpData,
            selected_flight: null,
            selected_hotel: null
        }
    };
    
    console.log("🔄 [WINDOW DATA] Initial save data:", window.currentTripData);

}, [tripData, navigate]);

  // [Step 1] 항공권 선택 핸들러
  const handleSelectFlight = (flight) => {
    console.log("✅ Selected Flight:", flight);
    setSelectedFlight(flight);
    if (finalPlan?.schedule && finalPlan.schedule.length > 0) {
      const adjustedSchedule = adjustScheduleWithFlightTimes(finalPlan.schedule, flight);
      setFinalPlan(prev => ({
        ...prev,
        schedule: adjustedSchedule
      }));

      if (window.currentTripData) {
        window.currentTripData.schedule = adjustedSchedule;
        window.currentTripData.raw_data.selected_flight = flight;
        console.log("💾 [WINDOW DATA] Schedule updated with flight times");
      }
      console.log("✅ [FLIGHT SELECT] 스케줄 조정 완료!");
    } else {
      console.warn("⚠️ [FLIGHT SELECT] 조정할 스케줄이 없습니다.");
      if (window.currentTripData) {
        window.currentTripDate.raw_data.selectedFlight = flight;
      }
    }
    
    setCurrentStep(1);
    window.scrollTo(0, 0);
  };

  // [Step 2] 호텔 선택 핸들러
  const handleSelectHotel = (hotel) => {
    console.log("✅ Selected Hotel:", hotel);
    setSelectedHotel(hotel);
    
    // ✅ window 데이터 업데이트
    if (window.currentTripData) {
      window.currentTripData.raw_data.selected_hotel = hotel;
      console.log("🔄 [WINDOW DATA] Updated with hotel:", window.currentTripData);
    }
    
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
                <p className="font-bold">⚠️ 데이터가 비어있습니다.</p>
            </div>
        )}

        <div className="space-y-4">
          {flightList.length > 0 ? (
            flightList.map((flight, idx) => (
              <div key={idx} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:border-blue-500 hover:shadow-md transition-all">
                <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
                  {/* 항공사 정보 */}
                  <div className="flex items-center gap-4 flex-1">
                    <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
                      <Plane size={32}/>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{flight.airline || "항공사 미정"}</h3>
                      <p className="text-gray-500 text-sm">{flight.origin} → {flight.destination}</p>
                    </div>
                  </div>

                  {/* ✅ 출입국 시간 표시 */}
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    {/* 출국 */}
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Plane size={14} className="text-blue-600" />
                        <span className="font-bold text-blue-900">출국</span>
                      </div>
                      <div className="flex items-center justify-between text-gray-700">
                        <div>
                          <div className="text-xs text-gray-500">출발</div>
                          <div className="font-bold">{formatTime(flight.outbound_departure_time)}</div>
                          <div className="text-xs text-gray-400">{formatDate(flight.outbound_departure_time)}</div>
                        </div>
                        <ArrowRight size={16} className="text-gray-400" />
                        <div className="text-right">
                          <div className="text-xs text-gray-500">도착</div>
                          <div className="font-bold">{formatTime(flight.outbound_arrival_time)}</div>
                          <div className="text-xs text-gray-400">{formatDate(flight.outbound_arrival_time)}</div>
                        </div>
                      </div>
                    </div>

                    {/* 입국 */}
                    {flight.inbound_departure_time && (
                      <div className="bg-green-50 p-3 rounded-lg">
                        <div className="flex items-center gap-2 mb-1">
                          <Plane size={14} className="text-green-600 transform rotate-180" />
                          <span className="font-bold text-green-900">입국</span>
                        </div>
                        <div className="flex items-center justify-between text-gray-700">
                          <div>
                            <div className="text-xs text-gray-500">출발</div>
                            <div className="font-bold">{formatTime(flight.inbound_departure_time)}</div>
                            <div className="text-xs text-gray-400">{formatDate(flight.inbound_departure_time)}</div>
                          </div>
                          <ArrowRight size={16} className="text-gray-400" />
                          <div className="text-right">
                            <div className="text-xs text-gray-500">도착</div>
                            <div className="font-bold">{formatTime(flight.inbound_arrival_time)}</div>
                            <div className="text-xs text-gray-400">{formatDate(flight.inbound_arrival_time)}</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* 가격 및 선택 버튼 */}
                  <div className="text-right">
                    <p className="text-2xl font-bold text-blue-600 mb-2">{formatPrice(flight.price_krw || flight.price)}원</p>
                    <button onClick={() => handleSelectFlight(flight)} className="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-700 transition-colors flex items-center gap-2">
                      선택하기 <ArrowRight size={18} />
                    </button>
                  </div>
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
  // [렌더링] Step 3: 최종 결과 화면 (ViewTripPage 스타일 탭)
  // ------------------------------------------------------------------
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {finalPlan?.destination} 여행 계획
          </h1>
          <p className="text-gray-600 flex items-center gap-2">
            <Calendar size={18} />
            {tripDates ? `${tripDates.start} ~ ${tripDates.end}` : '기간 미정'}
          </p>
        </div>

        {/* 메인 컨텐츠: 2열 그리드 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 왼쪽 사이드바 */}
          <div className="lg:col-span-1 space-y-6">
            {/* 활동 비율 카드 */}
            <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
              <h2 className="text-lg font-bold text-gray-900 mb-6">활동 비율</h2>
              
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
                
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <div className="text-4xl font-bold text-gray-900">100%</div>
                  <div className="text-sm text-gray-500">완료</div>
                </div>
              </div>

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

            {/* ✅ 여행 기간 카드 */}
            <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-purple-50 rounded-full flex items-center justify-center flex-shrink-0">
                  <Calendar className="text-purple-600" size={24} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-500">여행 기간</div>
                  <div className="text-lg font-bold text-gray-900">
                    {(() => {
                      if (!tripDates?.start || !tripDates?.end) return '기간 미정';
                      const start = new Date(tripDates.start);
                      const end = new Date(tripDates.end);
                      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
                      return `${days - 1}박 ${days}일`;
                    })()}
                  </div>
                  <div className="text-xs text-gray-400 mt-1 truncate">
                    {tripDates?.start} ~ {tripDates?.end}
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

          {/* 오른쪽: 탭 영역 (ViewTripPage 스타일) */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm p-6 sm:p-8 border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">여행 세부사항</h2>
              </div>

              {/* ✅ 탭 네비게이션 (ViewTripPage 스타일) */}
              <div className="flex gap-2 border-b border-gray-200 overflow-x-auto mb-6">
                {[
                  { id: 'schedule', label: '상세 일정', icon: <Calendar size={18} /> },
                  { id: 'flight', label: '항공권', icon: <Plane size={18} /> },
                  { id: 'hotel', label: '호텔', icon: <BedDouble size={18} /> }
                ].map((tab) => (
                  <button 
                    key={tab.id} 
                    onClick={() => setActiveTab(tab.id)} 
                    className={`flex items-center gap-2 px-6 py-4 font-bold text-sm transition-all border-b-2 whitespace-nowrap ${activeTab === tab.id ? 'border-black text-black' : 'border-transparent text-gray-400 hover:text-gray-600'}`}
                  >
                    {tab.icon} {tab.label}
                  </button>
                ))}
              </div>

              {/* ✅ 탭별 조건부 렌더링 (ViewTripPage 스타일) */}
              <div className="min-h-[400px]">
                {/* 상세 일정 탭 */}
                {activeTab === 'schedule' && (
                  <div className="animate-in fade-in">
                    {(!finalPlan?.schedule || finalPlan.schedule.length === 0) ? (
                      <div className="p-8 bg-red-50 text-red-600 rounded-xl border border-red-200">
                        <p className="font-bold">⚠️ 일정 데이터가 없습니다.</p>
                      </div>
                    ) : (
                      <div className="space-y-8 relative before:absolute before:inset-0 before:left-4 before:top-4 before:w-0.5 before:bg-gray-200 before:h-full">
                        {finalPlan.schedule.map((day, idx) => (
                          <div key={idx} className="relative pl-10">
                            <div className="absolute left-0 top-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md ring-4 ring-white z-10">
                              {day.day}
                            </div>

                            <div className="mb-4">
                              <h4 className="text-lg font-bold text-gray-900">{day.date || `Day ${day.day}`}</h4>
                              {/* ✅ 날씨 표시 */}
                              {finalPlan.weatherByDate && finalPlan.weatherByDate[day.full_date] && (
                                <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                                  <span>🌤️ {finalPlan.weatherByDate[day.full_date].condition}</span>
                                  <span>{finalPlan.weatherByDate[day.full_date].temp}°C</span>
                                </div>
                              )}
                            </div>

                            <div className="space-y-3">
                              {day.events?.map((event, eIdx) => (
                                <div key={eIdx} className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                                  <div className="flex gap-4">
                                    <div className="flex-shrink-0">
                                      {event.time_slot?.includes('오전') ? <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center text-xl">☀️</div> :
                                       event.time_slot?.includes('점심') ? <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center text-xl">🍽️</div> :
                                       event.time_slot?.includes('오후') ? <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-xl">☕</div> :
                                       event.time_slot?.includes('저녁') ? <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center text-xl">🌙</div> :
                                       <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center"><Clock size={20} className="text-gray-400" /></div>}
                                    </div>

                                    <div className="flex-1 min-w-0">
                                      <div className="font-bold text-gray-700 text-sm mb-1">{event.time_slot}</div>
                                      <div className="font-bold text-gray-900">{event.place_name || event.poi_name || event.description}</div>
                                      {(event.place_name || event.poi_name) && <div className="text-sm text-gray-500 mt-1">{event.description}</div>}
                                      {event.poi_rating && (
                                        <div className="flex items-center gap-1 mt-1 text-xs text-yellow-600">
                                          <Star size={12} fill="currentColor" />
                                          <span className="font-medium">{event.poi_rating}</span>
                                        </div>
                                      )}
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
                )}

                {/* 항공권 탭 */}
                {activeTab === 'flight' && (
                  <div className="space-y-6 animate-in fade-in">
                    {selectedFlight ? (
                      <div className="bg-white rounded-2xl overflow-hidden shadow-md border border-gray-200">
                        <div className="p-8">
                          <div className="flex items-center gap-4 mb-6">
                            <div className="w-14 h-14 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
                              <Plane size={28} />
                            </div>
                            <div>
                              <h4 className="text-2xl font-bold text-gray-900">{selectedFlight.airline || '항공편 정보'}</h4>
                              <p className="text-gray-500 font-medium">{selectedFlight.origin} → {selectedFlight.destination}</p>
                            </div>
                          </div>

                          {/* ✅ 출입국 시간 표시 */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                            {/* 출국 */}
                            <div className="bg-blue-50 p-4 rounded-xl">
                              <div className="flex items-center gap-2 mb-3">
                                <Plane size={16} className="text-blue-600" />
                                <span className="font-bold text-blue-900">출국</span>
                              </div>
                              <div className="space-y-2">
                                <div className="flex justify-between items-center">
                                  <div>
                                    <div className="text-xs text-gray-600">출발</div>
                                    <div className="text-lg font-bold text-gray-900">{formatTime(selectedFlight.outbound_departure_time)}</div>
                                    <div className="text-xs text-gray-500">{formatDate(selectedFlight.outbound_departure_time)}</div>
                                  </div>
                                  <ArrowRight size={20} className="text-gray-400" />
                                  <div className="text-right">
                                    <div className="text-xs text-gray-600">도착</div>
                                    <div className="text-lg font-bold text-gray-900">{formatTime(selectedFlight.outbound_arrival_time)}</div>
                                    <div className="text-xs text-gray-500">{formatDate(selectedFlight.outbound_arrival_time)}</div>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* 입국 */}
                            {selectedFlight.inbound_departure_time && (
                              <div className="bg-green-50 p-4 rounded-xl">
                                <div className="flex items-center gap-2 mb-3">
                                  <Plane size={16} className="text-green-600 transform rotate-180" />
                                  <span className="font-bold text-green-900">입국</span>
                                </div>
                                <div className="space-y-2">
                                  <div className="flex justify-between items-center">
                                    <div>
                                      <div className="text-xs text-gray-600">출발</div>
                                      <div className="text-lg font-bold text-gray-900">{formatTime(selectedFlight.inbound_departure_time)}</div>
                                      <div className="text-xs text-gray-500">{formatDate(selectedFlight.inbound_departure_time)}</div>
                                    </div>
                                    <ArrowRight size={20} className="text-gray-400" />
                                    <div className="text-right">
                                      <div className="text-xs text-gray-600">도착</div>
                                      <div className="text-lg font-bold text-gray-900">{formatTime(selectedFlight.inbound_arrival_time)}</div>
                                      <div className="text-xs text-gray-500">{formatDate(selectedFlight.inbound_arrival_time)}</div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>

                          <div className="flex items-center justify-between pt-6 border-t border-gray-100">
                            <div>
                              <p className="text-xs text-gray-400 mb-1">예상 가격 (1인, 왕복)</p>
                              <p className="text-3xl font-extrabold text-blue-600">
                                {(selectedFlight.price_krw || selectedFlight.price || 0).toLocaleString()}
                                <span className="text-lg font-medium text-gray-500 ml-1">원</span>
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center text-gray-500 py-10">항공편 정보가 없습니다.</div>
                    )}
                  </div>
                )}

                {/* 호텔 탭 */}
                {activeTab === 'hotel' && (
                  <div className="space-y-6 animate-in fade-in">
                    {selectedHotel ? (
                      <div className="bg-white rounded-2xl overflow-hidden shadow-md border border-gray-200">
                        <div className="flex flex-col md:flex-row h-full">
                          <div className="relative md:w-2/5 h-64 md:h-auto overflow-hidden">
                            <img src={selectedHotel.image || "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"} alt={selectedHotel.name} className="absolute inset-0 w-full h-full object-cover" />
                            <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur px-3 py-1.5 rounded-lg text-sm font-bold text-yellow-600 flex items-center gap-1">
                              <Star size={16} fill="currentColor" /> {selectedHotel.rating || 0}
                            </div>
                          </div>
                          <div className="p-8 flex-1 flex flex-col justify-center">
                            <div className="mb-6">
                              <h4 className="text-3xl font-bold text-gray-900 mb-2">{selectedHotel.name || '숙소 정보'}</h4>
                              <p className="text-gray-500 flex items-center gap-1.5">
                                <MapPin size={16} /> {selectedHotel.location || '위치 미정'}
                              </p>
                            </div>
                            <div className="flex items-center justify-between pt-6 border-t border-gray-100">
                              <div>
                                <p className="text-xs text-gray-400 mb-1">1박 기준 (세금 포함)</p>
                                <p className="text-3xl font-extrabold text-blue-600">
                                  {(selectedHotel.price || 0).toLocaleString()}
                                  <span className="text-lg font-medium text-gray-500 ml-1">원</span>
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center text-gray-500 py-10">숙소 정보가 없습니다.</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ✅ 저장 버튼 (Header와 동일한 로직) */}
        <div className="text-center mt-8 mb-4 flex gap-4 justify-center">
          <button 
            onClick={() => navigate('/saved')} 
            className="bg-gray-200 text-gray-700 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-300 transition-all"
          >
            목록으로
          </button>
          <button 
            onClick={async () => {
              try {
                const token = localStorage.getItem('token');
                if (!token) {
                  alert('로그인이 필요합니다.');
                  navigate('/login');
                  return;
                }

                // ✅ window 객체의 최신 데이터 사용 (Header와 동일)
                const tripData = window.currentTripData;
                if (!tripData) {
                  alert('저장할 여행 데이터가 없습니다.');
                  return;
                }

                console.log("💾 [PAGE SAVE] Using window data:", tripData);

                const response = await fetch('http://127.0.0.1:8080/api/trip/save', {
                  method: 'POST',
                  headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                  },
                  body: JSON.stringify(tripData)
                });

                if (response.ok) {
                  alert('여행 계획이 저장되었습니다! 🎉');
                  navigate('/saved');
                } else {
                  const errorData = await response.json().catch(() => ({}));
                  console.error('💾 [PAGE SAVE ERROR]:', errorData);
                  alert('저장에 실패했습니다: ' + (errorData.error || '알 수 없는 오류'));
                }
              } catch (error) {
                console.error('💾 [PAGE SAVE ERROR]:', error);
                alert('저장 중 오류가 발생했습니다.');
              }
            }}
            className="bg-gray-900 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-lg hover:bg-gray-800 transition-all"
          >
            여행 계획 저장하기
          </button>
        </div>
      </div>
    </div>
  );
}