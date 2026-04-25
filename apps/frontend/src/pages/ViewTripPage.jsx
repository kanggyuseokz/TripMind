import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Plane, Calendar, Users, Wallet, MapPin, ShoppingBag, Coffee, Car, Utensils, Home, Loader2, Star, BedDouble, ArrowRight, Trash2, Edit, Clock } from 'lucide-react';
import ScheduleEditor from '../components/ScheduleEditor';
import { useToast } from '../components/Toast';

const getBannerImage = (destination) => {
  if (!destination) return 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1920&q=80';
  const keyword = destination.split('/')[0].split('(')[0].trim();
  const images = {
    '오사카': 'https://images.unsplash.com/photo-1590559399607-57523cd47a61?w=1920&q=80',
    '도쿄': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1920&q=80',
    '다낭': 'https://images.unsplash.com/photo-1559592413-7cec430aaec3?w=1920&q=80',
    '제주': 'https://images.unsplash.com/photo-1548115184-bc6544d06a58?w=1920&q=80',
    '파리': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1920&q=80',
    '뉴욕': 'https://images.unsplash.com/photo-1496442226666-8d4a0e2907eb?w=1920&q=80',
    '방콕': 'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=1920&q=80',
    '런던': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=1920&q=80',
    '후쿠오카': 'https://images.unsplash.com/photo-1624329243765-b1e102293478?w=1920&q=80',
    '삿포로': 'https://images.unsplash.com/photo-1579401772658-2029589d980f?w=1920&q=80',
    '서울': 'https://images.unsplash.com/photo-1517154421773-0529f29ea451?w=1920&q=80',
  };
  const key = Object.keys(images).find(k => keyword.includes(k));
  return key ? images[key] : 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1920&q=80';
};

// 기존 코드 그대로...
const CalendarIcon = () => <Calendar size={20} />;
const UsersIcon = () => <Users size={20} />;
const WalletIcon = () => <Wallet size={20} />;
const HomeIcon = () => <Home size={16} className="text-gray-500"/>; 
const ShoppingIcon = () => <ShoppingBag size={16} className="text-gray-500"/>;
const CoffeeIcon = () => <Coffee size={16} className="text-gray-500"/>;
const CarIcon = () => <Car size={16} className="text-gray-500"/>;
const UtensilsIcon = () => <Utensils size={16} className="text-gray-500"/>;

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
  <div className="flex items-start p-5 bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 transition-all hover:shadow-md">
    <div className="p-3 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full mr-4 shrink-0">{icon}</div>
    <div>
      <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{title}</p>
      <p className="font-bold text-lg text-gray-900 dark:text-white dark:text-white">{value}</p>
      {subValue && <p className="text-sm text-gray-400 dark:text-gray-500 mt-0.5">{subValue}</p>}
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
      <div className="absolute text-center"><p className="text-2xl font-bold text-gray-800">{data[0]?.value}%</p><p className="text-xs font-medium text-gray-400">{data[0]?.name}</p></div>
    </div>
  );
};

