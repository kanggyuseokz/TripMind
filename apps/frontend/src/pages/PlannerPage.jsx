// apps/frontend/src/pages/PlannerPage.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Loader2, MapPin, Calendar, Wand2, Plane, ArrowLeft,
  BedDouble, CheckCircle2, Clock, Sparkles, UtensilsCrossed, ShoppingBag,
  Waves, Mountain
} from 'lucide-react';

const PLAN_STEPS = [
  { id: 'flight',   label: '항공권 검색중...',    icon: Plane,       targetPercent: 30, durationMs: 14000 },
  { id: 'hotel',    label: '호텔 검색중...',       icon: BedDouble,   targetPercent: 62, durationMs: 14000 },
  { id: 'schedule', label: 'AI 일정 생성중...',    icon: Calendar,    targetPercent: 92, durationMs: 20000 },
  { id: 'done',     label: '여행 계획 완성!',      icon: CheckCircle2,targetPercent: 100, durationMs: 400 },
];

const TRAVEL_STYLES = [
  { id: 'relaxation', label: '휴양', icon: Waves, color: 'blue' },
  { id: 'sightseeing', label: '관광', icon: Mountain, color: 'green' },
  { id: 'foodie', label: '맛집', icon: UtensilsCrossed, color: 'orange' },
  { id: 'activity', label: '액티비티', icon: Sparkles, color: 'purple' },
  { id: 'shopping', label: '쇼핑', icon: ShoppingBag, color: 'pink' },
];

const STYLE_COLORS = {
  blue:   { btn: 'border-blue-400 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300',   icon: 'text-blue-500' },
  green:  { btn: 'border-green-400 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300', icon: 'text-green-500' },
  orange: { btn: 'border-orange-400 bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300', icon: 'text-orange-500' },
  purple: { btn: 'border-purple-400 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300', icon: 'text-purple-500' },
  pink:   { btn: 'border-pink-400 bg-pink-50 dark:bg-pink-900/30 text-pink-700 dark:text-pink-300',   icon: 'text-pink-500' },
};

