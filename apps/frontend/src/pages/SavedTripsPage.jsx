// apps/frontend/src/pages/SavedTripsPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, Calendar, MapPin, ArrowRight, Trash2, Loader2 } from 'lucide-react';

const API_BASE_URL = "http://127.0.0.1:8080/api/trip";

// 도시별 이미지 매핑
const getCityImage = (destination) => {
  if (!destination) return 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80';
  
  const keyword = destination.split('/')[0].split('(')[0].trim();
  const images = { 
    '오사카': 'https://images.unsplash.com/photo-1590559399607-57523cd47a61?w=800&q=80', 
    '도쿄': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80', 
    '다낭': 'https://images.unsplash.com/photo-1559592413-7cec430aaec3?w=800&q=80', 
    '제주': 'https://images.unsplash.com/photo-1548115184-bc6544d06a58?w=800&q=80', 
    '파리': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80', 
    '뉴욕': 'https://images.unsplash.com/photo-1496442226666-8d4a0e2907eb?w=800&q=80', 
    '방콕': 'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800&q=80', 
    '런던': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&q=80',
    '후쿠오카': 'https://images.unsplash.com/photo-1624329243765-b1e102293478?w=800&q=80',
    '삿포로': 'https://images.unsplash.com/photo-1579401772658-2029589d980f?w=800&q=80',
    '서울': 'https://images.unsplash.com/photo-1517154421773-0529f29ea451?w=800&q=80'
  };
  
  const foundKey = Object.keys(images).find(key => keyword.includes(key));
  return foundKey ? images[foundKey] : 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80';
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

export default function SavedTripsPage() {
  const navigate = useNavigate();
  const [savedTrips, setSavedTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTrips();
  }, []);

  // ✅ 저장된 여행 목록 불러오기 (에러 핸들링 개선)
  const fetchTrips = async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      alert("로그인이 필요합니다.");
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
        alert("로그인 세션이 만료되었습니다. 다시 로그인해주세요.");
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

  // ✅ 여행 삭제 (에러 핸들링 개선)
  const handleDelete = async (e, tripId) => {
    e.stopPropagation(); 
    
    if (!window.confirm("정말로 이 여행 계획을 삭제하시겠습니까?")) return;

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
        alert("로그인 세션이 만료되었습니다.");
        navigate('/login');
        return;
      }

      if (response.ok) {
        setSavedTrips(prev => prev.filter(trip => trip.id !== tripId));
        alert("여행 계획이 삭제되었습니다.");
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(errorData.message || "삭제에 실패했습니다.");
      }
    } catch (err) {
      console.error('❌ 삭제 실패:', err);
      alert("오류가 발생했습니다. 다시 시도해주세요.");
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
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* 헤더 */}
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">나의 여행 보관함</h1>
            <p className="text-gray-500 mt-2">저장된 여행 계획을 확인하고 관리해보세요.</p>
          </div>
          <button 
            onClick={() => navigate('/planner')} 
            className="bg-black text-white px-5 py-2.5 rounded-lg font-semibold text-sm hover:bg-gray-800 transition-colors shadow-sm"
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
                  className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl border border-gray-100 transition-all duration-300 cursor-pointer group relative"
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
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                      <div className="flex items-center gap-1.5">
                        <Calendar size={16} className="text-blue-500" />
                        <span>{trip.start_date || '날짜 미정'} ({durationText})</span>
                      </div>
                    </div>
                    
                    {/* 하단 액션 */}
                    <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                      <div className="text-sm font-medium text-gray-900">
                        총 비용 <span className="text-blue-600 font-bold">{(trip.total_cost || 0).toLocaleString()}원</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <button 
                          onClick={(e) => handleDelete(e, trip.id)} 
                          className="text-gray-400 hover:text-red-500 transition-colors p-1"
                          title="삭제"
                        >
                          <Trash2 size={18} />
                        </button>
                        <div className="bg-gray-50 p-2 rounded-full group-hover:bg-blue-50 transition-colors">
                          <ArrowRight size={18} className="text-gray-400 group-hover:text-blue-600" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          // 빈 상태
          <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-300">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-400">
              <Plane size={32} />
            </div>
            <h3 className="text-lg font-medium text-gray-900">저장된 여행이 없습니다</h3>
            <p className="text-gray-500 mt-1 mb-6">새로운 여행 계획을 만들어보세요!</p>
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