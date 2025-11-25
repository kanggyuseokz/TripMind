// apps/frontend/src/pages/ResultPage.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Plane, Calendar, Users, Wallet, MapPin, ShoppingBag, Coffee, Car, Utensils, Home, Clock, Loader2, Edit2, Sparkles, Check, XCircle, Star, BedDouble, ArrowRight } from 'lucide-react';

// 아이콘 컴포넌트들
const CalendarIcon = () => <Calendar size={20} />;
const UsersIcon = () => <Users size={20} />;
const WalletIcon = () => <Wallet size={20} />;
const HomeIcon = () => <Home size={16} className="text-gray-500"/>; 
const ShoppingIcon = () => <ShoppingBag size={16} className="text-gray-500"/>;
const CoffeeIcon = () => <Coffee size={16} className="text-gray-500"/>;
const CarIcon = () => <Car size={16} className="text-gray-500"/>;
const UtensilsIcon = () => <Utensils size={16} className="text-gray-500"/>;

const OverviewCard = ({ title, value, subValue, icon }) => (
  <div className="flex items-start p-5 bg-white rounded-xl shadow-sm border border-gray-100 transition-all hover:shadow-md">
    <div className="p-3 bg-blue-50 text-blue-600 rounded-full mr-4 shrink-0">{icon}</div>
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
          return <circle key={index} cx={size / 2} cy={size / 2} r={radius} fill="transparent" stroke={colors[index % colors.length]} strokeWidth={strokeWidth} strokeDasharray={strokeDasharray} strokeDashoffset={strokeDashoffset} strokeLinecap="round" className="transition-all duration-1000 ease-out"/>;
        })}
      </svg>
      <div className="absolute text-center"><p className="text-2xl font-bold text-gray-800">100%</p><p className="text-xs font-medium text-gray-400">완료</p></div>
    </div>
  );
};

