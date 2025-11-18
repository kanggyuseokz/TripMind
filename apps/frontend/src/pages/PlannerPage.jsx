// tripmind/apps/frontend/src/pages/PlannerPage.jsx
import React, { useState, useEffect } from 'react';

// --- 아이콘 컴포넌트들 ---
const LoaderIcon = () => <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>;
const MapPinIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>;
const CalendarIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>;
const UsersIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>;
const WandIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L11 10l-1.5 1.5 3.88 3.88 1.5-1.5 7.64-7.64a1.21 1.21 0 0 0 0-1.72Z"/><path d="m14 7 3 3"/><path d="M5 6v4"/><path d="M19 14v4"/><path d="M10 2v2"/><path d="M7 8H3"/><path d="M14 19h-4"/><path d="M17 11h-4"/></svg>;
const WalletIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>;
const EditIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4Z"/></svg>;
const FlightIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-1-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 5.2 1.8c.5.1 1-.1 1.3-.3l.5-.3c.4-.3.6-.7.5-1.2z"/></svg>;
const HotelIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 22v-6.57"/><path d="M12 11h.01"/><path d="M12 7h.01"/><path d="M14 15.43V22"/><path d="M15 16h.01"/><path d="M15 12h.01"/><path d="M15 8h.01"/><path d="M10 16.5V22"/><path d="M18 22v-6.57"/><path d="M2 12h20"/><path d="M22 12.07V12c0-4.42-4.48-8-10-8S2 7.58 2 12v.07"/><path d="M12 12h.01"/><path d="M12 16h.01"/></svg>;
const WeatherIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/><path d="M22 10a3 3 0 0 0-3-3h-2.26a.99.99 0 0 0-.5 1.79 3 3 0 0 0 2.76 4.21Z"/></svg>;
const RestaurantIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-6a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2v6"/><path d="M21 15v6"/><path d="M3 15v6"/><path d="M21 11.16V9a7 7 0 1 0-14 0v2.16"/><path d="M21 3v2"/><path d="M16 3v2"/><path d="M11 3v2"/><path d="M6 3v2"/><path d="M3 3v2"/></svg>;


// --- 폰트 및 공용 스타일 ---
// (이 컴포넌트는 App.jsx나 index.js에서 한 번만 호출되면 됩니다)
const GlobalStyles = () => {
  useEffect(() => {
    const fontLink = document.createElement("link");
    fontLink.href = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Noto+Sans+KR:wght@400;500;700;900&display=swap";
    fontLink.rel = "stylesheet";
    document.head.appendChild(fontLink);

    const styles = `
      body {
        font-family: 'Noto Sans KR', 'Inter', sans-serif;
      }
      .font-inter {
        font-family: 'Inter', sans-serif;
      }
      .input-field {
        width: 100%;
        padding: 0.75rem;
        padding-left: 3rem; /* 아이콘을 위한 공간 */
        border: 1px solid #D1D5DB; /* gray-300 */
        border-radius: 0.5rem; /* rounded-lg */
        box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); /* shadow-sm */
        transition: border-color 0.2s, box-shadow 0.2s;
      }
      .input-field:focus {
        outline: none;
        border-color: #2563EB; /* blue-600 */
        box-shadow: 0 0 0 2px #BFDBFE; /* blue-200 */
      }
      .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
      }
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
      }
    `;
    const styleSheet = document.createElement("style");
    styleSheet.innerText = styles;
    document.head.appendChild(styleSheet);
  }, []);

  return null;
};

// --- Helper 컴포넌트: InputGroup ---
const InputGroup = ({ label, icon, children }) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
    <div className="flex items-center relative">
      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
        {icon}
      </span>
      {children}
    </div>
  </div>
);

