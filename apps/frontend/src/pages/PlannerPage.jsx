// apps/frontend/src/pages/PlannerPage.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Loader2, MapPin, Calendar, Users, Wand, Wallet, Edit, Plane, ArrowLeft,
  BedDouble, CheckCircle2, Clock
} from 'lucide-react';

// --- 아이콘 컴포넌트 ---
const LoaderIcon = () => <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />;

// 각 단계 정의: targetPercent까지 durationMs 동안 진행
const PLAN_STEPS = [
  { id: 'flight',   label: '항공권 검색중...',    icon: Plane,       targetPercent: 30, durationMs: 14000 },
  { id: 'hotel',    label: '호텔 검색중...',       icon: BedDouble,   targetPercent: 62, durationMs: 14000 },
  { id: 'schedule', label: 'AI 일정 생성중...',    icon: Calendar,    targetPercent: 92, durationMs: 20000 },
  { id: 'done',     label: '여행 계획 완성!',      icon: CheckCircle2,targetPercent: 100, durationMs: 400 },
];

const TripPlanningLoader = ({ percent }) => {
  const activeStep = PLAN_STEPS.findIndex((s, i) => {
    const prev = PLAN_STEPS[i - 1]?.targetPercent ?? 0;
    return percent >= prev && percent < s.targetPercent;
  });
  const currentStep = activeStep === -1 ? PLAN_STEPS.length - 1 : activeStep;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/80 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md mx-4">
        <h2 className="text-xl font-bold text-gray-900 mb-1 text-center">여행 계획을 만들고 있어요</h2>
        <p className="text-sm text-gray-500 text-center mb-6">AI가 최적의 일정을 분석 중입니다</p>

        {/* 전체 진행바 */}
        <div className="mb-6">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>진행률</span>
            <span className="font-bold text-blue-600">{Math.round(percent)}%</span>
          </div>
          <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>

        {/* 단계별 목록 */}
        <div className="space-y-3">
          {PLAN_STEPS.map((step, idx) => {
            const isDone = percent >= step.targetPercent;
            const isActive = idx === currentStep;
            const Icon = step.icon;

            return (
              <div
                key={step.id}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                  isDone ? 'bg-green-50' :
                  isActive ? 'bg-blue-50 shadow-sm' :
                  'bg-gray-50 opacity-40'
                }`}
              >
                <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  isDone ? 'bg-green-100 text-green-600' :
                  isActive ? 'bg-blue-100 text-blue-600' :
                  'bg-gray-200 text-gray-400'
                }`}>
                  {isActive && !isDone
                    ? <Loader2 size={16} className="animate-spin" />
                    : <Icon size={16} />
                  }
                </div>
                <span className={`text-sm font-medium ${
                  isDone ? 'text-green-700' :
                  isActive ? 'text-blue-700' :
                  'text-gray-400'
                }`}>
                  {step.label}
                </span>
                {isDone && <CheckCircle2 size={16} className="ml-auto text-green-500 shrink-0" />}
                {isActive && !isDone && (
                  <span className="ml-auto text-xs text-blue-400 flex items-center gap-1">
                    <Clock size={12} /> 진행중
                  </span>
                )}
              </div>
            );
          })}
        </div>

        <p className="text-xs text-gray-400 text-center mt-5">보통 30~60초 소요됩니다</p>
      </div>
    </div>
  );
};
const MapPinIcon = () => <MapPin size={20} />;
const CalendarIcon = () => <Calendar size={20} />;
const UsersIcon = () => <Users size={20} />;
const WandIcon = () => <Wand size={20} />;
const WalletIcon = () => <Wallet size={20} />;
const EditIcon = () => <Edit size={20} />;

// 💡 백엔드 API 주소
const API_BASE_URL = "http://127.0.0.1:8080/api/trip";