export default function ResultPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const tripData = location.state?.tripData;
  
  const [tripPlan, setTripPlan] = useState(null);
  const [activeTab, setActiveTab] = useState('schedule');
  const [isEditMode, setIsEditMode] = useState(false);
  const [editingSlot, setEditingSlot] = useState(null);
  const [editPrompt, setEditPrompt] = useState("");
  const [isModifying, setIsModifying] = useState(false);

  useEffect(() => {
    if (!tripData) { navigate('/planner'); return; }

    const destName = tripData.destination ? tripData.destination.split('(')[0].trim() : "여행지";
    
    const budget = parseInt(tripData.budget || tripData.per_person_budget || 0, 10);
    const partySize = parseInt(tripData.partySize || tripData.party_size || tripData.head_count || 1, 10);
    const totalCost = tripData.total_cost || (budget * partySize);

    let durationStr = tripData.durationText;
    const startDate = tripData.startDate || tripData.start_date;
    const endDate = tripData.endDate || tripData.end_date;

    if (!durationStr && startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
        durationStr = `${diffDays}박 ${diffDays + 1}일`;
    }

    // schedule 데이터 안전 처리
    let safeSchedule = [];
    if (Array.isArray(tripData.schedule)) {
        safeSchedule = tripData.schedule;
    } else if (tripData.content && Array.isArray(tripData.content.schedule)) {
        safeSchedule = tripData.content.schedule;
    }

    // 💡 [수정됨] 항공/숙소 데이터 추출 로직 강화
    // 백엔드에서 flights, hotels로 보내주는 경우와 mcp_fetched_data 내부에 있는 경우 모두 대응
    let flights = [];
    if (tripData.flights && Array.isArray(tripData.flights) && tripData.flights.length > 0) {
        flights = tripData.flights;
    } else if (tripData.raw_data?.mcp_fetched_data?.flight_quote) {
        flights = [tripData.raw_data.mcp_fetched_data.flight_quote];
    }

    let hotels = [];
    if (tripData.hotels && Array.isArray(tripData.hotels) && tripData.hotels.length > 0) {
        hotels = tripData.hotels;
    } else if (tripData.raw_data?.mcp_fetched_data?.hotel_quote) {
        hotels = [tripData.raw_data.mcp_fetched_data.hotel_quote];
    }

    setTripPlan({
      trip_summary: tripData.trip_summary || `${destName} 여행 계획`,
      total_cost: totalCost,
      per_person_budget: budget,
      startDate: startDate,
      endDate: endDate,
      durationText: durationStr || "기간 미정",
      head_count: partySize,
      activity_distribution: tripData.activity_distribution || [
        { name: '관광', value: 40 }, { name: '쇼핑', value: 30 }, { name: '휴식', value: 30 }
      ],
      // 추출한 데이터 적용
      flights: flights,
      hotels: hotels,
      schedule: safeSchedule 
    });
  }, [tripData, navigate]);

  const handleAiModify = async () => {
    if (!editPrompt.trim()) return;
    setIsModifying(true);
    setTimeout(() => {
      const newPlan = { ...tripPlan };
      if (newPlan.schedule[editingSlot.dayIndex] && newPlan.schedule[editingSlot.dayIndex].events[editingSlot.eventIndex]) {
          newPlan.schedule[editingSlot.dayIndex].events[editingSlot.eventIndex].description = `[AI 수정됨] ${editPrompt}`;
          setTripPlan(newPlan);
      }
      setIsModifying(false);
      setEditingSlot(null); 
      setEditPrompt("");
    }, 1500);
  };

  if (!tripPlan) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="flex flex-col items-center gap-4"><Loader2 className="animate-spin text-blue-600" size={32}/><span className="text-gray-500 font-medium">여행 계획을 불러오는 중...</span></div></div>;
  
  const bestFlight = tripPlan.flights[0] || {};
  const bestHotel = tripPlan.hotels[0] || {};

  return (
    <div className="w-full max-w-7xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden animate-fade-in relative pb-12 my-8">
      {/* 상단 배너 */}
      <div className="relative h-80 bg-cover bg-center group" style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1920&q=80)' }}>
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent"></div>
        <div className="absolute bottom-0 left-0 w-full p-8 text-white transform translate-y-2 group-hover:translate-y-0 transition-transform duration-500">
          <h1 className="text-4xl md:text-5xl font-extrabold mb-3 tracking-tight shadow-sm">{tripPlan.trip_summary}</h1>
          <div className="flex flex-wrap items-baseline gap-3 opacity-90">
            <p className="text-lg font-medium">총 예상 비용 <span className="font-bold text-2xl text-yellow-300">{(tripPlan.total_cost || 0).toLocaleString()} KRW</span></p>
            <span className="text-white/60">|</span>
            <p className="text-sm text-white/80">1인당 {(tripPlan.per_person_budget || 0).toLocaleString()} KRW</p>
          </div>
        </div>
      </div>

      {/* 메인 컨텐츠 그리드 */}
      <div className="p-6 md:p-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 좌측 사이드: 개요 및 차트 */}
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
            <OverviewCard title="1인 예산" value={`${(tripPlan.per_person_budget || 0).toLocaleString()} KRW`} icon={<WalletIcon size={20} />} />
          </div>
        </div>

        {/* 우측 메인: 탭 컨텐츠 */}
        <div className="lg:col-span-2 space-y-8">
          <div className="flex gap-2 border-b border-gray-200 overflow-x-auto">
            {[
              { id: 'schedule', label: '상세 일정', icon: <Calendar size={18} /> },
              { id: 'flights', label: '항공권 추천', icon: <Plane size={18} /> },
              { id: 'hotels', label: '숙소 추천', icon: <BedDouble size={18} /> }
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
          
          <div className="min-h-[400px]">
            {activeTab === 'schedule' && (
              <div className="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-100 relative animate-in fade-in slide-in-from-bottom-2">
                {/* 지도 플레이스홀더 */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden group mb-8">
                    <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                        <h3 className="text-sm font-bold text-gray-700 flex items-center gap-2"><MapPin size={16} className="text-red-500" /> 예상 경로</h3>
                        <button className="text-blue-600 text-xs font-medium hover:underline">크게 보기</button>
                    </div>
                    <div className="h-64 bg-gray-100 relative flex items-center justify-center overflow-hidden">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/USA_location_map.svg/1200px-USA_location_map.svg.png" alt="Map Placeholder" className="absolute inset-0 w-full h-full object-cover opacity-30 grayscale group-hover:grayscale-0 transition-all duration-500" />
                        <div className="z-10 bg-white/90 backdrop-blur-sm px-4 py-2 rounded-full shadow-sm flex items-center gap-2"><MapPin className="text-red-500 animate-bounce" size={16} /><span className="font-bold text-gray-700 text-sm">지도 영역</span></div>
                    </div>
                </div>

                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-gray-800">일정표</h3>
                    <button onClick={() => { setIsEditMode(!isEditMode); setEditingSlot(null); }} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${isEditMode ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-200' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
                        {isEditMode ? <Check size={16} /> : <Edit2 size={16} />} {isEditMode ? '수정 종료' : '일정 수정하기'}
                    </button>
                </div>
                
                {isEditMode && !editingSlot && <div className="mb-4 p-3 bg-blue-50 text-blue-700 text-sm rounded-lg flex items-center gap-2 animate-in fade-in"><Sparkles size={16} />수정하고 싶은 일정을 클릭하세요. AI가 도와드립니다!</div>}
                
                <div className="space-y-8 relative before:absolute before:inset-0 before:left-4 before:top-4 before:w-0.5 before:bg-gray-200 before:h-full">
                  {tripPlan.schedule && tripPlan.schedule.length > 0 ? (
                    tripPlan.schedule.map((dayPlan, idx) => (
                    <div key={idx} className="relative pl-10">
                      <div className="absolute left-0 top-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md ring-4 ring-white z-10">{dayPlan.day}</div>
                      <div className="mb-4">
                        <h4 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                            {dayPlan.date} <span className="text-sm font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">{dayPlan.full_date || tripPlan.startDate}</span>
                        </h4>
                      </div>
                      <ul className="space-y-3">
                        {dayPlan.events && dayPlan.events.map((event, eIdx) => { 
                            const isEditing = editingSlot?.dayIndex === idx && editingSlot?.eventIndex === eIdx; 
                            return (
                                <li key={eIdx} onClick={() => isEditMode && !isEditing && setEditingSlot({ dayIndex: idx, eventIndex: eIdx })} className={`relative flex items-start bg-gray-50 p-4 rounded-xl border transition-all ${isEditMode && !isEditing ? 'cursor-pointer hover:border-blue-400 hover:shadow-md hover:-translate-y-0.5' : 'border-gray-100'} ${isEditing ? 'border-blue-500 ring-2 ring-blue-100 bg-white shadow-lg z-10' : ''}`}>
                                    <span className="flex-shrink-0 mr-4 mt-1 text-gray-500 p-2 bg-white rounded-lg shadow-sm">
                                        {event.icon === "plane" ? <Plane size={18} className="text-blue-500" /> : event.icon === "shopping" ? <ShoppingIcon size={18} className="text-purple-500" /> : event.icon === "utensils" ? <UtensilsIcon size={18} className="text-orange-500" /> : event.icon === "home" ? <HomeIcon size={18} className="text-green-500" /> : event.icon === "coffee" ? <CoffeeIcon size={18} className="text-brown-500" /> : event.icon === "car" ? <CarIcon size={18} className="text-gray-600" /> : <span className="text-sm">●</span>}
                                    </span>
                                    <div className="flex-1">
                                        {isEditing ? (
                                            <div className="animate-in fade-in zoom-in-95 duration-200">
                                                <div className="flex justify-between items-center mb-2"><p className="font-bold text-blue-700 text-sm">{event.time_slot} 일정 수정</p><button onClick={(e) => { e.stopPropagation(); setEditingSlot(null); }} className="text-gray-400 hover:text-gray-600"><XCircle size={18}/></button></div>
                                                <textarea autoFocus className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none mb-3 resize-none" rows={3} placeholder={`AI에게 요청: "${event.description}" 대신 다른 걸 추천해줘`} value={editPrompt} onChange={(e) => setEditPrompt(e.target.value)} onClick={(e) => e.stopPropagation()} />
                                                <div className="flex justify-end gap-2"><button onClick={(e) => { e.stopPropagation(); handleAiModify(); }} disabled={isModifying || !editPrompt.trim()} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-700 flex items-center gap-1 disabled:bg-gray-300">{isModifying ? <Loader2 className="animate-spin" size={14} /> : <Sparkles size={14} />}{isModifying ? '수정 중...' : 'AI 수정 요청'}</button></div>
                                            </div>
                                        ) : (
                                            <div><p className="font-bold text-gray-800 text-sm mb-0.5">{event.time_slot}</p><p className="text-gray-600 text-sm leading-relaxed">{event.description}</p>{isEditMode && <p className="text-xs text-blue-500 mt-2 font-medium">클릭하여 수정하기</p>}</div>
                                        )}
                                    </div>
                                </li>
                            ); 
                        })}
                      </ul>
                    </div>
                  ))
                  ) : (
                    <div className="text-center text-gray-500 py-10">일정 정보가 없습니다.</div>
                  )}
                </div>
              </div>
            )}
            
            {/* 항공권 탭 */}
            {activeTab === 'flights' && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 text-blue-800 text-sm mb-4 flex items-center gap-2"><Sparkles size={16} />AI가 분석한 최적의 항공권을 추천해 드립니다.</div>
                {tripPlan.flights && tripPlan.flights.length > 0 ? (
                    <div className="bg-white rounded-2xl overflow-hidden shadow-md border border-gray-200 group hover:shadow-lg transition-all">
                        <div className="flex flex-col md:flex-row h-full">
                            <div className="relative md:w-2/5 h-64 md:h-auto bg-gray-100 flex items-center justify-center overflow-hidden">
                                <img src={bestFlight.image || "https://images.unsplash.com/photo-1436491865332-7a6153217f27?w=800&q=80"} alt="Flight" className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
                                <div className="absolute top-3 left-3 bg-black/60 text-white px-3 py-1 rounded-full text-xs font-bold backdrop-blur-sm">BEST CHOICE</div>
                            </div>
                            <div className="p-8 flex-1 flex flex-col justify-center">
                                <div className="flex items-center gap-4 mb-6"><div className="w-14 h-14 bg-blue-50 rounded-full flex items-center justify-center text-blue-600 shrink-0 border border-blue-100"><Plane size={28} /></div><div><h4 className="text-2xl font-bold text-gray-900">{bestFlight.airline || '항공사 미정'}</h4><p className="text-gray-500 font-medium">{bestFlight.flightNo || '-'} • {bestFlight.type || '직항'}</p></div></div>
                                <div className="grid grid-cols-2 gap-6 border-t border-gray-100 pt-6 mb-8"><div><p className="text-sm text-gray-400 mb-1">비행 시간</p><p className="font-bold text-xl text-gray-800">{bestFlight.time || '-'}</p></div><div><p className="text-sm text-gray-400 mb-1">소요 시간</p><p className="font-bold text-xl text-gray-800">{bestFlight.duration || '-'}</p></div></div>
                                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-gray-100"><div><p className="text-xs text-gray-400 mb-1">예상 가격 (1인, 왕복)</p><p className="text-3xl font-extrabold text-blue-600">{(bestFlight.price || 0).toLocaleString()}<span className="text-lg font-medium text-gray-500 ml-1">원</span></p></div><button className="w-full sm:w-auto bg-black text-white px-8 py-3.5 rounded-xl font-bold hover:bg-gray-800 transition-all shadow-lg flex items-center justify-center gap-2">예매하러 가기 <ArrowRight size={18} /></button></div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="text-center text-gray-500 py-10">추천 항공권 정보가 없습니다.</div>
                )}
              </div>
            )}
            
            {/* 숙소 탭 */}
            {activeTab === 'hotels' && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 text-blue-800 text-sm mb-4 flex items-center gap-2"><Sparkles size={16} />여행 스타일에 딱 맞는 최고의 숙소를 추천해 드립니다.</div>
                {tripPlan.hotels && tripPlan.hotels.length > 0 ? (
                    <div className="bg-white rounded-2xl overflow-hidden shadow-md border border-gray-200 group hover:shadow-lg transition-all">
                        <div className="flex flex-col md:flex-row h-full">
                            <div className="relative md:w-2/5 h-64 md:h-auto overflow-hidden">
                                <img src={bestHotel.image || "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"} alt={bestHotel.name} className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
                                <div className="absolute top-4 left-4 bg-black/60 backdrop-blur px-3 py-1 rounded-full text-xs font-bold text-white flex items-center gap-1">BEST STAY</div>
                                <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur px-3 py-1.5 rounded-lg text-sm font-bold text-yellow-600 flex items-center gap-1 shadow-sm"><Star size={16} fill="currentColor" /> {bestHotel.rating || 4.5}</div>
                            </div>
                            <div className="p-8 flex-1 flex flex-col justify-center">
                                <div className="mb-6">
                                    <div className="flex flex-wrap gap-2 mb-3">{(bestHotel.tags || []).map((tag, i) => (<span key={i} className="text-xs bg-blue-50 text-blue-600 px-3 py-1 rounded-full font-medium border border-blue-100">{tag}</span>))}</div>
                                    <h4 className="text-3xl font-bold text-gray-900 mb-2">{bestHotel.name || '추천 호텔'}</h4>
                                    <p className="text-gray-500 flex items-center gap-1.5"><MapPin size={16} /> {bestHotel.address || '시내 중심가'}</p>
                                </div>
                                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-gray-100 mt-auto"><div><p className="text-xs text-gray-400 mb-1">1박 기준 (세금 포함)</p><p className="text-3xl font-extrabold text-blue-600">{(bestHotel.price || 0).toLocaleString()}<span className="text-lg font-medium text-gray-500 ml-1">원</span></p></div><button className="w-full sm:w-auto bg-black text-white px-8 py-3.5 rounded-xl font-bold hover:bg-gray-800 transition-all shadow-lg flex items-center justify-center gap-2">객실 확인하기 <ArrowRight size={18} /></button></div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="text-center text-gray-500 py-10">추천 숙소 정보가 없습니다.</div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="text-center mt-8 mb-4"><button onClick={() => navigate('/planner')} className="bg-gray-900 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-lg hover:bg-gray-800 hover:shadow-xl transform hover:-translate-y-0.5 transition-all">다른 여행 계획하기</button></div>
    </div>
  );
}