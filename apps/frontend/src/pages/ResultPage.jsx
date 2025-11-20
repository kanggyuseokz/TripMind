// apps/frontend/src/pages/ResultPage.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Plane, Calendar, Users, Wallet, X, MapPin, ShoppingBag, Coffee, Car, Utensils, Home, Clock, Loader2,
  Edit2, Sparkles, Check, XCircle, Star, BedDouble, ArrowRight
} from 'lucide-react';

// --- 아이콘 ---
const CalendarIcon = () => <Calendar size={20} />;
const UsersIcon = () => <Users size={20} />;
const WalletIcon = () => <Wallet size={20} />;
const HomeIcon = () => <Home size={16} className="text-gray-500"/>; 
const ShoppingIcon = () => <ShoppingBag size={16} className="text-gray-500"/>;
const CoffeeIcon = () => <Coffee size={16} className="text-gray-500"/>;
const CarIcon = () => <Car size={16} className="text-gray-500"/>;
const UtensilsIcon = () => <Utensils size={16} className="text-gray-500"/>;
const ClockIcon = () => <Clock size={18} />;

// --- 차트 및 요약 컴포넌트 ---
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
  
  // 탭 상태 관리
  const [activeTab, setActiveTab] = useState('schedule');

  const [isEditMode, setIsEditMode] = useState(false);
  const [editingSlot, setEditingSlot] = useState(null);
  const [editPrompt, setEditPrompt] = useState("");
  const [isModifying, setIsModifying] = useState(false);

  useEffect(() => {
    if (!tripData) {
      navigate('/planner');
      return;
    }

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
      // 💡 [수정] 여러 개의 추천 데이터를 다시 복구 (1xN 리스트용)
      flights: [
        { id: 1, airline: "Korean Air", flightNo: "KE123", time: "10:00 - 12:30", duration: "2h 30m", price: 450000, type: "직항" },
        { id: 2, airline: "Asiana", flightNo: "OZ456", time: "14:00 - 16:30", duration: "2h 30m", price: 420000, type: "직항" },
        { id: 3, airline: "Jeju Air", flightNo: "7C101", time: "08:00 - 10:30", duration: "2h 30m", price: 350000, type: "직항" },
      ],
      hotels: [
        { id: 1, name: `${destName} 힐튼 호텔`, rating: 4.8, price: 250000, image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80", tags: ["5성급", "조식포함", "수영장"], address: "시내 중심가, 역에서 5분" },
        { id: 2, name: "시티 센터 비즈니스 호텔", rating: 4.5, price: 120000, image: "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&q=80", tags: ["4성급", "시내중심", "가성비"], address: "지하철역 도보 3분" },
        { id: 3, name: "코지 부티크 스테이", rating: 4.2, price: 90000, image: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80", tags: ["3성급", "감성숙소", "조용함"], address: "카페 거리 인근" },
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

  const handleAiModify = async () => {
    if (!editPrompt.trim()) return;
    setIsModifying(true);
    
    setTimeout(() => {
      const newPlan = { ...tripPlan };
      const { dayIndex, eventIndex } = editingSlot;
      newPlan.schedule[dayIndex].events[eventIndex].description = `[AI 수정됨] ${editPrompt}`;
      setTripPlan(newPlan);
      setIsModifying(false);
      setEditingSlot(null); 
      setEditPrompt("");
    }, 1500);
  };

  if (!tripPlan) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="flex flex-col items-center gap-4"><Loader2 className="animate-spin text-blue-600" size={32}/><span className="text-gray-500 font-medium">여행 계획을 불러오는 중...</span></div></div>;

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8 font-sans text-gray-900">
      <div className="w-full max-w-7xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden animate-fade-in relative pb-12">
        
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

        {/* 메인 콘텐츠 영역 */}
        <div className="p-6 md:p-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* 왼쪽: 개요 및 그래프 (고정) */}
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

          {/* 오른쪽: 탭 및 상세 내용 */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* 탭 메뉴 */}
            <div className="flex gap-2 border-b border-gray-200 overflow-x-auto">
              {[
                { id: 'schedule', label: '상세 일정', icon: <Calendar size={18} /> },
                { id: 'flights', label: '항공권 추천', icon: <Plane size={18} /> },
                { id: 'hotels', label: '숙소 추천', icon: <BedDouble size={18} /> }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 font-bold text-sm transition-all border-b-2 whitespace-nowrap ${
                    activeTab === tab.id 
                      ? 'border-black text-black' 
                      : 'border-transparent text-gray-400 hover:text-gray-600'
                  }`}
                >
                  {tab.icon} {tab.label}
                </button>
              ))}
            </div>

            <div className="min-h-[400px]">
              
              {/* 1. 상세 일정 탭 */}
              {activeTab === 'schedule' && (
                <div className="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-100 relative animate-in fade-in slide-in-from-bottom-2">
                  {/* 지도 */}
                  <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden group mb-8">
                    <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                      <h3 className="text-sm font-bold text-gray-700 flex items-center gap-2">
                        <MapPin size={16} className="text-red-500" /> 예상 경로
                      </h3>
                      <button className="text-blue-600 text-xs font-medium hover:underline">크게 보기</button>
                    </div>
                    <div className="h-64 bg-gray-100 relative flex items-center justify-center overflow-hidden">
                      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/USA_location_map.svg/1200px-USA_location_map.svg.png" alt="Map Placeholder" className="absolute inset-0 w-full h-full object-cover opacity-30 grayscale group-hover:grayscale-0 transition-all duration-500" />
                      <div className="z-10 bg-white/90 backdrop-blur-sm px-4 py-2 rounded-full shadow-sm flex items-center gap-2">
                        <MapPin className="text-red-500 animate-bounce" size={16} />
                        <span className="font-bold text-gray-700 text-sm">지도 영역</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-gray-800">일정표</h3>
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
                                      <textarea
                                        autoFocus
                                        className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none mb-3 resize-none"
                                        rows={3}
                                        placeholder={`AI에게 요청: "${event.description}" 대신 다른 걸 추천해줘`}
                                        value={editPrompt}
                                        onChange={(e) => setEditPrompt(e.target.value)}
                                        onClick={(e) => e.stopPropagation()}
                                      />
                                      <div className="flex justify-end gap-2">
                                        <button onClick={(e) => { e.stopPropagation(); setEditingSlot(null); }} className="text-gray-500 text-sm hover:underline px-2">취소</button>
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
              )}

              {/* 2. 항공권 탭 (세로 리스트) */}
              {activeTab === 'flights' && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
                   <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 text-blue-800 text-sm mb-4 flex items-center gap-2">
                    <Sparkles size={16} />
                    AI가 추천하는 최적의 항공권 목록입니다.
                  </div>
                  
                  {tripPlan.flights.map((flight) => (
                    <div key={flight.id} className="bg-white p-6 rounded-2xl shadow-md border border-gray-100 hover:shadow-lg transition-all flex flex-col md:flex-row items-center justify-between gap-6">
                      <div className="flex items-center gap-5 w-full md:w-auto">
                        <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center text-blue-600 border border-gray-100 shrink-0">
                          <Plane size={28} />
                        </div>
                        <div>
                          <h4 className="font-bold text-xl text-gray-900 mb-1">{flight.airline}</h4>
                          <p className="text-gray-500 text-sm font-medium">{flight.flightNo} • {flight.type}</p>
                        </div>
                      </div>
                      
                      <div className="flex-1 w-full md:w-auto flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="text-center md:text-left">
                          <p className="text-sm text-gray-400 mb-0.5">비행 시간</p>
                          <p className="font-bold text-lg text-gray-800">{flight.time}</p>
                          <p className="text-xs text-gray-500 mt-1">{flight.duration}</p>
                        </div>
                        <div className="text-center md:text-right w-full md:w-auto">
                          <p className="text-2xl font-bold text-blue-600 mb-2">{flight.price.toLocaleString()}원</p>
                          <button className="w-full md:w-auto bg-black text-white px-6 py-2 rounded-lg font-bold hover:bg-gray-800 transition-colors text-sm">
                            선택하기
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* 3. 숙소 탭 (세로 리스트) */}
              {activeTab === 'hotels' && (
                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2">
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 text-blue-800 text-sm mb-2 flex items-center gap-2">
                    <Sparkles size={16} />
                    여행 스타일에 딱 맞는 숙소들을 추천해 드립니다.
                  </div>

                  {tripPlan.hotels.map((hotel) => (
                    <div key={hotel.id} className="bg-white rounded-2xl overflow-hidden shadow-md border border-gray-200 group hover:shadow-xl transition-all">
                      <div className="flex flex-col md:flex-row h-full">
                        {/* 이미지 영역 (가로 배치 시 왼쪽, 모바일은 위쪽) */}
                        <div className="relative md:w-1/3 h-56 md:h-auto">
                          <img src={hotel.image} alt={hotel.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
                          <div className="absolute top-3 right-3 bg-white/90 backdrop-blur px-2 py-1 rounded-lg text-xs font-bold text-yellow-600 flex items-center gap-1 shadow-sm">
                            <Star size={12} fill="currentColor" /> {hotel.rating}
                          </div>
                        </div>
                        
                        {/* 정보 영역 */}
                        <div className="p-6 flex-1 flex flex-col justify-between">
                          <div>
                            <div className="flex flex-wrap gap-2 mb-3">
                              {hotel.tags.map((tag, i) => (
                                <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-md border border-gray-100">{tag}</span>
                              ))}
                            </div>
                            <h4 className="text-xl font-bold text-gray-900 mb-2">{hotel.name}</h4>
                            <p className="text-gray-500 text-sm flex items-center gap-1 mb-4">
                              <MapPin size={14} /> {hotel.address}
                            </p>
                          </div>
                          
                          <div className="flex items-end justify-between border-t border-gray-100 pt-4 mt-2">
                            <div>
                              <p className="text-xs text-gray-400 mb-0.5">1박 기준 (세금 포함)</p>
                              <p className="text-2xl font-bold text-blue-600">{hotel.price.toLocaleString()}<span className="text-sm font-normal text-gray-500">원</span></p>
                            </div>
                            <button className="bg-black text-white px-6 py-2.5 rounded-xl font-bold hover:bg-gray-800 transition-all shadow-md flex items-center gap-2 text-sm">
                              예약하기 <ArrowRight size={16} />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

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