const POPULAR_LOCATIONS = [
  { code: 'ICN', name: '서울/인천', country: '대한민국' },
  { code: 'GMP', name: '서울/김포', country: '대한민국' },
  { code: 'NRT', name: '도쿄/나리타', country: '일본' },
  { code: 'HND', name: '도쿄/하네다', country: '일본' },
  { code: 'KIX', name: '오사카/간사이', country: '일본' },
  { code: 'FUK', name: '후쿠오카', country: '일본' },
  { code: 'CTS', name: '삿포로/신치토세', country: '일본' },
  { code: 'OKA', name: '오키나와/나하', country: '일본' },
  { code: 'CJU', name: '제주', country: '대한민국' },
  { code: 'PUS', name: '부산/김해', country: '대한민국' },
  { code: 'DAD', name: '다낭', country: '베트남' },
  { code: 'BKK', name: '방콕', country: '태국' },
  { code: 'CDG', name: '파리/샤를드골', country: '프랑스' },
  { code: 'LHR', name: '런던/히드로', country: '영국' },
  { code: 'JFK', name: '뉴욕/JFK', country: '미국' },
  { code: 'LAX', name: '로스앤젤레스', country: '미국' },
];

const LocationSearchInput = ({ label, icon, value, onChange, placeholder }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  const handleInputChange = (e) => {
    const inputValue = e.target.value;
    onChange(inputValue);
    if (inputValue.length > 0) {
      const filtered = POPULAR_LOCATIONS.filter(loc =>
        loc.name.includes(inputValue) ||
        loc.code.includes(inputValue.toUpperCase()) ||
        loc.country.includes(inputValue)
      );
      setSuggestions(filtered);
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
  };

  const handleSelect = (location) => {
    onChange(`${location.name} (${location.code})`);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <div className="flex items-center relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">{icon}</span>
        <input
          type="text"
          value={value}
          onChange={handleInputChange}
          placeholder={placeholder}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          onFocus={() => value && handleInputChange({ target: { value } })}
          onBlur={() => setTimeout(() => setIsOpen(false), 200)}
        />
      </div>
      {isOpen && suggestions.length > 0 && (
        <ul className="absolute z-20 w-full bg-white border border-gray-200 rounded-lg shadow-xl mt-1 max-h-60 overflow-y-auto animate-in fade-in zoom-in-95 duration-100">
          {suggestions.map((loc) => (
            <li key={loc.code} onClick={() => handleSelect(loc)} className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 flex justify-between items-center transition-colors">
              <div><span className="font-medium text-gray-800">{loc.name}</span><span className="text-xs text-gray-500 ml-2">{loc.country}</span></div>
              <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded border border-blue-100">{loc.code}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

const InputGroup = ({ label, icon, children }) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
    <div className="flex items-center relative">
      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">{icon}</span>
      {children}
    </div>
  </div>
);

export default function PlannerPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const initialPrompt = location.state?.initialPrompt || '';

  // 💡 [UX 개선] 오늘 날짜 구하기 유틸리티
  const getTodayString = () => new Date().toISOString().split('T')[0];
  const getFutureDateString = (days) => {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return date.toISOString().split('T')[0];
  };

  const [origin, setOrigin] = useState('서울/인천 (ICN)');
  const [destination, setDestination] = useState('');
  
  // 💡 기본값을 오늘 ~ 3일 뒤로 설정
  const [startDate, setStartDate] = useState(getTodayString());
  const [endDate, setEndDate] = useState(getFutureDateString(3));
  
  const [partySize, setPartySize] = useState(2);
  const [preferredStyleText, setPreferredStyleText] = useState(initialPrompt);
  const [budget, setBudget] = useState(1000000);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const progressTimer = useRef(null);

  useEffect(() => {
    if (initialPrompt) {
        setPreferredStyleText(initialPrompt);
        if(initialPrompt.includes("오사카")) setDestination("오사카/간사이 (KIX)");
        if(initialPrompt.includes("도쿄")) setDestination("도쿄/나리타 (NRT)");
    }
  }, [initialPrompt]);

  const startProgressSimulation = () => {
    setProgress(0);
    let current = 0;
    const steps = [
      { target: 30, duration: 14000 },
      { target: 62, duration: 14000 },
      { target: 92, duration: 20000 },
    ];
    let stepIdx = 0;
    const TICK = 200;

    const tick = () => {
      if (stepIdx >= steps.length) return;
      const { target, duration } = steps[stepIdx];
      const increment = (target - (stepIdx === 0 ? 0 : steps[stepIdx - 1].target)) / (duration / TICK);
      current = Math.min(current + increment, target);
      setProgress(Math.round(current * 10) / 10);
      if (current >= target) stepIdx++;
      progressTimer.current = setTimeout(tick, TICK);
    };
    progressTimer.current = setTimeout(tick, TICK);
  };

  const stopProgressSimulation = () => {
    if (progressTimer.current) clearTimeout(progressTimer.current);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    startProgressSimulation();

    const destName = destination.split('(')[0].trim();

    const requestBody = {
      origin: origin,
      destination: destName,
      start_date: startDate,
      end_date: endDate,
      party_size: parseInt(partySize),
      budget: parseInt(budget),
      preferred_style_text: preferredStyleText
    };

    try {
        const response = await fetch(`${API_BASE_URL}/plan`, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "여행 계획 생성 중 오류가 발생했습니다.");
        }

        stopProgressSimulation();
        setProgress(100);
        setTimeout(() => {
          navigate('/result', { state: { tripData: data } });
        }, 600);

    } catch (err) {
        console.error(err);
        stopProgressSimulation();
        setProgress(0);
        setError(err.message);
        setLoading(false);
    }
  };

  return (
    <>
    {loading && <TripPlanningLoader percent={progress} />}
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8 font-sans text-gray-900 flex items-center justify-center">
      <div className="w-full max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-2xl animate-fade-in relative">
        <button onClick={() => navigate(-1)} className="absolute top-4 left-4 flex items-center gap-1.5 text-gray-400 hover:text-gray-700 text-sm font-medium transition-colors">
          <ArrowLeft size={16} /> 돌아가기
        </button>
        <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">어디로 떠나시나요?</h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <LocationSearchInput label="출발지" icon={<Plane size={20} className="text-gray-400 rotate-[-45deg]" />} value={origin} onChange={setOrigin} placeholder="도시/공항 검색 (예: 인천, ICN)" />
            <LocationSearchInput label="도착지" icon={<MapPinIcon />} value={destination} onChange={setDestination} placeholder="도시 검색 (예: 도쿄, 오사카)" />
          </div>

          <InputGroup label="여행 날짜" icon={<CalendarIcon />}>
            <div className="flex items-center space-x-2 w-full pl-10">
              <input 
                type="date" 
                value={startDate} 
                min={getTodayString()} // 과거 날짜 선택 방지
                onChange={(e) => setStartDate(e.target.value)} 
                className="w-full py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" 
              />
              <span className="text-gray-500">-</span>
              <input 
                type="date" 
                value={endDate} 
                min={startDate} // 시작 날짜보다 이전 날짜 선택 방지
                onChange={(e) => setEndDate(e.target.value)} 
                className="w-full py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" 
              />
            </div>
          </InputGroup>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputGroup label="인원" icon={<UsersIcon />}><input type="number" value={partySize} min={1} onChange={(e) => setPartySize(e.target.value)} className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></InputGroup>
            <InputGroup label="1인 예산 (원)" icon={<WalletIcon />}><input type="number" value={budget} min={0} step={10000} onChange={(e) => setBudget(e.target.value)} className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></InputGroup>
          </div>
          
          <InputGroup label="여행 스타일" icon={<EditIcon />}><textarea value={preferredStyleText} onChange={(e) => setPreferredStyleText(e.target.value)} className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg h-24 resize-none focus:ring-2 focus:ring-blue-500 outline-none" placeholder="예: 맛집 위주, 휴양지 선호, 빡빡한 일정..." /></InputGroup>
          
          {error && <div className="text-red-600 text-center bg-red-50 p-2 rounded font-medium">{error}</div>}

          <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 flex justify-center items-center gap-2 shadow-lg transition-transform active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed">
            {loading ? <LoaderIcon /> : <WandIcon />} 
            <span>{loading ? '여행 계획 생성 중...' : '여행 계획 생성하기'}</span>
          </button>
        </form>
      </div>
    </div>
    </>
  );
}