// --- Helper 컴포넌트: SummaryCard (결과 페이지용) ---
const SummaryCard = ({ title, icon, data }) => {
  let content;

  if (!data || Object.keys(data).length === 0) {
    content = <p className="text-gray-500">정보 없음</p>;
  } else if (title === '항공권') {
    content = (
      <>
        <p className="text-lg font-semibold text-gray-800">{data.route}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">₩{data.price_total?.toLocaleString()}</p>
        <p className="text-sm text-gray-500">({data.price_per_person?.toLocaleString()}원/인)</p>
      </>
    );
  } else if (title === '숙소') {
    content = (
      <>
        <p className="text-lg font-semibold text-gray-800 truncate">{data.name || '추천 숙소'}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">₩{data.priceTotal?.toLocaleString()}</p>
        <p className="text-sm text-gray-500">{data.nights}박 / ⭐️ {data.rating} ({data.review_count})</p>
      </>
    );
  } else if (title === '날씨') {
    content = (
      <>
        <p className="text-lg font-semibold text-gray-800">{data.condition}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">{data.average_temperature_celsius}°C</p>
        <p className="text-sm text-gray-500">{data.location}</p>
      </>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <div className="flex items-center text-gray-500 mb-3">
        {icon}
        <h3 className="ml-2 text-lg font-semibold">{title}</h3>
      </div>
      {content}
    </div>
  );
};


// -----------------------------------------------------------------
// --- 메인 플래너 페이지 컴포넌트 (Default Export) ---
// -----------------------------------------------------------------
export default function PlannerPage() {
  // 플래너 페이지 내부 상태 (폼 입력, 결과 등)
  const [step, setStep] = useState(1); // 1: 폼, 2: 로딩, 3: 결과
  const [origin, setOrigin] = useState('서울');
  const [destination, setDestination] = useState('도쿄');
  const [startDate, setStartDate] = useState('2026-01-26');
  const [endDate, setEndDate] = useState('2026-01-29');
  const [partySize, setPartySize] = useState(2);
  const [preferredStyleText, setPreferredStyleText] = useState('관광과 맛집 위주로 짜줘');
  const [budget, setBudget] = useState(1200000);
  
  const [tripPlan, setTripPlan] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStep(2); // 로딩 상태로 변경
    setError(null);
    setTripPlan(null);

    // 백엔드로 보낼 요청 Body (하이브리드 방식)
    const requestBody = {
      "origin": origin,
      "destination": destination,
      "start_date": startDate,
      "end_date": endDate,
      "party_size": parseInt(partySize, 10),
      "budget": parseInt(budget, 10),
      "preferred_style_text": preferredStyleText,
    };

    try {
      const response = await fetch('http://localhost:8080/api/trip/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || '알 수 없는 백엔드 오류');
      
      if (data.type === 'plan') {
        setTripPlan(data.content);
        setStep(3); // 결과 표시
      } else {
        throw new Error('예상치 못한 응답 타입입니다.');
      }
    } catch (err) {
      setError(err.message || '여행 계획 생성 중 오류가 발생했습니다.');
      setStep(1); // 오류 시 다시 폼으로
    }
  };

  // 폼 UI
  const renderForm = () => (
    <div className="w-full max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-2xl animate-fade-in">
      <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
        어디로 떠나시나요?
      </h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InputGroup label="출발지" icon={<MapPinIcon />}>
            <input type="text" value={origin} onChange={(e) => setOrigin(e.target.value)} className="input-field" required />
          </InputGroup>
          <InputGroup label="도착지" icon={<MapPinIcon />}>
            <input type="text" value={destination} onChange={(e) => setDestination(e.target.value)} className="input-field" required />
          </InputGroup>
        </div>
        <InputGroup label="여행 날짜" icon={<CalendarIcon />}>
          <div className="flex items-center space-x-2">
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="input-field w-full" required />
            <span className="text-gray-500">-</span>
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="input-field w-full" required />
          </div>
        </InputGroup>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InputGroup label="인원" icon={<UsersIcon />}>
            <input type="number" min="1" value={partySize} onChange={(e) => setPartySize(e.target.value)} className="input-field" required />
          </InputGroup>
          <InputGroup label="총 예산 (원)" icon={<WalletIcon />}>
            <input type="number" min="0" step="10000" value={budget} onChange={(e) => setBudget(e.target.value)} className="input-field" />
          </InputGroup>
        </div>
        <InputGroup label="여행 스타일" icon={<EditIcon />}>
          <textarea
            value={preferredStyleText}
            onChange={(e) => setPreferredStyleText(e.target.value)}
            className="input-field w-full h-24 resize-none"
            placeholder="예: 맛집 탐방과 쇼핑을 좋아해요. 휴양 위주로 부탁해요."
            required
          />
        </InputGroup>
        <button
          type="submit"
          disabled={step === 2}
          className={`w-full flex justify-center items-center text-white font-bold py-3 px-6 rounded-lg shadow-lg transition-all duration-300 text-lg
                      ${step === 2 ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
        >
          {step === 2 ? <LoaderIcon /> : <WandIcon />}
          <span className="ml-2">{step === 2 ? '여행 계획 생성 중...' : '나만의 여행 계획 생성하기'}</span>
        </button>
        {error && <div className="text-red-600 text-center font-medium">{error}</div>}
      </form>
    </div>
  );

  // 로딩 UI
  const renderLoading = () => (
    <div className="w-full max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-2xl flex flex-col items-center justify-center h-96">
      <LoaderIcon />
      <h2 className="text-2xl font-bold text-gray-700 mt-6">여행 계획 생성 중...</h2>
      <p className="text-gray-500 mt-2">항공권, 호텔, 날씨, POI 정보를 수집하고 있습니다.</p>
    </div>
  );

  // 결과 UI
  const renderResults = () => (
    <div className="w-full max-w-6xl mx-auto p-8 bg-white rounded-lg shadow-2xl animate-fade-in">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">{tripPlan.trip_summary}</h1>
          <p className="text-xl text-gray-600 mt-2">
            총 예상 경비: <span className="font-bold text-blue-600">₩{tripPlan.total_cost.toLocaleString()}</span>
          </p>
        </div>
        <button
          onClick={() => setStep(1)} // 다시 폼으로 돌아가기
          className="bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors"
        >
          다시 계획하기
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <SummaryCard title="항공권" icon={<FlightIcon />} data={tripPlan.raw_data.mcp_fetched_data.flight_quote} />
        <SummaryCard title="숙소" icon={<HotelIcon />} data={tripPlan.raw_data.mcp_fetched_data.hotel_quote} />
        <SummaryCard title="날씨" icon={<WeatherIcon />} data={tripPlan.raw_data.mcp_fetched_data.weather_info} />
      </div>
      <h2 className="text-3xl font-bold text-gray-800 mb-6">상세 일정표</h2>
      <div className="space-y-6">
        {tripPlan.schedule && tripPlan.schedule.map((dayPlan) => (
          <div key={dayPlan.day} className="p-6 bg-gray-50 rounded-lg shadow-md border border-gray-200">
            <h3 className="text-2xl font-semibold text-blue-700 mb-4">Day {dayPlan.day}</h3>
            <div className="space-y-4">
              {dayPlan.slots && dayPlan.slots.map((slot, index) => (
                <div key={index} className="flex items-start p-4 bg-white rounded-lg shadow-sm">
                  <div className="flex-shrink-0 w-24">
                    <span className="font-bold text-gray-800">{slot.slot_name}</span>
                  </div>
                  <div className="ml-4">
                    <h4 className="text-lg font-semibold text-gray-900">{slot.activity}</h4>
                    {slot.poi_details?.address && <p className="text-sm text-gray-500 mt-1">{slot.poi_details.address}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // --- 메인 렌더링 로직 ---
  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <GlobalStyles />
      {step === 1 && renderForm()}
      {step === 2 && renderLoading()}
      {step === 3 && tripPlan && renderResults()}
    </div>
  );
}