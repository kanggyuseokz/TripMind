// apps/frontend/src/pages/ResultPage.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Plane, Calendar, Users, Wallet, X, MapPin, ShoppingBag, Coffee, Car, Utensils, Home, Clock, Loader2,
  Edit2, Sparkles, Check, XCircle
} from 'lucide-react';

// ... (아이콘 컴포넌트들은 이전과 동일) ...
const CalendarIcon = () => <Calendar size={20} />;
const UsersIcon = () => <Users size={20} />;
const WalletIcon = () => <Wallet size={20} />;
const HomeIcon = () => <Home size={16} className="text-gray-500"/>; 
const ShoppingIcon = () => <ShoppingBag size={16} className="text-gray-500"/>;
const CoffeeIcon = () => <Coffee size={16} className="text-gray-500"/>;
const CarIcon = () => <Car size={16} className="text-gray-500"/>;
const UtensilsIcon = () => <Utensils size={16} className="text-gray-500"/>;
const ClockIcon = () => <Clock size={18} />;

// ... (OverviewCard, DonutChart 컴포넌트는 이전과 동일) ...
const OverviewCard = ({ title, value, subValue, icon }) => (
  <div className="flex items-start p-5 bg-white rounded-xl shadow-sm border border-gray-100 transition-all hover:shadow-md">
    <div className="p-3 bg-blue-50 text-blue-600 rounded-full mr-4 shrink-0">
      {icon}
    </div>
    <div>
      <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
      <p className="font-bold text-lg text-gray-900">{value}</p>
      {subValue && <p className="text-sm text-gray-400 mt-0.5">{subValue}</p>}
    </div>
  </div>
);

const DonutChart = ({ data, size = 160, strokeWidth = 20 }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  let accumulatedPercentage = 0;
  const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="rotate-[-90deg]">
        {data.map((item, index) => {
          const percentage = item.value;
          const strokeDasharray = `${(percentage / 100) * circumference} ${circumference}`;
          const strokeDashoffset = -((accumulatedPercentage / 100) * circumference);
          accumulatedPercentage += percentage;
          return (
            <circle
              key={index} cx={size / 2} cy={size / 2} r={radius} fill="transparent"
              stroke={colors[index % colors.length]} strokeWidth={strokeWidth}
              strokeDasharray={strokeDasharray} strokeDashoffset={strokeDashoffset}
              strokeLinecap="round" className="transition-all duration-1000 ease-out"
            />
          );
        })}
      </svg>
      <div className="absolute text-center">
        <p className="text-2xl font-bold text-gray-800">100%</p>
        <p className="text-xs font-medium text-gray-400">완료</p>
      </div>
    </div>
  );
};