export default function ViewTripPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [tripPlan, setTripPlan] = useState(null);
  const [activeTab, setActiveTab] = useState('schedule');
  const [loading, setLoading] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [pendingCancelEdit, setPendingCancelEdit] = useState(false);

  const [isEditing, setIsEditing] = useState(false);
  const [originalSchedule, setOriginalSchedule] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchTrip = async () => {
      try {
        const token = localStorage.getItem('token');
        
        if (!token) {
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

        let durationStr = "";
        if (data.start_date && data.end_date) {
          const start = new Date(data.start_date);
          const end = new Date(data.end_date);
          const diffDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
          const nights = diffDays;
          const days = nights + 1;
          durationStr = `${nights}박 ${days}일`;
        }

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

        const weatherByDate = mcpData.weather_by_date || {};

        // ✅ travel_style별 동적 활동 비율 계산
        const getActivityDataByStyle = (travelStyle) => {
          // 🔄 영어 스타일명을 한국어로 매핑
          const englishToKorean = {
            'sightseeing': '관광형',
            'relaxation': '휴양형',
            'activity': '액티비티형', 
            'foodie': '미식형',
            'shopping': '쇼핑형'
          };
          
          const mappedStyle = englishToKorean[travelStyle] || travelStyle;
          
          const styleMap = {
            '휴양형': [
              { name: '휴식', value: 60 },
              { name: '관광', value: 25 },
              { name: '쇼핑', value: 15 }
            ],
            '관광형': [
              { name: '관광', value: 70 },
              { name: '휴식', value: 20 },
              { name: '쇼핑', value: 10 }
            ],
            '미식형': [
              { name: '맛집', value: 50 },
              { name: '관광', value: 30 },
              { name: '휴식', value: 20 }
            ],
            '쇼핑형': [
              { name: '쇼핑', value: 50 },
              { name: '관광', value: 30 },
              { name: '휴식', value: 20 }
            ],
            '액티비티형': [
              { name: '액티비티', value: 60 },
              { name: '관광', value: 25 },
              { name: '휴식', value: 15 }
            ]
          };

          return styleMap[mappedStyle] || [
            { name: '관광', value: 40 },
            { name: '쇼핑', value: 30 },
            { name: '휴식', value: 30 }
          ];
        };

        // ✅ 사용자의 travel_style 추출
        const rawTravelStyle = data.travel_style || 
                             rawData.travel_style || 
                             mcpData?.travel_style ||
                             'sightseeing';
        
        const englishToKorean = {
          'sightseeing': '관광형',
          'relaxation': '휴양형',
          'activity': '액티비티형',
          'foodie': '미식형', 
          'shopping': '쇼핑형'
        };
        
        const userTravelStyle = englishToKorean[rawTravelStyle] || rawTravelStyle;
        const dynamicActivityData = getActivityDataByStyle(userTravelStyle);
        
        console.log("📊 [VIEW] Raw travel style:", rawTravelStyle);
        console.log("📊 [VIEW] Mapped travel style:", userTravelStyle);

        const tripData = {
          id: data.id,
          destination: data.destination || '',
          trip_summary: data.trip_summary || `${data.destination} 여행`,
          total_cost: totalCost,
          per_person_budget: budget,
          startDate: data.start_date,
          endDate: data.end_date,
          durationText: durationStr || "기간 미정",
          head_count: partySize,
          activity_distribution: dynamicActivityData, // ✅ 동적 데이터 사용
          flights: flights,
          hotels: hotels,
          schedule: data.schedule || [],
          weatherByDate: weatherByDate,
          // ✅ POI 데이터 추가
          poi_list: mcpData.poi_list || [],
          // ✅ 비용 계산을 위한 데이터 추가  
          travel_style: userTravelStyle,
          selected_flight_cost: data.selected_flight_cost || 0,
          selected_hotel_cost: data.selected_hotel_cost || 0,
          other_costs: data.other_costs || 0,
          cost_calculation: data.cost_calculation || null
        };

        setTripPlan(tripData);
        
        // ✅ 원본 스케줄 백업
        if (data.schedule) {
          setOriginalSchedule(JSON.parse(JSON.stringify(data.schedule)));
        }

        setLoading(false);

      } catch (error) {
        console.error('Error fetching trip:', error);
        toast('여행 정보를 불러오는데 실패했습니다.', 'error');
        navigate('/saved');
      }
    };

    fetchTrip();
  }, [id, navigate]);

  const toggleEditMode = () => {
    if (isEditing) {
      if (JSON.stringify(tripPlan.schedule) !== JSON.stringify(originalSchedule)) {
        setPendingCancelEdit(true);
        return;
      }
    } else {
      setOriginalSchedule(JSON.parse(JSON.stringify(tripPlan.schedule)));
    }
    setIsEditing(!isEditing);
  };

  const confirmCancelEdit = () => {
    setTripPlan(prev => ({
      ...prev,
      schedule: JSON.parse(JSON.stringify(originalSchedule))
    }));
    setIsEditing(false);
    setPendingCancelEdit(false);
  };

  // ✅ 스케줄 변경 핸들러
  const handleScheduleChange = (newSchedule) => {
    setTripPlan(prev => ({
      ...prev,
      schedule: newSchedule
    }));
  };

  // ✅ 수정된 일정 저장
  const handleSaveSchedule = async () => {
    try {
      setSaving(true);
      
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:8080/api/trip/saved/${id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          schedule: tripPlan.schedule,
          updated_at: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error('일정 저장에 실패했습니다.');
      }

      // 성공 - 원본 스케줄 업데이트
      setOriginalSchedule(JSON.parse(JSON.stringify(tripPlan.schedule)));
      setIsEditing(false);
      toast('일정이 성공적으로 저장되었습니다!', 'success');

    } catch (err) {
      console.error('Error saving schedule:', err);
      toast('일정 저장 중 오류가 발생했습니다: ' + err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:8080/api/trip/saved/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to delete trip');

      toast('여행이 삭제되었습니다.', 'success');
      navigate('/saved');
    } catch (error) {
      console.error('Error deleting trip:', error);
      toast('삭제에 실패했습니다.', 'error');
    }
    setShowDeleteConfirm(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="animate-spin text-blue-600" size={32}/>
          <span className="text-gray-500 dark:text-gray-400 font-medium">여행 정보를 불러오는 중...</span>
        </div>
      </div>
    );
  }

  if (!tripPlan) return null;
  
  const bestFlight = tripPlan.flights[0] || {};
  const bestHotel = tripPlan.hotels[0] || {};

  return (
    <div className="w-full max-w-7xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden animate-fade-in relative pb-12 my-8">
      {/* 상단 배너 */}
      <div className="relative h-80 bg-cover bg-center group" style={{ backgroundImage: `url(${getBannerImage(tripPlan.destination || tripPlan.trip_summary)})` }}>
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent"></div>

        <div className="absolute top-4 right-4 flex gap-2">
          {isEditing ? (
            <>
              <button
                onClick={toggleEditMode}
                className="bg-gray-500/90 backdrop-blur hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all"
                disabled={saving}
              >
                취소
              </button>
              <button
                onClick={handleSaveSchedule}
                className="bg-green-500/90 backdrop-blur hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all"
                disabled={saving}
              >
                {saving ? '저장 중...' : '저장'}
              </button>
            </>
          ) : showDeleteConfirm ? (
            <>
              <span className="text-white text-sm font-medium self-center">삭제할까요?</span>
              <button
                onClick={handleDelete}
                className="bg-red-500/90 backdrop-blur hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium text-sm shadow-lg transition-all"
              >
                삭제
              </button>
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="bg-gray-500/90 backdrop-blur hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium text-sm shadow-lg transition-all"
              >
                취소
              </button>
            </>
          ) : (
            <>
              <button
                onClick={toggleEditMode}
                className="bg-white/90 backdrop-blur hover:bg-white text-gray-800 px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all"
              >
                <Edit size={16} /> 수정하기
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="bg-red-500/90 backdrop-blur hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all"
              >
                <Trash2 size={16} /> 삭제
              </button>
            </>
          )}
        </div>

        {isEditing && (
          <div className="absolute top-4 left-4 bg-yellow-500 text-white px-3 py-1 rounded-full text-sm font-medium">
            편집 모드
          </div>
        )}

        {/* 편집 취소 확인 모달 */}
        {pendingCancelEdit && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/60 z-10">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-2xl max-w-sm mx-4 text-center">
              <p className="font-bold text-gray-900 dark:text-white mb-2">변경사항이 있습니다</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">저장하지 않고 종료하면 변경사항이 사라집니다.</p>
              <div className="flex gap-3 justify-center">
                <button onClick={() => { handleSaveSchedule(); setPendingCancelEdit(false); }} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-700">저장 후 종료</button>
                <button onClick={confirmCancelEdit} className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-300">그냥 종료</button>
                <button onClick={() => setPendingCancelEdit(false)} className="bg-white border border-gray-300 text-gray-600 px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-50">계속 편집</button>
              </div>
            </div>
          </div>
        )}

        <div className="absolute bottom-0 left-0 w-full p-8 text-white transform translate-y-2 group-hover:translate-y-0 transition-transform duration-500">
          <h1 className="text-4xl md:text-5xl font-extrabold mb-3 tracking-tight shadow-sm">{tripPlan.trip_summary}</h1>
          <div className="flex flex-wrap items-baseline gap-3 opacity-90">
            <p className="text-lg font-medium">총 예상 비용 <span className="font-bold text-2xl text-yellow-300">{(tripPlan.total_cost || 0).toLocaleString()} KRW</span></p>
            <span className="text-white/60">|</span>
            <p className="text-sm text-white/80">1인당 {(tripPlan.per_person_budget || 0).toLocaleString()} KRW</p>
          </div>
        </div>
      </div>

      {/* 기존 메인 컨텐츠 그리드... */}
      <div className="p-6 md:p-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 좌측 사이드 */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-6 flex items-center gap-2">
              <span className="w-1 h-6 bg-blue-500 rounded-full"></span>
              {tripPlan.travel_style} 활동 비율
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
            
            {/* ✅ 1인 예산을 DB 저장값으로 간단 표시 */}
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
              <div className="flex items-start gap-3">
                <div className="p-3 bg-blue-50 text-blue-600 rounded-full shrink-0">
                  <WalletIcon size={20} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">1인 예산</p>
                  <p className="font-bold text-lg text-gray-900 dark:text-white dark:text-white">₩{(tripPlan.total_cost || 0).toLocaleString()}</p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">실제 계산된 비용</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 우측 메인 */}
        <div className="lg:col-span-2 space-y-8">
          <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
            {[
              { id: 'schedule', label: '상세 일정', icon: <Calendar size={18} /> },
              { id: 'flights', label: '항공권', icon: <Plane size={18} /> },
              { id: 'hotels', label: '숙소', icon: <BedDouble size={18} /> }
            ].map((tab) => (
              <button 
                key={tab.id} 
                onClick={() => setActiveTab(tab.id)} 
                className={`flex items-center gap-2 px-6 py-4 font-bold text-sm transition-all border-b-2 whitespace-nowrap ${activeTab === tab.id ? 'border-black dark:border-white text-black dark:text-white' : 'border-transparent text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'}`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
          
          <div className="min-h-[400px]">
            {/* ✅ 일정 탭 - 편집 모드 추가 */}
            {activeTab === 'schedule' && (
              <div className="bg-white dark:bg-gray-900 p-6 md:p-8 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 animate-in fade-in">
                <h3 className="text-xl font-bold text-gray-800 dark:text-white mb-6 flex items-center gap-2">
                  일정표
                  {isEditing && (
                    <span className="text-sm font-normal text-yellow-600 bg-yellow-50 px-2 py-1 rounded">
                      편집 모드 활성화
                    </span>
                  )}
                </h3>
                
                {isEditing ? (
                  /* ✅ 편집 모드 */
                  <ScheduleEditor
                    schedule={tripPlan.schedule}
                    pois={tripPlan.poi_list || []}
                    onScheduleChange={handleScheduleChange}
                  />
                ) : (
                  /* ✅ 기존 읽기 모드 */
                  <div className="space-y-8 relative before:absolute before:inset-0 before:left-4 before:top-4 before:w-0.5 before:bg-gray-200 before:h-full">
                    {tripPlan.schedule && tripPlan.schedule.length > 0 ? (
                      tripPlan.schedule.map((dayPlan, idx) => (
                      <div key={idx} className="relative pl-10">
                        <div className="absolute left-0 top-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md ring-4 ring-white z-10">{dayPlan.day}</div>
                        <div className="mb-4">
                          <h4 className="text-lg font-bold text-gray-900 dark:text-white dark:text-white">{dayPlan.date || `Day ${dayPlan.day}`}</h4>
                          {tripPlan.weatherByDate && tripPlan.weatherByDate[dayPlan.full_date] && (
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-2">
                              <span>🌤️ {tripPlan.weatherByDate[dayPlan.full_date].condition}</span>
                              <span>{tripPlan.weatherByDate[dayPlan.full_date].temp}°C</span>
                            </div>
                          )}
                        </div>
                        <ul className="space-y-3">
                          {dayPlan.events && dayPlan.events.map((event, eIdx) => (
                            <li key={eIdx} className="relative flex items-start bg-gray-50 dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
                              <span className="flex-shrink-0 mr-4 mt-1 text-gray-500 dark:text-gray-400 p-2 bg-white dark:bg-gray-700 rounded-lg shadow-sm">
                                {event.icon === "plane" ? <Plane size={18} className="text-blue-500" /> : 
                                 event.icon === "shopping" ? <ShoppingIcon /> : 
                                 event.icon === "utensils" ? <UtensilsIcon /> : 
                                 event.icon === "home" ? <HomeIcon /> : 
                                 event.icon === "coffee" ? <CoffeeIcon /> : 
                                 event.icon === "car" ? <CarIcon /> : 
                                 <Clock size={18} className="text-gray-400" />}
                              </span>
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-0.5">
                                  <span className="font-bold text-blue-600 dark:text-blue-400 text-sm">{event.time_slot}</span>
                                  {(event.place_name || event.poi_name) && (
                                    <span className="text-xs text-gray-400 dark:text-gray-500">·</span>
                                  )}
                                  {(event.place_name || event.poi_name) && (
                                    <span className="text-sm font-semibold text-gray-600 dark:text-gray-300 truncate">{event.place_name || event.poi_name}</span>
                                  )}
                                  {event.poi_rating && event.poi_rating > 0 && (
                                    <span className="ml-auto flex items-center gap-0.5 text-xs text-yellow-500 shrink-0">
                                      <Star size={11} fill="currentColor" />
                                      {event.poi_rating}
                                    </span>
                                  )}
                                </div>
                                <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                                  {event.description}
                                </p>
                                {event.user_note && (
                                  <p className="text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded mt-1">
                                    📝 {event.user_note}
                                  </p>
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
                )}
              </div>
            )}
            
            {/* 기존 항공권/숙소 탭들... */}
            {activeTab === 'flights' && (
              <div className="space-y-6 animate-in fade-in">
                {tripPlan.flights && tripPlan.flights.length > 0 ? (
                  <div className="bg-white dark:bg-gray-900 rounded-2xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700">
                    <div className="p-8">
                      <div className="flex items-center gap-4 mb-6">
                        <div className="w-14 h-14 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
                          <Plane size={28} />
                        </div>
                        <div>
                          <h4 className="text-2xl font-bold text-gray-900 dark:text-white">{bestFlight.airline || '항공편 정보'}</h4>
                          <p className="text-gray-500 dark:text-gray-400 font-medium">{bestFlight.origin} → {bestFlight.destination}</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        <div className="bg-blue-50 p-4 rounded-xl">
                          <div className="flex items-center gap-2 mb-3">
                            <Plane size={16} className="text-blue-600" />
                            <span className="font-bold text-blue-900">출국</span>
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between items-center">
                              <div>
                                <div className="text-xs text-gray-600 dark:text-gray-400">출발</div>
                                <div className="text-lg font-bold text-gray-900 dark:text-white dark:text-white">{formatTime(bestFlight.outbound_departure_time)}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">{formatDate(bestFlight.outbound_departure_time)}</div>
                              </div>
                              <ArrowRight size={20} className="text-gray-400" />
                              <div className="text-right">
                                <div className="text-xs text-gray-600 dark:text-gray-400">도착</div>
                                <div className="text-lg font-bold text-gray-900 dark:text-white dark:text-white">{formatTime(bestFlight.outbound_arrival_time)}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">{formatDate(bestFlight.outbound_arrival_time)}</div>
                              </div>
                            </div>
                          </div>
                        </div>

                        {bestFlight.inbound_departure_time && (
                          <div className="bg-green-50 p-4 rounded-xl">
                            <div className="flex items-center gap-2 mb-3">
                              <Plane size={16} className="text-green-600 transform rotate-180" />
                              <span className="font-bold text-green-900">입국</span>
                            </div>
                            <div className="space-y-2">
                              <div className="flex justify-between items-center">
                                <div>
                                  <div className="text-xs text-gray-600 dark:text-gray-400">출발</div>
                                  <div className="text-lg font-bold text-gray-900 dark:text-white dark:text-white">{formatTime(bestFlight.inbound_departure_time)}</div>
                                  <div className="text-xs text-gray-500 dark:text-gray-400">{formatDate(bestFlight.inbound_departure_time)}</div>
                                </div>
                                <ArrowRight size={20} className="text-gray-400" />
                                <div className="text-right">
                                  <div className="text-xs text-gray-600 dark:text-gray-400">도착</div>
                                  <div className="text-lg font-bold text-gray-900 dark:text-white dark:text-white">{formatTime(bestFlight.inbound_arrival_time)}</div>
                                  <div className="text-xs text-gray-500 dark:text-gray-400">{formatDate(bestFlight.inbound_arrival_time)}</div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center justify-between pt-6 border-t border-gray-100 dark:border-gray-700">
                        <div>
                          <p className="text-xs text-gray-400 dark:text-gray-500 mb-1">예상 가격 (1인, 왕복)</p>
                          <p className="text-3xl font-extrabold text-blue-600 dark:text-blue-400">
                            {(bestFlight.price_krw || bestFlight.price || 0).toLocaleString()}
                            <span className="text-lg font-medium text-gray-500 dark:text-gray-400 ml-1">원</span>
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
            
            {activeTab === 'hotels' && (
              <div className="space-y-6 animate-in fade-in">
                {tripPlan.hotels && tripPlan.hotels.length > 0 ? (
                  <div className="bg-white dark:bg-gray-900 rounded-2xl overflow-hidden shadow-md border border-gray-200 dark:border-gray-700">
                    <div className="flex flex-col md:flex-row h-full">
                      <div className="relative md:w-2/5 h-64 md:h-auto overflow-hidden">
                        <img src="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80" alt={bestHotel.name} className="absolute inset-0 w-full h-full object-cover" />
                        <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur px-3 py-1.5 rounded-lg text-sm font-bold text-yellow-600 flex items-center gap-1">
                          <Star size={16} fill="currentColor" /> {bestHotel.rating || 0}
                        </div>
                      </div>
                      <div className="p-8 flex-1 flex flex-col justify-center">
                        <div className="mb-6">
                          <h4 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{bestHotel.name || '숙소 정보'}</h4>
                          <p className="text-gray-500 flex items-center gap-1.5">
                            <MapPin size={16} /> {bestHotel.location || '위치 미정'}
                          </p>
                        </div>
                        <div className="flex items-center justify-between pt-6 border-t border-gray-100 dark:border-gray-700">
                          <div>
                            <p className="text-xs text-gray-400 dark:text-gray-500 mb-1">1박 기준 (세금 포함)</p>
                            <p className="text-3xl font-extrabold text-blue-600 dark:text-blue-400">
                              {(bestHotel.price || 0).toLocaleString()}
                              <span className="text-lg font-medium text-gray-500 dark:text-gray-400 ml-1">원</span>
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
          className="bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-all"
        >
          목록으로
        </button>
        <button 
          onClick={() => navigate('/planner')} 
          className="bg-gray-900 dark:bg-white text-white dark:text-gray-900 px-8 py-4 rounded-xl font-bold text-lg shadow-lg hover:bg-gray-800 dark:hover:bg-gray-200 transition-all"
        >
          새 여행 계획하기
        </button>
      </div>
    </div>
  );
}