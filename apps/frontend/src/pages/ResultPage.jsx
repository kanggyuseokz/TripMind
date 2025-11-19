// apps/frontend/src/pages/ResultPage.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Plane, Calendar, Users, Wallet, X, MapPin, ShoppingBag, Coffee, Car, Utensils, Home
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

// --- 차트 및 요약 컴포넌트 ---
const OverviewCard = ({ title, value, icon }) => (
  <div className="flex items-center p-4 bg-white rounded-lg shadow-sm border border-gray-100">
    <div className="p-2 bg-blue-100 text-blue-600 rounded-full mr-3">{icon}</div>
    <div>
      <p className="text-xs text-gray-500">{title}</p>
      <p className="font-semibold text-lg text-gray-800">{value}</p>
    </div>
  </div>
);

const DonutChart = ({ data, size = 100, strokeWidth = 15 }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;
  const colors = ['#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981'];

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="absolute">
        {data.map((item, index) => {
          const dasharray = `${(item.value / 100) * circumference} ${circumference}`;
          const currentOffset = circumference - offset;
          offset += (item.value / 100) * circumference;
          return (
            <circle key={index} cx={size / 2} cy={size / 2} r={radius} fill="transparent" stroke={colors[index % colors.length]} strokeWidth={strokeWidth} strokeDasharray={dasharray} strokeDashoffset={currentOffset} transform={`rotate(-90 ${size / 2} ${size / 2})`} className="transition-all duration-500 ease-out"/>
          );
        })}
      </svg>
      <div className="text-center"><p className="text-xl font-bold text-gray-800">100%</p><p className="text-xs text-gray-500">완료</p></div>
    </div>
  );
};