export default function ResultPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const tripData = location.state?.tripData;

  const [tripPlan, setTripPlan] = useState(null);
  
  // 수정 모드 관련 상태
  const [isEditMode, setIsEditMode] = useState(false);
  const [editingSlot, setEditingSlot] = useState(null); // { dayIndex, eventIndex }
  const [editPrompt, setEditPrompt] = useState("");
  const [isModifying, setIsModifying] = useState(false);

  useEffect(() => {
    if (!tripData) {
      navigate('/planner');
      return;
    }

    // ... (초기 데이터 설정 로직은 이전과 동일) ...
    const destName = tripData.destination.split('(')[0].trim() || "여행지";
    const budget = parseInt(tripData.budget, 10) || 0;
    const partySize = parseInt(tripData.partySize, 10) || 1;

    let durationStr = tripData.durationText;
    if (!durationStr && tripData.startDate && tripData.endDate) {
        const start = new Date(tripData.startDate);
        const end = new Date(tripData.endDate);
        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
        durationStr = `${diffDays}박 ${diffDays + 1}일`;
    }

    setTripPlan({
      trip_summary: `${destName} 여행 계획`,
      total_cost: budget * partySize,
      per_person_budget: budget,
      startDate: tripData.startDate,
      endDate: tripData.endDate,
      durationText: durationStr || "기간 미정",
      head_count: partySize,
      activity_distribution: [
          { name: '관광', value: 40 },
          { name: '쇼핑', value: 30 },
          { name: '휴식', value: 30 },
      ],
      schedule: [
        { day: 1, date: "1일차", events: [
            { time_slot: "오전", description: `${destName} 도착 및 체크인`, icon: "plane" },
            { time_slot: "오후", description: "주변 탐방 및 카페", icon: "coffee" },
            { time_slot: "저녁", description: "현지 맛집 저녁 식사", icon: "utensils" }
        ]},
        { day: 2, date: "2일차", events: [
            { time_slot: "오전", description: "랜드마크 방문", icon: "home" },
            { time_slot: "오후", description: "쇼핑 센터 방문", icon: "shopping" },
            { time_slot: "저녁", description: "야경 감상", icon: "car" }
        ]},
        { day: 3, date: "3일차", events: [
            { time_slot: "오전", description: "근교 명소 투어", icon: "car" },
            { time_slot: "오후", description: "숨은 골목 카페 탐방", icon: "coffee" },
            { time_slot: "저녁", description: "루프탑 바에서 칵테일", icon: "utensils" }
        ]},
        { day: 4, date: "4일차", events: [
            { time_slot: "오전", description: "기념품 구매 및 체크아웃", icon: "shopping" },
            { time_slot: "오후", description: "공항 이동 및 귀국", icon: "plane" }
        ]},
      ]
    });
  }, [tripData, navigate]);

  // [백엔드 연동 예정] 수정 요청 핸들러
  const handleAiModify = async () => {
    if (!editPrompt.trim()) return;
    setIsModifying(true);
    
    /* // --- [TODO] 실제 백엔드 연동 시 사용할 코드 ---
    try {
      const response = await fetch('http://localhost:8080/api/trip/modify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_plan: tripPlan, // 현재 전체 일정 정보
          target_slot: editingSlot, // 수정하려는 일정의 인덱스 { dayIndex, eventIndex }
          user_prompt: editPrompt // 사용자의 수정 요청 사항 (예: "좀 더 액티비티한 걸로 바꿔줘")
        }),
      });

      if (!response.ok) throw new Error('수정 요청 실패');

      const data = await response.json();
      // 백엔드에서 수정된 전체 일정(newPlan) 혹은 수정된 항목(modifiedEvent)을 받아와야 함
      
      // 예시 1: 전체 일정을 통째로 갈아끼우는 경우
      // setTripPlan(data.new_plan);

      // 예시 2: 특정 항목만 업데이트하는 경우
      // const newPlan = { ...tripPlan };
      // newPlan.schedule[editingSlot.dayIndex].events[editingSlot.eventIndex] = data.modified_event;
      // setTripPlan(newPlan);

    } catch (error) {
      console.error("AI 수정 중 오류 발생:", error);
      alert("일정 수정에 실패했습니다.");
    } finally {
      setIsModifying(false);
      setEditingSlot(null);
      setEditPrompt("");
    }
    */

    // --- [현재] 프론트엔드 목업(Mock) 처리 ---
    setTimeout(() => {
      const newPlan = { ...tripPlan };
      const { dayIndex, eventIndex } = editingSlot;
      
      // 더미 데이터로 내용 변경
      newPlan.schedule[dayIndex].events[eventIndex].description = `[AI 수정됨] ${editPrompt}`;
      
      setTripPlan(newPlan);
      setIsModifying(false);
      setEditingSlot(null); 
      setEditPrompt("");
    }, 1500);
  };

  if (!tripPlan) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="flex flex-col items-center gap-4"><Loader2 className="animate-spin text-blue-600" size={32}/><span className="text-gray-500 font-medium">여행 계획을 불러오는 중...</span></div></div>;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8 font-sans text-gray-900">
      {/* ... (나머지 렌더링 코드는 이전과 동일) ... */}
      <div className="w-full max-w-7xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden animate-fade-in relative pb-12">
        
        {/* 상단 바 */}
        <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-center bg-white/80 backdrop-blur-md z-10 border-b border-gray-100">
          <div className="flex items-center gap-2 text-gray-900 font-extrabold text-xl tracking-tight cursor-pointer" onClick={() => navigate('/')}>
            <Plane size={24} className="text-blue-600" strokeWidth={2.5} /> TripMind
          </div>
          <div className="flex items-center gap-3">
            {/* 👇 [수정할 부분] 저장 버튼에 navigate 연결 */}
            <button 
              onClick={() => {
                // 1. (나중에) 여기서 백엔드에 저장 API 호출
                // 2. 저장 완료 후 페이지 이동
                navigate('/saved'); // 저장 페이지로 이동
              }}
              className="p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors" 
              title="저장"
            >
              <ShoppingBag size={20} />
            </button>

            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md">U</div>
            <button onClick={() => navigate('/planner')} className="p-2 text-gray-400 hover:text-gray-700 transition-colors">
              <X size={24} />
            </button>
          </div>
        </div>

        {/* 히어로 이미지 */}
        <div className="relative h-80 bg-cover bg-center group" style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1920&q=80)' }}>
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent"></div>
          <div className="absolute bottom-0 left-0 w-full p-8 text-white transform translate-y-2 group-hover:translate-y-0 transition-transform duration-500">
            <h1 className="text-4xl md:text-5xl font-extrabold mb-3 tracking-tight shadow-sm">{tripPlan.trip_summary}</h1>
            <div className="flex flex-wrap items-baseline gap-3 opacity-90">
              <p className="text-lg font-medium">총 예상 비용 <span className="font-bold text-2xl text-yellow-300">{tripPlan.total_cost.toLocaleString()} KRW</span></p>
              <span className="text-white/60">|</span>
              <p className="text-sm text-white/80">1인당 {tripPlan.per_person_budget.toLocaleString()} KRW</p>
            </div>
          </div>
        </div>

        {/* 메인 콘텐츠 */}
        <div className="p-6 md:p-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* 왼쪽: 개요 및 그래프 */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
                <span className="w-1 h-6 bg-blue-500 rounded-full"></span>활동 비율
              </h3>
              <div className="flex flex-col items-center">
                <DonutChart data={tripPlan.activity_distribution} size={180} strokeWidth={24} />
                <div className="mt-6 w-full space-y-3">
                  {tripPlan.activity_distribution.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full" style={{ backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'][idx % 5] }}></span>
                        <span className="text-gray-600 font-medium">{item.name}</span>
                      </div>
                      <span className="font-bold text-gray-900">{item.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <OverviewCard title="인원" value={`${tripPlan.head_count}명`} icon={<UsersIcon size={20} />} />
              <OverviewCard title="여행 기간" value={tripPlan.durationText} subValue={`${tripPlan.startDate} ~ ${tripPlan.endDate}`} icon={<CalendarIcon size={20} />} />
              <OverviewCard title="1인 예산" value={`${tripPlan.per_person_budget.toLocaleString()} KRW`} icon={<WalletIcon size={20} />} />
            </div>
          </div>

          {/* 오른쪽: 지도 및 일정표 */}
          <div className="lg:col-span-2 space-y-8">
            {/* 지도 (더미) */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden group">
              <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                  <MapPin size={18} className="text-red-500" /> 예상 경로
                </h3>
                <button className="text-blue-600 text-sm font-medium hover:underline">지도 크게 보기</button>
              </div>
              <div className="h-80 bg-gray-100 relative flex items-center justify-center overflow-hidden">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/USA_location_map.svg/1200px-USA_location_map.svg.png" alt="Map Placeholder" className="absolute inset-0 w-full h-full object-cover opacity-30 grayscale group-hover:grayscale-0 transition-all duration-500" />
                <div className="z-10 bg-white/90 backdrop-blur-sm px-6 py-3 rounded-full shadow-lg flex items-center gap-2">
                  <MapPin className="text-red-500 animate-bounce" />
                  <span className="font-bold text-gray-700">지도가 표시될 영역입니다</span>
                </div>
              </div>
            </div>

            {/* 일정표 (수정 기능 포함) */}
            <div className="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-100 relative">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-gray-800">상세 일정</h3>
                <button 
                  onClick={() => { setIsEditMode(!isEditMode); setEditingSlot(null); }}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                    isEditMode 
                      ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-200' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {isEditMode ? <Check size={16} /> : <Edit2 size={16} />}
                  {isEditMode ? '수정 종료' : '일정 수정하기'}
                </button>
              </div>

              {isEditMode && !editingSlot && (
                <div className="mb-4 p-3 bg-blue-50 text-blue-700 text-sm rounded-lg flex items-center gap-2 animate-in fade-in">
                  <Sparkles size={16} />
                  수정하고 싶은 일정을 클릭하세요. AI가 도와드립니다!
                </div>
              )}

              <div className="space-y-8 relative before:absolute before:inset-0 before:left-4 before:top-4 before:w-0.5 before:bg-gray-200 before:h-full">
                {tripPlan.schedule.map((dayPlan, idx) => (
                  <div key={idx} className="relative pl-10">
                    <div className="absolute left-0 top-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md ring-4 ring-white z-10">
                      {idx + 1}
                    </div>
                    <div className="mb-4">
                      <h4 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                        {dayPlan.date} <span className="text-sm font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">{dayPlan.date === "1일차" ? tripPlan.startDate : ""}</span>
                      </h4>
                    </div>
                    
                    <ul className="space-y-3">
                      {dayPlan.events.map((event, eIdx) => {
                        const isEditing = editingSlot?.dayIndex === idx && editingSlot?.eventIndex === eIdx;
                        return (
                          <li 
                            key={eIdx} 
                            onClick={() => isEditMode && !isEditing && setEditingSlot({ dayIndex: idx, eventIndex: eIdx })}
                            className={`relative flex items-start bg-gray-50 p-4 rounded-xl border transition-all
                              ${isEditMode && !isEditing ? 'cursor-pointer hover:border-blue-400 hover:shadow-md hover:-translate-y-0.5' : 'border-gray-100'}
                              ${isEditing ? 'border-blue-500 ring-2 ring-blue-100 bg-white shadow-lg z-10' : ''}
                            `}
                          >
                            <span className="flex-shrink-0 mr-4 mt-1 text-gray-500 p-2 bg-white rounded-lg shadow-sm">
                              {event.icon === "plane" ? <Plane size={18} className="text-blue-500" /> :
                               event.icon === "shopping" ? <ShoppingIcon size={18} className="text-purple-500" /> :
                               event.icon === "utensils" ? <UtensilsIcon size={18} className="text-orange-500" /> :
                               event.icon === "home" ? <HomeIcon size={18} className="text-green-500" /> :
                               event.icon === "coffee" ? <CoffeeIcon size={18} className="text-brown-500" /> :
                               event.icon === "car" ? <CarIcon size={18} className="text-gray-600" /> : <span className="text-sm">●</span>}
                            </span>

                            <div className="flex-1">
                              {isEditing ? (
                                <div className="animate-in fade-in zoom-in-95 duration-200">
                                  <div className="flex justify-between items-center mb-2">
                                    <p className="font-bold text-blue-700 text-sm">{event.time_slot} 일정 수정</p>
                                    <button onClick={(e) => { e.stopPropagation(); setEditingSlot(null); }} className="text-gray-400 hover:text-gray-600"><XCircle size={18}/></button>
                                  </div>
                                  <textarea
                                    autoFocus
                                    className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none mb-3 resize-none"
                                    rows={3}
                                    placeholder={`AI에게 요청: "${event.description}" 대신 다른 걸 추천해줘`}
                                    value={editPrompt}
                                    onChange={(e) => setEditPrompt(e.target.value)}
                                    onClick={(e) => e.stopPropagation()}
                                  />
                                  <div className="flex justify-end gap-2">
                                    <button 
                                      onClick={(e) => { e.stopPropagation(); handleAiModify(); }}
                                      disabled={isModifying || !editPrompt.trim()}
                                      className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-700 flex items-center gap-1 disabled:bg-gray-300"
                                    >
                                      {isModifying ? <Loader2 className="animate-spin" size={14} /> : <Sparkles size={14} />}
                                      {isModifying ? '수정 중...' : 'AI 수정 요청'}
                                    </button>
                                  </div>
                                </div>
                              ) : (
                                <div>
                                  <p className="font-bold text-gray-800 text-sm mb-0.5">{event.time_slot}</p>
                                  <p className="text-gray-600 text-sm leading-relaxed">{event.description}</p>
                                  {isEditMode && <p className="text-xs text-blue-500 mt-2 font-medium">클릭하여 수정하기</p>}
                                </div>
                              )}
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="text-center mt-8 mb-4">
          <button onClick={() => navigate('/planner')} className="bg-gray-900 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-lg hover:bg-gray-800 hover:shadow-xl transform hover:-translate-y-0.5 transition-all">
            다른 여행 계획하기
          </button>
        </div>
      </div>
    </div>
  );
}