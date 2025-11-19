// apps/frontend/src/pages/PlannerPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Loader2, MapPin, Calendar, Users, Wand, Wallet, Edit, Plane, ArrowLeft
} from 'lucide-react';

// --- 아이콘 컴포넌트 ---
const LoaderIcon = () => <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />;
const MapPinIcon = () => <MapPin size={20} />;
const CalendarIcon = () => <Calendar size={20} />;
const UsersIcon = () => <Users size={20} />;
const WandIcon = () => <Wand size={20} />;
const WalletIcon = () => <Wallet size={20} />;
const EditIcon = () => <Edit size={20} />;

// --- 공항 데이터 (Mock) ---
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

// --- 검색 입력 컴포넌트 ---
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

  // 폼 상태 관리
  const [origin, setOrigin] = useState('서울/인천 (ICN)');
  const [destination, setDestination] = useState('');
  const [startDate, setStartDate] = useState('2025-10-23');
  const [endDate, setEndDate] = useState('2025-10-26');
  const [partySize, setPartySize] = useState(2);
  const [preferredStyleText, setPreferredStyleText] = useState(initialPrompt);
  const [budget, setBudget] = useState(1000000);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialPrompt) {
        setPreferredStyleText(initialPrompt);
        if(initialPrompt.includes("오사카")) setDestination("오사카/간사이 (KIX)");
        if(initialPrompt.includes("도쿄")) setDestination("도쿄/나리타 (NRT)");
    }
  }, [initialPrompt]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // 💡 폼 데이터를 객체로 묶음
    const tripData = {
      origin, destination, startDate, endDate, partySize, preferredStyleText, budget
    };

    // 1.5초 딜레이 후 결과 페이지로 이동 (데이터 전달)
    setTimeout(() => {
      setLoading(false);
      // navigate의 두 번째 인자로 state를 넘겨줍니다.
      navigate('/result', { state: { tripData } });
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8 font-sans text-gray-900 flex items-center justify-center">
      <div className="w-full max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-2xl animate-fade-in relative">
        <button onClick={() => navigate('/')} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-sm">✕ 닫기</button>
        <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">어디로 떠나시나요?</h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <LocationSearchInput label="출발지" icon={<Plane size={20} className="text-gray-400 rotate-[-45deg]" />} value={origin} onChange={setOrigin} placeholder="도시/공항 검색 (예: 인천)" />
            <LocationSearchInput label="도착지" icon={<MapPinIcon />} value={destination} onChange={setDestination} placeholder="도시 검색 (예: 도쿄)" />
          </div>

          <InputGroup label="여행 날짜" icon={<CalendarIcon />}>
            <div className="flex items-center space-x-2 w-full pl-10">
              <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
              <span className="text-gray-500">-</span>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
            </div>
          </InputGroup>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputGroup label="인원" icon={<UsersIcon />}><input type="number" value={partySize} onChange={(e) => setPartySize(e.target.value)} className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></InputGroup>
            <InputGroup label="1인 예산 (원)" icon={<WalletIcon />}><input type="number" value={budget} onChange={(e) => setBudget(e.target.value)} className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></InputGroup>
          </div>
          
          <InputGroup label="여행 스타일" icon={<EditIcon />}><textarea value={preferredStyleText} onChange={(e) => setPreferredStyleText(e.target.value)} className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg h-24 resize-none focus:ring-2 focus:ring-blue-500 outline-none" placeholder="예: 맛집 위주, 휴양지 선호, 빡빡한 일정..." /></InputGroup>
          
          <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 flex justify-center items-center gap-2 shadow-lg transition-transform active:scale-95">
            {loading ? <LoaderIcon /> : <WandIcon />} 
            <span>{loading ? '여행 계획 생성 중...' : '여행 계획 생성하기'}</span>
          </button>
        </form>
      </div>
    </div>
  );
}