export default function ResultPage() {
  const navigate = useNavigate();
  const location = useLocation();
  // PlannerPage에서 넘겨준 데이터를 받습니다.
  const tripData = location.state?.tripData;

  const [tripPlan, setTripPlan] = useState(null);

  useEffect(() => {
    // 데이터가 없으면 플래너 페이지로 돌려보냄
    if (!tripData) {
      navigate('/planner');
      return;
    }

    // 실제로는 여기서 백엔드 API를 호출해서 상세 플랜을 받아와야 합니다.
    // 지금은 tripData를 기반으로 더미 결과를 생성합니다.
    const destName = tripData.destination.split('(')[0].trim() || "여행지";
    const budget = parseInt(tripData.budget, 10) || 0;
    const partySize = parseInt(tripData.partySize, 10) || 1;

    setTripPlan({
      trip_summary: `${destName} 여행 계획`,
      total_cost: budget * partySize,
      per_person_budget: budget,
      duration: `${tripData.startDate} ~ ${tripData.endDate}`,
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
         // ... (더 많은 일정 추가 가능)
      ]
    });
  }, [tripData, navigate]);

  if (!tripPlan) return <div className="min-h-screen flex items-center justify-center">로딩 중...</div>;

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8 font-sans text-gray-900">
      <div className="w-full max-w-7xl mx-auto bg-white rounded-lg shadow-2xl overflow-hidden animate-fade-in relative pb-10">
        
        {/* 상단 바 */}
        <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-center bg-white/70 backdrop-blur-sm z-10 border-b border-gray-100">
          <div className="flex items-center gap-2 text-gray-800 font-bold text-xl">
            <Plane size={24} className="text-blue-600" /> TripMind
          </div>
          <div className="flex items-center gap-4">
            <button className="text-gray-600 hover:text-black">💾 저장</button>
            <button className="text-gray-600 hover:text-black">✉ 공유</button>
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">U</div>
            <button onClick={() => navigate('/')} className="text-gray-500 hover:text-gray-700">
              <X size={24} />
            </button>
          </div>
        </div>

        {/* 히어로 이미지 섹션 */}
        <div className="relative h-64 bg-cover bg-center" style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1920&q=80)' }}>
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
          <div className="absolute bottom-6 left-8 text-white">
            <h1 className="text-4xl font-extrabold mb-2">{tripPlan.trip_summary}</h1>
            <p className="text-lg opacity-90">총 예상 비용: {tripPlan.total_cost.toLocaleString()} KRW</p>
            <p className="text-sm opacity-70">(1인당 {tripPlan.per_person_budget.toLocaleString()} KRW)</p>
          </div>
        </div>

        {/* 메인 콘텐츠 영역 */}
        <div className="p-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* 왼쪽: 개요 및 그래프 */}
          <div className="lg:col-span-1 space-y-8">
            {/* 활동 비율 */}
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">활동 비율</h3>
              <div className="flex items-center justify-around gap-4">
                <DonutChart data={tripPlan.activity_distribution} size={150} strokeWidth={20} />
                <div className="space-y-2">
                  {tripPlan.activity_distribution.map((item, idx) => (
                    <div key={idx} className="flex items-center">
                      <span className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: ['#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981'][idx % 5] }}></span>
                      <span className="text-gray-700">{item.name} {item.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 여행 개요 */}
            <div className="space-y-4">
              <OverviewCard title="여행 기간" value={tripPlan.duration} icon={<CalendarIcon />} />
              <OverviewCard title="인원" value={`${tripPlan.head_count}명`} icon={<UsersIcon />} />
              <OverviewCard title="1인 예산" value={`${tripPlan.per_person_budget.toLocaleString()} KRW`} icon={<WalletIcon />} />
            </div>
          </div>

          {/* 오른쪽: 지도 및 일정표 */}
          <div className="lg:col-span-2 space-y-8">
            {/* 지도 (더미) */}
            <div className="bg-white rounded-lg shadow-md border border-gray-100 overflow-hidden">
              <div className="p-4 border-b border-gray-100 flex justify-between items-center">
                <h3 className="text-xl font-semibold text-gray-800">예상 경로</h3>
                <button className="text-blue-600 text-sm">자세히 보기</button>
              </div>
              <div className="h-96 bg-gray-200 flex items-center justify-center text-gray-500">
                <img src="https://via.placeholder.com/600x400?text=Map+Placeholder" alt="Map Placeholder" className="w-full h-full object-cover opacity-70" />
                <span className="absolute text-xl font-bold text-white bg-black/50 p-2 rounded">지도 표시 영역</span>
              </div>
            </div>

            {/* 일정표 */}
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">상세 일정</h3>
              <div className="space-y-6">
                {tripPlan.schedule.map((dayPlan, idx) => (
                  <div key={idx} className="border-b border-gray-100 pb-4 last:border-b-0 last:pb-0">
                    <h4 className="text-lg font-bold text-gray-700 mb-3 flex items-center">
                      <CalendarIcon size={18} className="mr-2 text-blue-500" /> Day {dayPlan.day} ({dayPlan.date})
                    </h4>
                    <ul className="space-y-2 pl-2">
                      {dayPlan.events.map((event, eIdx) => (
                        <li key={eIdx} className="flex items-start">
                          <span className="flex-shrink-0 mr-3 mt-1 text-gray-500">
                            {event.icon === "plane" ? <Plane size={16} /> :
                             event.icon === "shopping" ? <ShoppingIcon /> :
                             event.icon === "utensils" ? <UtensilsIcon /> :
                             event.icon === "home" ? <HomeIcon /> :
                             event.icon === "coffee" ? <CoffeeIcon /> :
                             event.icon === "car" ? <CarIcon /> : <span className="text-sm">●</span>}
                          </span>
                          <div>
                            <p className="font-semibold text-gray-800">{event.time_slot}</p>
                            <p className="text-gray-600 text-sm">{event.description}</p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>

        <div className="text-center mt-10">
          <button onClick={() => navigate('/planner')} className="bg-gray-800 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors">
            다시 계획하기
          </button>
        </div>
      </div>
    </div>
  );
}