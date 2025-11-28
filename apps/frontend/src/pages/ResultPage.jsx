import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
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

  useEffect(() => {
    if (!tripData) { 
        console.error("❌ [DEBUG] tripData가 없습니다. Planner로 리다이렉트합니다.");
        navigate('/planner'); 
        return; 
    }

    console.log("🔍 [DEBUG] RAW tripData:", tripData);

    // 🚀 [수정됨] 데이터 우선순위 변경: MCP에서 가져온 데이터를 최우선으로 사용
    // tripData(전체)에서 찾으면 LLM raw 데이터를 먼저 찾을 위험이 있으므로,
    // mcp_fetched_data 내부를 먼저 타겟팅합니다.
    const mcpSource = tripData.raw_data?.mcp_fetched_data || tripData.mcp_fetched_data || tripData;
    
    // 1. 항공권 리스트 (MCP 데이터 우선 탐색)
    let flights = findDataKey(mcpSource, 'flight_candidates');
    if (!flights || flights.length === 0) {
        const quote = findDataKey(mcpSource, 'flight_quote');
        if (quote && Object.keys(quote).length > 0) flights = [quote];
        else flights = findDataKey(tripData, 'flights') || []; // Fallback to root
    }
    console.log("✈️ [DEBUG] Extracted Flights:", flights);
    setFlightList(flights || []);

    // 2. 호텔 리스트 (MCP 데이터 우선 탐색)
    let hotels = findDataKey(mcpSource, 'hotel_candidates');
    if (!hotels || hotels.length === 0) {
        hotels = findDataKey(mcpSource, 'hotel_quote');
        if (!hotels || hotels.length === 0) hotels = findDataKey(tripData, 'hotels') || []; // Fallback to root
    }
    console.log("🏨 [DEBUG] Extracted Hotels:", hotels);
    setHotelList(hotels || []);

    // 3. 일정 (Schedule) - 여기가 문제였음
    // mcpSource에서 schedule을 먼저 찾아야 'Enriched(맛집 포함)' 일정을 가져옵니다.
    let schedule = findDataKey(mcpSource, 'schedule');
    
    // MCP에 스케줄이 없으면(에러 등), 그때 LLM raw 스케줄을 사용 (Fallback)
    if (!schedule || schedule.length === 0) {
        console.warn("⚠️ [DEBUG] MCP 스케줄 없음. LLM 기본 스케줄 사용.");
        schedule = findDataKey(tripData, 'schedule');
        // 더 깊숙한 곳 확인
        if (!schedule) {
             const llm = findDataKey(tripData, 'llm_parsed_data');
             if (llm && llm.schedule) schedule = llm.schedule;
        }
    }
    console.log("📅 [DEBUG] Final Schedule Data:", schedule);

    // 메타 정보 찾기
    const dest = findDataKey(tripData, 'destination') || "여행지";
    const startDate = findDataKey(tripData, 'start_date') || tripData.startDate;
    const endDate = findDataKey(tripData, 'end_date') || tripData.endDate;
    
    const dates = findDataKey(tripData, 'dates');
    const finalStart = dates?.start || startDate;
    const finalEnd = dates?.end || endDate;

    setFinalPlan({
        destination: dest,
        schedule: schedule || [],
        startDate: finalStart,
        endDate: finalEnd,
        total_cost: tripData.total_cost || 0
    });

  }, [tripData, navigate]);

  // [Step 1] 항공권 선택 핸들러
  const handleSelectFlight = (flight) => {
    console.log("✅ Selected Flight:", flight);
    setSelectedFlight(flight);
    setCurrentStep(1); // 호텔 선택 단계로 이동
    window.scrollTo(0, 0);
  };

  // [Step 2] 호텔 선택 핸들러
  const handleSelectHotel = (hotel) => {
    console.log("✅ Selected Hotel:", hotel);
    setSelectedHotel(hotel);
    setCurrentStep(2); // 결과 페이지로 이동
    window.scrollTo(0, 0);
  };

  // 가격 포맷팅
  const formatPrice = (price) => (price ? Number(price).toLocaleString() : '0');

  // ------------------------------------------------------------------
  // [렌더링] Step 1: 항공권 선택 화면
  // ------------------------------------------------------------------
  if (currentStep === 0) {
    return (
      <div className="w-full max-w-5xl mx-auto p-6 min-h-screen bg-gray-50">
        <StepIndicator currentStep={0} />
        <h2 className="text-2xl font-bold mb-6 text-gray-800 text-center">🛫 최적의 항공권을 선택해주세요</h2>
        
        {/* 디버깅용: 데이터가 비어있을 때 원시 데이터 확인용 버튼 (개발 중에만 보임) */}
        {flightList.length === 0 && (
            <div className="mb-4 p-4 bg-yellow-50 text-yellow-800 text-xs rounded overflow-auto max-h-40">
                <p className="font-bold">⚠️ 데이터가 비어있습니다. Console을 확인하세요. (tripData dump below)</p>
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
  // [렌더링] Step 3: 최종 결과 화면 (기존 ResultPage UI 재사용)
  // ------------------------------------------------------------------
  return (
    <div className="w-full max-w-7xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden animate-fade-in relative pb-12 my-8">
      {/* 상단 배너 */}
      <div className="relative h-80 bg-cover bg-center" style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1920&q=80)' }}>
        <div className="absolute inset-0 bg-black/40"></div>
        <div className="absolute bottom-8 left-8 text-white">
          <h1 className="text-4xl font-extrabold mb-2">{finalPlan?.destination} 여행 계획</h1>
          <p className="text-lg opacity-90">{finalPlan?.startDate} ~ {finalPlan?.endDate}</p>
        </div>
      </div>

      <div className="p-8">
        <div className="mb-10">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">선택하신 예약 정보</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 선택한 항공권 카드 */}
            <div className="bg-blue-50 p-6 rounded-xl border border-blue-100">
              <h3 className="font-bold text-blue-800 mb-4 flex items-center gap-2"><Plane size={20}/> 선택한 항공권</h3>
              {selectedFlight ? (
                <div>
                  <p className="text-xl font-bold text-gray-900 mb-1">{selectedFlight.airline}</p>
                  <p className="text-gray-600 mb-4">{selectedFlight.route}</p>
                  <div className="flex justify-between items-end">
                    <p className="text-sm text-gray-500">{selectedFlight.departure_time?.split('T')[1].slice(0,5)} 출발</p>
                    <p className="text-2xl font-bold text-blue-600">{formatPrice(selectedFlight.price || selectedFlight.price_total)}원</p>
                  </div>
                </div>
              ) : <p className="text-gray-500">선택 안 함</p>}
            </div>

            {/* 선택한 호텔 카드 */}
            <div className="bg-orange-50 p-6 rounded-xl border border-orange-100">
              <h3 className="font-bold text-orange-800 mb-4 flex items-center gap-2"><Home size={20}/> 선택한 숙소</h3>
              {selectedHotel ? (
                <div>
                  <p className="text-xl font-bold text-gray-900 mb-1">{selectedHotel.name}</p>
                  <p className="text-gray-600 mb-4 flex items-center gap-1"><Star size={14} className="text-yellow-500" fill="currentColor"/> {selectedHotel.rating}</p>
                  <div className="flex justify-between items-end">
                    <p className="text-sm text-gray-500">{selectedHotel.location}</p>
                    <p className="text-2xl font-bold text-orange-600">{formatPrice(selectedHotel.price)}원</p>
                  </div>
                </div>
              ) : <p className="text-gray-500">선택 안 함</p>}
            </div>
          </div>
        </div>

        {/* 일정표 */}
        <h2 className="text-2xl font-bold text-gray-800 mb-6">상세 일정표</h2>
        
        {/* [디버깅] 화면에 데이터가 없는 경우 메시지 출력 */}
        {(!finalPlan?.schedule || finalPlan.schedule.length === 0) ? (
            <div className="p-8 bg-red-50 text-red-600 rounded-xl border border-red-200">
                <p className="font-bold">⚠️ 일정 데이터가 없습니다.</p>
                <p className="text-sm mt-1">콘솔 로그([DEBUG])를 확인해주세요. 백엔드에서 schedule 키가 누락되었을 수 있습니다.</p>
            </div>
        ) : (
            <div className="space-y-8 border-l-2 border-gray-200 pl-8 ml-4">
            {finalPlan.schedule.map((day, idx) => (
                <div key={idx} className="relative">
                <div className="absolute -left-[41px] top-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md ring-4 ring-white">{day.day}</div>
                <h3 className="text-lg font-bold text-gray-900 mb-4">{day.date}</h3>
                <div className="space-y-4">
                    {day.events?.map((event, eIdx) => (
                    <div key={eIdx} className="bg-gray-50 p-4 rounded-xl border border-gray-100 flex gap-4">
                        <div className="font-bold text-gray-700 w-16 shrink-0">{event.time_slot}</div>
                        <div>
                        <p className="font-bold text-gray-900">{event.place_name || event.description}</p>
                        {event.place_name && <p className="text-sm text-gray-500 mt-1">{event.description}</p>}
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
  );
}