const TripPlanningLoader = ({ percent }) => {
  const activeStep = PLAN_STEPS.findIndex((s, i) => {
    const prev = PLAN_STEPS[i - 1]?.targetPercent ?? 0;
    return percent >= prev && percent < s.targetPercent;
  });
  const currentStep = activeStep === -1 ? PLAN_STEPS.length - 1 : activeStep;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/80 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 w-full max-w-md mx-4">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1 text-center">여행 계획을 만들고 있어요</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center mb-6">AI가 최적의 일정을 분석 중입니다</p>

        <div className="mb-6">
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
            <span>진행률</span>
            <span className="font-bold text-blue-600">{Math.round(percent)}%</span>
          </div>
          <div className="h-2.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>

        <div className="space-y-3">
          {PLAN_STEPS.map((step, idx) => {
            const isDone = percent >= step.targetPercent;
            const isActive = idx === currentStep;
            const Icon = step.icon;
            return (
              <div
                key={step.id}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                  isDone ? 'bg-green-50 dark:bg-green-900/20' :
                  isActive ? 'bg-blue-50 dark:bg-blue-900/30 shadow-sm' :
                  'bg-gray-50 dark:bg-gray-700/50 opacity-40'
                }`}
              >
                <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  isDone ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' :
                  isActive ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' :
                  'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500'
                }`}>
                  {isActive && !isDone ? <Loader2 size={16} className="animate-spin" /> : <Icon size={16} />}
                </div>
                <span className={`text-sm font-medium ${
                  isDone ? 'text-green-700 dark:text-green-400' : isActive ? 'text-blue-700 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500'
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
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-5">보통 30~60초 소요됩니다</p>
      </div>
    </div>
  );
};

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
      <label className="block text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">{label}</label>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">{icon}</span>
        <input
          type="text"
          value={value}
          onChange={handleInputChange}
          placeholder={placeholder}
          className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 dark:text-white rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder-gray-400 dark:placeholder-gray-500"
          onFocus={() => value && handleInputChange({ target: { value } })}
          onBlur={() => setTimeout(() => setIsOpen(false), 200)}
        />
      </div>
      {isOpen && suggestions.length > 0 && (
        <ul className="absolute z-20 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-xl mt-1 max-h-60 overflow-y-auto">
          {suggestions.map((loc) => (
            <li
              key={loc.code}
              onClick={() => handleSelect(loc)}
              className="px-4 py-3 hover:bg-blue-50 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0 flex justify-between items-center transition-colors"
            >
              <div>
                <span className="font-medium text-gray-800 dark:text-white">{loc.name}</span>
                <span className="text-xs text-gray-400 ml-2">{loc.country}</span>
              </div>
              <span className="text-xs font-bold text-blue-600 bg-blue-50 dark:bg-blue-900/30 px-2 py-1 rounded-lg">{loc.code}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

const API_BASE_URL = "http://127.0.0.1:8080/api/trip";

export default function PlannerPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const initialPrompt = location.state?.initialPrompt || '';

  const getTodayString = () => new Date().toISOString().split('T')[0];
  const getFutureDateString = (days) => {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return date.toISOString().split('T')[0];
  };

  const [origin, setOrigin] = useState('서울/인천 (ICN)');
  const [destination, setDestination] = useState('');
  const [startDate, setStartDate] = useState(getTodayString());
  const [endDate, setEndDate] = useState(getFutureDateString(3));
  const [partySize, setPartySize] = useState(2);
  const [selectedStyles, setSelectedStyles] = useState([]);
  const [styleNote, setStyleNote] = useState(initialPrompt);
  const [budget, setBudget] = useState(1000000);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const progressTimer = useRef(null);

  useEffect(() => {
    if (initialPrompt) {
      setStyleNote(initialPrompt);
      if (initialPrompt.includes('오사카')) setDestination('오사카/간사이 (KIX)');
      if (initialPrompt.includes('도쿄')) setDestination('도쿄/나리타 (NRT)');
    }
  }, [initialPrompt]);

  const toggleStyle = (id) => {
    setSelectedStyles(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  const formatBudget = (v) => {
    if (v >= 10000000) return `${(v / 10000000).toFixed(1)}천만원`;
    if (v >= 1000000) return `${(v / 1000000).toFixed(0)}백만원`;
    if (v >= 10000) return `${(v / 10000).toFixed(0)}만원`;
    return `${v.toLocaleString()}원`;
  };

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
      if (stepIdx >= steps.length) {
        // 92% 이후: 99%까지 매우 천천히 크리핑 (3초마다 0.5%)
        if (current < 99) {
          current = Math.min(current + 0.5 * (TICK / 3000), 99);
          setProgress(Math.round(current * 10) / 10);
        }
        progressTimer.current = setTimeout(tick, TICK);
        return;
      }
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
    // 선택된 스타일 중 첫 번째가 primary, 나머지는 secondary
    const primaryStyle = selectedStyles[0] || 'sightseeing';
    const styleLabels = selectedStyles.map(id => TRAVEL_STYLES.find(s => s.id === id)?.label).filter(Boolean);
    const styleText = [
      styleLabels.length > 0 ? styleLabels.join(', ') + ' 스타일 여행' : '',
      styleNote.trim()
    ].filter(Boolean).join('. ') || '자유 여행';

    const requestBody = {
      origin,
      destination: destName,
      start_date: startDate,
      end_date: endDate,
      party_size: parseInt(partySize),
      budget: parseInt(budget),
      travel_style: primaryStyle,          // 체크박스 ID 직접 전달
      secondary_styles: selectedStyles.slice(1), // 나머지 스타일
      preferred_style_text: styleText,     // LLM 참고용 텍스트
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 180000); // 3분 타임아웃

      const response = await fetch(`${API_BASE_URL}/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || '여행 계획 생성 중 오류가 발생했습니다.');

      stopProgressSimulation();
      setProgress(100);
      setTimeout(() => navigate('/result', { state: { tripData: data } }), 600);
    } catch (err) {
      console.error(err);
      stopProgressSimulation();
      setProgress(0);
      const msg = err.name === 'AbortError'
        ? '요청 시간이 초과되었습니다. 다시 시도해주세요.'
        : err.message;
      setError(msg);
      setLoading(false);
    }
  };

  const calcNights = () => {
    if (!startDate || !endDate) return 0;
    const diff = (new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24);
    return Math.max(0, diff);
  };

  return (
    <>
      {loading && <TripPlanningLoader percent={progress} />}
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 py-10 px-4">
        <div className="w-full max-w-2xl mx-auto">

          {/* 헤더 */}
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 text-sm font-medium mb-6 transition-colors"
          >
            <ArrowLeft size={16} /> 돌아가기
          </button>

          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">어디로 떠나시나요?</h1>
            <p className="text-gray-500 dark:text-gray-400">AI가 최적의 여행 계획을 만들어 드릴게요</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">

            {/* 출발/도착 */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
              <h2 className="text-sm font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-4">항공편</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-end">
                <LocationSearchInput
                  label="출발지"
                  icon={<Plane size={18} className="rotate-[-45deg]" />}
                  value={origin}
                  onChange={setOrigin}
                  placeholder="도시/공항 (예: 인천, ICN)"
                />
                <LocationSearchInput
                  label="도착지"
                  icon={<MapPin size={18} />}
                  value={destination}
                  onChange={setDestination}
                  placeholder="도시 (예: 도쿄, 오사카)"
                />
              </div>
            </div>

            {/* 날짜 */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
              <h2 className="text-sm font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-4">여행 날짜</h2>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">출발일</label>
                  <div className="relative">
                    <Calendar size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="date"
                      value={startDate}
                      min={getTodayString()}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full pl-9 pr-3 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 dark:text-white rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">귀국일</label>
                  <div className="relative">
                    <Calendar size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="date"
                      value={endDate}
                      min={startDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="w-full pl-9 pr-3 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 dark:text-white rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                    />
                  </div>
                </div>
              </div>
              {calcNights() > 0 && (
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-2 text-center font-medium">
                  {calcNights()}박 {calcNights() + 1}일 여행
                </p>
              )}
            </div>

            {/* 인원 & 예산 */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
              <h2 className="text-sm font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-4">인원 및 예산</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">인원</label>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setPartySize(p => Math.max(1, parseInt(p) - 1))}
                      className="w-10 h-10 rounded-xl bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 font-bold transition-colors text-lg"
                    >−</button>
                    <span className="flex-1 text-center font-bold text-lg text-gray-900 dark:text-white">
                      {partySize}명
                    </span>
                    <button
                      type="button"
                      onClick={() => setPartySize(p => Math.min(20, parseInt(p) + 1))}
                      className="w-10 h-10 rounded-xl bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 font-bold transition-colors text-lg"
                    >+</button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
                    1인 예산
                    <span className="ml-2 font-bold text-blue-600 dark:text-blue-400">{formatBudget(budget)}</span>
                  </label>
                  <input
                    type="range"
                    min={100000}
                    max={10000000}
                    step={100000}
                    value={budget}
                    onChange={(e) => setBudget(parseInt(e.target.value))}
                    className="w-full accent-blue-600"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>10만원</span>
                    <span>1000만원</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 여행 스타일 */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
              <h2 className="text-sm font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-4">여행 스타일</h2>
              <div className="flex flex-wrap gap-2 mb-4">
                {TRAVEL_STYLES.map(({ id, label, icon: Icon, color }) => {
                  const isSelected = selectedStyles.includes(id);
                  const colors = STYLE_COLORS[color];
                  return (
                    <button
                      key={id}
                      type="button"
                      onClick={() => toggleStyle(id)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-xl border-2 text-sm font-semibold transition-all ${
                        isSelected
                          ? colors.btn
                          : 'border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-500'
                      }`}
                    >
                      <Icon size={15} className={isSelected ? colors.icon : 'text-gray-400'} />
                      {label}
                    </button>
                  );
                })}
              </div>
              <textarea
                value={styleNote}
                onChange={(e) => setStyleNote(e.target.value)}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 rounded-xl h-20 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                placeholder="추가 요청사항을 자유롭게 입력해주세요 (선택)"
              />
            </div>

            {error && (
              <div className="text-red-600 dark:text-red-400 text-center bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-3 rounded-xl text-sm font-medium">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !destination.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed text-white py-4 rounded-2xl font-bold text-base shadow-lg hover:shadow-xl transition-all flex justify-center items-center gap-2"
            >
              {loading
                ? <><Loader2 size={20} className="animate-spin" /> 여행 계획 생성 중...</>
                : <><Wand2 size={20} /> 여행 계획 생성하기</>
              }
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
