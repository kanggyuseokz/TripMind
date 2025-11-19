// apps/frontend/src/pages/PlannerPage.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

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

// --- 헬퍼 컴포넌트 ---
const InputGroup = ({ label, icon, children }) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
    <div className="flex items-center relative">
      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">{icon}</span>
      {children}
    </div>
  </div>
);

const SummaryCard = ({ title, icon, data }) => (
  <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
    <div className="flex items-center text-gray-500 mb-3">
      {icon}
      <h3 className="ml-2 text-lg font-semibold">{title}</h3>
    </div>
    <p className="text-gray-800">{data ? JSON.stringify(data).substring(0, 50) + "..." : "정보 없음"}</p>
  </div>
);

export default function PlannerPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const initialPrompt = location.state?.initialPrompt || '';

  const [step, setStep] = useState(1);
  const [origin, setOrigin] = useState('서울');
  const [destination, setDestination] = useState('도쿄');
  const [startDate, setStartDate] = useState('2026-01-26');
  const [endDate, setEndDate] = useState('2026-01-29');
  const [partySize, setPartySize] = useState(2);
  const [preferredStyleText, setPreferredStyleText] = useState(initialPrompt);
  const [budget, setBudget] = useState(1200000);
  
  const [tripPlan, setTripPlan] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (initialPrompt) setPreferredStyleText(initialPrompt);
  }, [initialPrompt]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStep(2);
    setError(null);

    // 프론트엔드 단독 테스트를 위한 가짜 응답 (1.5초 지연)
    setTimeout(() => {
      setTripPlan({
        trip_summary: `${destination} 3박 4일 여행`,
        total_cost: budget,
        schedule: [
          { day: 1, slots: [{ slot_name: "오전", activity: "공항 도착 및 이동" }, { slot_name: "오후", activity: "호텔 체크인 및 시내 구경" }] },
          { day: 2, slots: [{ slot_name: "오전", activity: "유명 명소 방문" }, { slot_name: "오후", activity: "맛집 탐방 및 쇼핑" }] }
        ],
        raw_data: { mcp_fetched_data: { flight_quote: { price: 500000 }, hotel_quote: { price: 400000 }, weather_info: { temp: 20 } } }
      });
      setStep(3);
    }, 1500);
  };

  // 폼 화면
  const renderForm = () => (
    <div className="w-full max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-2xl animate-fade-in relative">
      <button onClick={() => navigate('/')} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-sm">✕ 닫기</button>
      <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">어디로 떠나시나요?</h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InputGroup label="출발지" icon={<MapPinIcon />}><input type="text" value={origin} onChange={(e) => setOrigin(e.target.value)} className="w-full pl-10 pr-4 py-3 border rounded-lg" required /></InputGroup>
          <InputGroup label="도착지" icon={<MapPinIcon />}><input type="text" value={destination} onChange={(e) => setDestination(e.target.value)} className="w-full pl-10 pr-4 py-3 border rounded-lg" required /></InputGroup>
        </div>
        <InputGroup label="여행 날짜" icon={<CalendarIcon />}>
          <div className="flex items-center space-x-2 w-full pl-10"><input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full py-3 border rounded-lg" /><span className="text-gray-500">-</span><input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full py-3 border rounded-lg" /></div>
        </InputGroup>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InputGroup label="인원" icon={<UsersIcon />}><input type="number" value={partySize} onChange={(e) => setPartySize(e.target.value)} className="w-full pl-10 pr-4 py-3 border rounded-lg" /></InputGroup>
          <InputGroup label="예산 (원)" icon={<WalletIcon />}><input type="number" value={budget} onChange={(e) => setBudget(e.target.value)} className="w-full pl-10 pr-4 py-3 border rounded-lg" /></InputGroup>
        </div>
        <InputGroup label="여행 스타일" icon={<EditIcon />}><textarea value={preferredStyleText} onChange={(e) => setPreferredStyleText(e.target.value)} className="w-full pl-10 pr-4 py-3 border rounded-lg h-24 resize-none" placeholder="예: 맛집 위주, 휴양지 선호..." /></InputGroup>
        <button type="submit" disabled={step === 2} className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 flex justify-center items-center gap-2">
          {step === 2 ? <LoaderIcon /> : <WandIcon />} <span>{step === 2 ? '여행 계획 생성 중...' : '계획 생성하기'}</span>
        </button>
      </form>
    </div>
  );

  // 결과 화면
  const renderResults = () => (
    <div className="w-full max-w-6xl mx-auto p-8 bg-white rounded-lg shadow-2xl">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">{tripPlan.trip_summary}</h1>
        <button onClick={() => setStep(1)} className="bg-gray-200 px-4 py-2 rounded hover:bg-gray-300">다시 계획하기</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <SummaryCard title="항공권" icon={<FlightIcon />} data={tripPlan.raw_data.mcp_fetched_data.flight_quote} />
        <SummaryCard title="숙소" icon={<HotelIcon />} data={tripPlan.raw_data.mcp_fetched_data.hotel_quote} />
        <SummaryCard title="날씨" icon={<WeatherIcon />} data={tripPlan.raw_data.mcp_fetched_data.weather_info} />
      </div>
      <h2 className="text-2xl font-bold mb-4">일정표</h2>
      <div className="space-y-4">
        {tripPlan.schedule.map((day) => (
          <div key={day.day} className="border p-4 rounded-lg">
            <h3 className="font-bold text-lg text-blue-600 mb-2">Day {day.day}</h3>
            {day.slots.map((slot, idx) => (
              <div key={idx} className="flex gap-4 mb-2 last:mb-0">
                <span className="font-bold w-16 text-gray-500">{slot.slot_name}</span>
                <span>{slot.activity}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      {step === 1 && renderForm()}
      {step === 2 && <div className="flex flex-col items-center justify-center h-96"><div className="text-blue-600 mb-4"><svg className="animate-spin h-10 w-10" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg></div><h2 className="text-2xl font-bold text-gray-700">여행 계획 생성 중...</h2></div>}
      {step === 3 && tripPlan && renderResults()}
    </div>
  );
}