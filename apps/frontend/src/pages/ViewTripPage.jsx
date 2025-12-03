import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Plane, Calendar, Users, Wallet, MapPin, ShoppingBag, Coffee, Car, Utensils, Home, Loader2, Star, BedDouble, ArrowRight, Trash2, Edit, Clock } from 'lucide-react';

// 아이콘 컴포넌트들
const CalendarIcon = () => <Calendar size={20} />;
const UsersIcon = () => <Users size={20} />;
const WalletIcon = () => <Wallet size={20} />;
const HomeIcon = () => <Home size={16} className="text-gray-500"/>; 
const ShoppingIcon = () => <ShoppingBag size={16} className="text-gray-500"/>;
const CoffeeIcon = () => <Coffee size={16} className="text-gray-500"/>;
const CarIcon = () => <Car size={16} className="text-gray-500"/>;
const UtensilsIcon = () => <Utensils size={16} className="text-gray-500"/>;

// ✅ 시간 포맷팅
const formatTime = (isoString) => {
  if (!isoString) return '-';
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
  } catch {
    return '-';
  }
};

const formatDate = (isoString) => {
  if (!isoString) return '-';
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  } catch {
    return '-';
  }
};

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

export default function ViewTripPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tripPlan, setTripPlan] = useState(null);
  const [activeTab, setActiveTab] = useState('schedule');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrip = async () => {
      try {
        const token = localStorage.getItem('token');
        
        if (!token) {
          console.error('No access token found');
          alert('로그인이 필요합니다.');
          navigate('/login');
          return;
        }

        console.log(`[ViewTripPage] Fetching trip ${id}...`);
        
        const response = await fetch(`http://127.0.0.1:8080/api/trip/saved/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error('[ViewTripPage] Error response:', errorData);
          throw new Error(errorData.error || 'Failed to fetch trip');
        }

        const data = await response.json();
        console.log('[ViewTripPage] Trip data received:', data);
        
        const budget = parseInt(data.budget || data.total_cost || 0, 10);
        const partySize = parseInt(data.pax || data.party_size || data.head_count || 1, 10);
        const totalCost = data.budget || data.total_cost || (budget * partySize);

        // ✅ 날짜 계산
        let durationStr = "";
        if (data.start_date && data.end_date) {
          const start = new Date(data.start_date);
          const end = new Date(data.end_date);
          const diffDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
          durationStr = `${diffDays}박 ${diffDays + 1}일`;
        }

        // ✅ 항공/호텔 데이터 추출
        const rawData = data.raw_data || {};
        const mcpData = rawData.mcp_fetched_data || {};

        let flights = [];
        if (mcpData.flight_quote && Object.keys(mcpData.flight_quote).length > 0) {
          flights = [mcpData.flight_quote];
        } else if (mcpData.flight_candidates && mcpData.flight_candidates.length > 0) {
          flights = mcpData.flight_candidates.slice(0, 1);
        }

        let hotels = [];
        if (mcpData.hotel_quote && Array.isArray(mcpData.hotel_quote)) {
          hotels = mcpData.hotel_quote.slice(0, 1);
        } else if (mcpData.hotel_candidates && mcpData.hotel_candidates.length > 0) {
          hotels = mcpData.hotel_candidates.slice(0, 1);
        }

        // ✅ 날씨 데이터
        const weatherByDate = mcpData.weather_by_date || {};

        setTripPlan({
          id: data.id,
          trip_summary: data.trip_summary || `${data.destination} 여행`,
          total_cost: totalCost,
          per_person_budget: budget,
          startDate: data.start_date,
          endDate: data.end_date,
          durationText: durationStr || "기간 미정",
          head_count: partySize,
          activity_distribution: [
            { name: '관광', value: 40 },
            { name: '쇼핑', value: 30 },
            { name: '휴식', value: 30 }
          ],
          flights: flights,
          hotels: hotels,
          schedule: data.schedule || [],
          weatherByDate: weatherByDate // ✅ 추가
        });

        setLoading(false);

      } catch (error) {
        console.error('Error fetching trip:', error);
        alert('여행 정보를 불러오는데 실패했습니다.');
        navigate('/saved');
      }
    };

    fetchTrip();
  }, [id, navigate]);

  const handleDelete = async () => {
    if (!window.confirm('정말로 이 여행을 삭제하시겠습니까?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:8080/api/trip/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete trip');

      alert('여행이 삭제되었습니다.');
      navigate('/saved');
    } catch (error) {
      console.error('Error deleting trip:', error);
      alert('삭제에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="animate-spin text-blue-600" size={32}/>
          <span className="text-gray-500 font-medium">여행 정보를 불러오는 중...</span>
        </div>
      </div>
    );
  }

  if (!tripPlan) return null;
  
  const bestFlight = tripPlan.flights[0] || {};
  const bestHotel = tripPlan.hotels[0] || {};

  return (
    <div className="w-full max-w-7xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden animate-fade-in relative pb-12 my-8">
      {/* 상단 배너 */}
      <div className="relative h-80 bg-cover bg-center group" style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1920&q=80)' }}>
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent"></div>
        
        <div className="absolute top-4 right-4 flex gap-2">
          <button
            onClick={() => navigate(`/planner?edit=${id}`)}
            className="bg-white/90 backdrop-blur hover:bg-white text-gray-800 px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all"
          >
            <Edit size={16} /> 수정
          </button>
          <button
            onClick={handleDelete}
            className="bg-red-500/90 backdrop-blur hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all"
          >
            <Trash2 size={16} /> 삭제
          </button>
        </div>

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
        {/* 좌측 사이드 */}
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

        {/* 우측 메인 */}
        <div className="lg:col-span-2 space-y-8">
          <div className="flex gap-2 border-b border-gray-200 overflow-x-auto">
            {[
              { id: 'schedule', label: '상세 일정', icon: <Calendar size={18} /> },
              { id: 'flights', label: '항공권', icon: <Plane size={18} /> },
              { id: 'hotels', label: '숙소', icon: <BedDouble size={18} /> }
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
            {/* 일정 탭 */}
            {activeTab === 'schedule' && (
              <div className="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-100 animate-in fade-in">
                <h3 className="text-xl font-bold text-gray-800 mb-6">일정표</h3>
                
                <div className="space-y-8 relative before:absolute before:inset-0 before:left-4 before:top-4 before:w-0.5 before:bg-gray-200 before:h-full">
                  {tripPlan.schedule && tripPlan.schedule.length > 0 ? (
                    tripPlan.schedule.map((dayPlan, idx) => (
                    <div key={idx} className="relative pl-10">
                      <div className="absolute left-0 top-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md ring-4 ring-white z-10">{dayPlan.day}</div>
                      <div className="mb-4">
                        <h4 className="text-lg font-bold text-gray-900">{dayPlan.date || `Day ${dayPlan.day}`}</h4>
                        {/* ✅ 날씨 표시 */}
                        {tripPlan.weatherByDate && tripPlan.weatherByDate[dayPlan.full_date] && (
                          <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                            <span>🌤️ {tripPlan.weatherByDate[dayPlan.full_date].condition}</span>
                            <span>{tripPlan.weatherByDate[dayPlan.full_date].temp}°C</span>
                          </div>
                        )}
                      </div>
                      <ul className="space-y-3">
                        {dayPlan.events && dayPlan.events.map((event, eIdx) => (
                          <li key={eIdx} className="relative flex items-start bg-gray-50 p-4 rounded-xl border border-gray-100">
                            <span className="flex-shrink-0 mr-4 mt-1 text-gray-500 p-2 bg-white rounded-lg shadow-sm">
                              {event.icon === "plane" ? <Plane size={18} className="text-blue-500" /> : 
                               event.icon === "shopping" ? <ShoppingIcon /> : 
                               event.icon === "utensils" ? <UtensilsIcon /> : 
                               event.icon === "home" ? <HomeIcon /> : 
                               event.icon === "coffee" ? <CoffeeIcon /> : 
                               event.icon === "car" ? <CarIcon /> : 
                               <Clock size={18} className="text-gray-400" />}
                            </span>
                            <div className="flex-1">
                              <p className="font-bold text-gray-800 text-sm mb-0.5">{event.time_slot}</p>
                              <p className="text-gray-600 text-sm leading-relaxed">{event.description}</p>
                              {event.poi_rating && (
                                <div className="flex items-center gap-1 mt-1 text-xs text-yellow-600">
                                  <Star size={12} fill="currentColor" />
                                  <span>{event.poi_rating}</span>
                                </div>
                              )}
                            </div>
                          </li>
                        ))}
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
              <div className="space-y-6 animate-in fade-in">
                {tripPlan.flights && tripPlan.flights.length > 0 ? (
                  <div className="bg-white rounded-2xl overflow-hidden shadow-md border border-gray-200">
                    <div className="p-8">
                      <div className="flex items-center gap-4 mb-6">
                        <div className="w-14 h-14 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
                          <Plane size={28} />
                        </div>
                        <div>
                          <h4 className="text-2xl font-bold text-gray-900">{bestFlight.airline || '항공편 정보'}</h4>
                          <p className="text-gray-500 font-medium">{bestFlight.origin} → {bestFlight.destination}</p>
                        </div>
                      </div>

                      {/* ✅ 출입국 시간 표시 */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        {/* 출국 */}
                        <div className="bg-blue-50 p-4 rounded-xl">
                          <div className="flex items-center gap-2 mb-3">
                            <Plane size={16} className="text-blue-600" />
                            <span className="font-bold text-blue-900">출국</span>
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between items-center">
                              <div>
                                <div className="text-xs text-gray-600">출발</div>
                                <div className="text-lg font-bold text-gray-900">{formatTime(bestFlight.outbound_departure_time)}</div>
                                <div className="text-xs text-gray-500">{formatDate(bestFlight.outbound_departure_time)}</div>
                              </div>
                              <ArrowRight size={20} className="text-gray-400" />
                              <div className="text-right">
                                <div className="text-xs text-gray-600">도착</div>
                                <div className="text-lg font-bold text-gray-900">{formatTime(bestFlight.outbound_arrival_time)}</div>
                                <div className="text-xs text-gray-500">{formatDate(bestFlight.outbound_arrival_time)}</div>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* 입국 */}
                        {bestFlight.inbound_departure_time && (
                          <div className="bg-green-50 p-4 rounded-xl">
                            <div className="flex items-center gap-2 mb-3">
                              <Plane size={16} className="text-green-600 transform rotate-180" />
                              <span className="font-bold text-green-900">입국</span>
                            </div>
                            <div className="space-y-2">
                              <div className="flex justify-between items-center">
                                <div>
                                  <div className="text-xs text-gray-600">출발</div>
                                  <div className="text-lg font-bold text-gray-900">{formatTime(bestFlight.inbound_departure_time)}</div>
                                  <div className="text-xs text-gray-500">{formatDate(bestFlight.inbound_departure_time)}</div>
                                </div>
                                <ArrowRight size={20} className="text-gray-400" />
                                <div className="text-right">
                                  <div className="text-xs text-gray-600">도착</div>
                                  <div className="text-lg font-bold text-gray-900">{formatTime(bestFlight.inbound_arrival_time)}</div>
                                  <div className="text-xs text-gray-500">{formatDate(bestFlight.inbound_arrival_time)}</div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center justify-between pt-6 border-t border-gray-100">
                        <div>
                          <p className="text-xs text-gray-400 mb-1">예상 가격 (1인, 왕복)</p>
                          <p className="text-3xl font-extrabold text-blue-600">
                            {(bestFlight.price_krw || bestFlight.price || 0).toLocaleString()}
                            <span className="text-lg font-medium text-gray-500 ml-1">원</span>
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-10">항공편 정보가 없습니다.</div>
                )}
              </div>
            )}
            
            {/* 숙소 탭 */}
            {activeTab === 'hotels' && (
              <div className="space-y-6 animate-in fade-in">
                {tripPlan.hotels && tripPlan.hotels.length > 0 ? (
                  <div className="bg-white rounded-2xl overflow-hidden shadow-md border border-gray-200">
                    <div className="flex flex-col md:flex-row h-full">
                      <div className="relative md:w-2/5 h-64 md:h-auto overflow-hidden">
                        <img src="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80" alt={bestHotel.name} className="absolute inset-0 w-full h-full object-cover" />
                        <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur px-3 py-1.5 rounded-lg text-sm font-bold text-yellow-600 flex items-center gap-1">
                          <Star size={16} fill="currentColor" /> {bestHotel.rating || 0}
                        </div>
                      </div>
                      <div className="p-8 flex-1 flex flex-col justify-center">
                        <div className="mb-6">
                          <h4 className="text-3xl font-bold text-gray-900 mb-2">{bestHotel.name || '숙소 정보'}</h4>
                          <p className="text-gray-500 flex items-center gap-1.5">
                            <MapPin size={16} /> {bestHotel.location || '위치 미정'}
                          </p>
                        </div>
                        <div className="flex items-center justify-between pt-6 border-t border-gray-100">
                          <div>
                            <p className="text-xs text-gray-400 mb-1">1박 기준 (세금 포함)</p>
                            <p className="text-3xl font-extrabold text-blue-600">
                              {(bestHotel.price || 0).toLocaleString()}
                              <span className="text-lg font-medium text-gray-500 ml-1">원</span>
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-10">숙소 정보가 없습니다.</div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="text-center mt-8 mb-4 flex gap-4 justify-center">
        <button 
          onClick={() => navigate('/saved')} 
          className="bg-gray-200 text-gray-700 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-300 transition-all"
        >
          목록으로
        </button>
        <button 
          onClick={() => navigate('/planner')} 
          className="bg-gray-900 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-lg hover:bg-gray-800 transition-all"
        >
          새 여행 계획하기
        </button>
      </div>
    </div>
  );
}