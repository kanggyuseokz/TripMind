// apps/frontend/src/pages/SavedTripsPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, Calendar, MapPin, ArrowRight, Trash2, Loader2 } from 'lucide-react';
import { useToast } from '../components/Toast';

const API_BASE_URL = "http://127.0.0.1:8080/api/trip";

// 도시별 이미지 매핑 (한국어·영어 키워드 → Unsplash 사진)
const CITY_IMAGES = [
  // 일본
  { keys: ['도쿄', 'tokyo'],        url: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80' },
  { keys: ['오사카', 'osaka', 'kix'], url: 'https://images.unsplash.com/photo-1590559399607-57523cd47a61?w=800&q=80' },
  { keys: ['후쿠오카', 'fukuoka'],   url: 'https://images.unsplash.com/photo-1601823984263-6936e89c9ca9?w=800&q=80' },
  { keys: ['삿포로', 'sapporo'],     url: 'https://images.unsplash.com/photo-1579401772658-2029589d980f?w=800&q=80' },
  { keys: ['오키나와', 'okinawa'],   url: 'https://images.unsplash.com/photo-1590077428593-a55bb07c4665?w=800&q=80' },
  { keys: ['교토', 'kyoto'],         url: 'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800&q=80' },
  { keys: ['나고야', 'nagoya'],      url: 'https://images.unsplash.com/photo-1580789958947-7da6a0551440?w=800&q=80' },
  // 한국
  { keys: ['서울', 'seoul'],         url: 'https://images.unsplash.com/photo-1517154421773-0529f29ea451?w=800&q=80' },
  { keys: ['부산', 'busan'],         url: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80' },
  { keys: ['제주', 'jeju'],          url: 'https://images.unsplash.com/photo-1548115184-bc6544d06a58?w=800&q=80' },
  // 동남아
  { keys: ['다낭', 'da nang', 'danang'], url: 'https://images.unsplash.com/photo-1559592413-7cec430aaec3?w=800&q=80' },
  { keys: ['방콕', 'bangkok'],       url: 'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800&q=80' },
  { keys: ['발리', 'bali'],          url: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80' },
  { keys: ['싱가포르', 'singapore'], url: 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&q=80' },
  { keys: ['세부', 'cebu'],          url: 'https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?w=800&q=80' },
  { keys: ['하노이', 'hanoi'],       url: 'https://images.unsplash.com/photo-1509030450996-dd1a26dda07a?w=800&q=80' },
  { keys: ['호치민', 'ho chi minh'], url: 'https://images.unsplash.com/photo-1583417267826-aebc4d1542e1?w=800&q=80' },
  { keys: ['쿠알라룸푸르', 'kuala lumpur', 'kl'], url: 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=800&q=80' },
  // 유럽
  { keys: ['파리', 'paris', 'charles de gaulle', 'cdg'], url: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80' },
  { keys: ['런던', 'london', 'heathrow', 'lhr'],         url: 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&q=80' },
  { keys: ['로마', 'rome'],          url: 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800&q=80' },
  { keys: ['바르셀로나', 'barcelona'], url: 'https://images.unsplash.com/photo-1523531294919-4bcd7c65e216?w=800&q=80' },
  { keys: ['암스테르담', 'amsterdam'], url: 'https://images.unsplash.com/photo-1534351590666-13e3e96b5702?w=800&q=80' },
  { keys: ['프라하', 'prague'],      url: 'https://images.unsplash.com/photo-1541849546-216549ae216d?w=800&q=80' },
  { keys: ['빈', 'vienna'],          url: 'https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=800&q=80' },
  { keys: ['취리히', 'zurich'],      url: 'https://images.unsplash.com/photo-1515488764276-beab7607c1e6?w=800&q=80' },
  // 미주
  { keys: ['뉴욕', 'new york', 'jfk', 'lga'], url: 'https://images.unsplash.com/photo-1496442226666-8d4a0e2907eb?w=800&q=80' },
  { keys: ['로스앤젤레스', 'los angeles', 'la', 'lax'], url: 'https://images.unsplash.com/photo-1544413660-299165566b1d?w=800&q=80' },
  { keys: ['하와이', 'hawaii', 'honolulu'], url: 'https://images.unsplash.com/photo-1507876466758-0f33219249fc?w=800&q=80' },
  { keys: ['라스베이거스', 'las vegas'],    url: 'https://images.unsplash.com/photo-1581351721010-8cf859cb14a4?w=800&q=80' },
  // 기타
  { keys: ['두바이', 'dubai'],       url: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80' },
  { keys: ['시드니', 'sydney'],      url: 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&q=80' },
];

const getCityImage = (destination) => {
  const DEFAULT = 'https://images.unsplash.com/photo-1488085061387-422e29b40080?w=800&q=80';
  if (!destination) return DEFAULT;

  const lower = destination.toLowerCase();
  const match = CITY_IMAGES.find(({ keys }) => keys.some(k => lower.includes(k)));
  return match ? match.url : DEFAULT;
};

// ✅ 날짜 차이 계산 함수 (개선)
const calculateDuration = (startDate, endDate) => {
  if (!startDate || !endDate) return "기간 미정";
  
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  if (isNaN(start.getTime()) || isNaN(end.getTime())) return "기간 미정";
  
  // 일수 차이 계산 (박 수)
  const diffTime = Math.abs(end - start);
  const nights = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  const days = nights + 1;
  
  return `${nights}박 ${days}일`;
};

// 날짜 관련
const formatTripDates = (startDate, endDate) => {
  if (!startDate || !endDate) return '날짜 미정';
  
  try {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // 기간 계산
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const nights = diffDays;
    const days = nights + 1;
    
    // 날짜 포맷팅
    const formatDate = (date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}년 ${month}월 ${day}일`;
    };
    
    return `${formatDate(start)} ~ ${formatDate(end)} (${nights}박 ${days}일)`;
  } catch (error) {
    return '날짜 미정';
  }
};

export default function SavedTripsPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const [savedTrips, setSavedTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  useEffect(() => {
    fetchTrips();
  }, []);

  // ✅ 저장된 여행 목록 불러오기 (에러 핸들링 개선)
  const fetchTrips = async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);
      setError(''); // 이전 에러 초기화
      
      const response = await fetch(`${API_BASE_URL}/saved`, {
        method: 'GET', 
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      // ✅ 401 에러 시 자동 로그아웃
      if (response.status === 401 || response.status === 422) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
        return;
      }

      if (!response.ok) {
        throw new Error(`데이터 로딩 실패 (${response.status})`);
      }

      const data = await response.json();
      setSavedTrips(Array.isArray(data) ? data : []);
      
    } catch (err) {
      console.error('❌ 여행 목록 로딩 실패:', err);
      setError(err.message || '데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, tripId) => {
    e.stopPropagation();
    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`${API_BASE_URL}/saved/${tripId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
        return;
      }

      if (response.ok) {
        setSavedTrips(prev => prev.filter(trip => trip.id !== tripId));
        setConfirmDeleteId(null);
        toast('여행 계획이 삭제되었습니다.', 'success');
      } else {
        const errorData = await response.json().catch(() => ({}));
        toast(errorData.message || '삭제에 실패했습니다.', 'error');
      }
    } catch (err) {
      console.error('❌ 삭제 실패:', err);
      toast('오류가 발생했습니다. 다시 시도해주세요.', 'error');
    }
  };

  // ✅ 카드 클릭 시 상세 페이지로 이동
  const handleCardClick = (trip) => {
    navigate(`/trip/${trip.id}`);
  };

  // 로딩 상태
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="animate-spin text-blue-600 mx-auto mb-4" size={48} />
          <p className="text-gray-500">여행 목록을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 font-sans text-gray-900 dark:text-gray-100">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* 헤더 */}
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">나의 여행 보관함</h1>
            <p className="text-gray-500 dark:text-gray-400 mt-2">저장된 여행 계획을 확인하고 관리해보세요.</p>
          </div>
          <button 
            onClick={() => navigate('/planner')} 
            className="bg-black dark:bg-white text-white dark:text-gray-900 px-5 py-2.5 rounded-lg font-semibold text-sm hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors shadow-sm"
          >
            + 새 여행 만들기
          </button>
        </div>

        {/* ✅ 에러 메시지 (개선) */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center gap-2">
            <span className="font-semibold">⚠️</span>
            <span>{error}</span>
            <button 
              onClick={fetchTrips}
              className="ml-auto text-sm underline hover:no-underline"
            >
              다시 시도
            </button>
          </div>
        )}

        {/* 여행 카드 그리드 */}
        {savedTrips.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedTrips.map((trip) => {
              const durationText = calculateDuration(trip.start_date, trip.end_date);

              return (
                <div 
                  key={trip.id} 
                  onClick={() => handleCardClick(trip)} 
                  className="bg-white dark:bg-gray-800 rounded-2xl overflow-hidden shadow-sm hover:shadow-xl border border-gray-100 dark:border-gray-700 transition-all duration-300 cursor-pointer group relative"
                >
                  {/* 이미지 영역 */}
                  <div className="h-48 overflow-hidden relative">
                    <img 
                      src={getCityImage(trip.destination)} 
                      alt={trip.destination} 
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-60"></div>
                    <div className="absolute bottom-4 left-4 text-white">
                      <p className="text-xs font-medium opacity-90 mb-1 flex items-center gap-1">
                        <MapPin size={12} /> {trip.destination}
                      </p>
                      <h3 className="text-xl font-bold truncate pr-4">{trip.trip_summary}</h3>
                    </div>
                  </div>
                  
                  
                  {/* 정보 영역 */}
                  <div className="p-5">
                    <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
                      <div className="flex items-center gap-1.5">
                        <Calendar size={16} className="text-blue-500" />
                        <span>{formatTripDates(trip.start_date, trip.end_date)}</span>
                      </div>
                    </div>
                    
                    {/* 하단 액션 */}
                    <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-700">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        총 비용 <span className="text-blue-600 font-bold">{(trip.total_cost || 0).toLocaleString()}원</span>
                      </div>
                      <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
                        {confirmDeleteId === trip.id ? (
                          <>
                            <span className="text-xs text-red-600 font-medium">삭제할까요?</span>
                            <button
                              onClick={(e) => handleDelete(e, trip.id)}
                              className="bg-red-500 text-white px-2.5 py-1 rounded-lg text-xs font-bold hover:bg-red-600 transition-colors"
                            >
                              삭제
                            </button>
                            <button
                              onClick={() => setConfirmDeleteId(null)}
                              className="bg-gray-200 text-gray-600 px-2.5 py-1 rounded-lg text-xs font-bold hover:bg-gray-300 transition-colors"
                            >
                              취소
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              onClick={() => setConfirmDeleteId(trip.id)}
                              className="text-gray-400 hover:text-red-500 transition-colors p-1"
                              title="삭제"
                            >
                              <Trash2 size={18} />
                            </button>
                            <div className="bg-gray-50 dark:bg-gray-700 p-2 rounded-full group-hover:bg-blue-50 dark:group-hover:bg-blue-900/30 transition-colors">
                              <ArrowRight size={18} className="text-gray-400 group-hover:text-blue-600" />
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          // 빈 상태
          <div className="text-center py-20 bg-white dark:bg-gray-800 rounded-2xl border border-dashed border-gray-300 dark:border-gray-600">
            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-400 dark:text-gray-500">
              <Plane size={32} />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">저장된 여행이 없습니다</h3>
            <p className="text-gray-500 dark:text-gray-400 mt-1 mb-6">새로운 여행 계획을 만들어보세요!</p>
            <button 
              onClick={() => navigate('/planner')} 
              className="text-blue-600 font-semibold hover:underline"
            >
              여행 계획하러 가기
            </button>
          </div>
        )}
      </main>
    </div>
  );
}