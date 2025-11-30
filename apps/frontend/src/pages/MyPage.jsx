// apps/frontend/src/pages/MyPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Settings, LogOut, Plane, ChevronRight, MapPin, Calendar, Mail, Loader2 } from 'lucide-react';
import ProfileImage from '../components/ProfileImage';

const API_BASE_URL = "http://127.0.0.1:8080/api/trip";
const AUTH_API_URL = "http://127.0.0.1:8080/api/auth";

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

export default function MyPage() {
  const navigate = useNavigate();
  
  const [user, setUser] = useState(null);
  const [recentTrip, setRecentTrip] = useState(null);
  const [tripCount, setTripCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    fetchUserProfile(token);
    fetchUserTrips(token);
  }, [navigate]);

  const fetchUserProfile = async (token) => {
    try {
      const response = await fetch(`${AUTH_API_URL}/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const profileData = await response.json();
        setUser(profileData);
        localStorage.setItem('user', JSON.stringify(profileData));
      } else if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
      }
    } catch (error) {
      console.error("Failed to fetch profile:", error);
      
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser));
        } catch (e) {
          console.error("User parse error", e);
        }
      }
    }
  };

  const fetchUserTrips = async (token) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/saved`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const trips = await response.json();
        if (Array.isArray(trips)) {
          setTripCount(trips.length);
          if (trips.length > 0) {
            setRecentTrip(trips[0]);
          }
        }
      }
    } catch (error) {
      console.error("Failed to fetch trips:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    alert("로그아웃 되었습니다.");
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="animate-spin text-blue-600" size={32} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">마이페이지</h1>
        
        {/* ✅ ProfileImage 컴포넌트 사용 */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-6 flex items-center gap-5">
          <ProfileImage 
            imageUrl={user?.profile_image} 
            username={user?.username}
            size="lg"
            className="shadow-md"
          />

          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              {user?.username || '여행자'}님
              <span className="text-xs font-normal text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100">
                여행 {tripCount}회
              </span>
            </h2>
            <div className="flex items-center gap-1 text-gray-500 text-sm mt-1">
              <Mail size={14} /> {user?.email || '이메일 없음'}
            </div>
            <p className="text-xs text-gray-400 mt-2">TripMind 회원</p>
          </div>
          <button onClick={() => navigate('/mypage/edit')} className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg font-medium transition-colors">
            정보 수정
          </button>
        </div>

        {/* 메뉴 그리드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div 
            onClick={() => navigate('/saved')} 
            className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-md hover:border-blue-200 cursor-pointer transition-all group"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg group-hover:bg-blue-600 group-hover:text-white transition-colors">
                <Plane size={24} />
              </div>
              <ChevronRight className="text-gray-300 group-hover:text-blue-500" />
            </div>
            <h3 className="font-bold text-lg mb-1">나의 여행 보관함</h3>
            <p className="text-sm text-gray-500">저장된 {tripCount}개의 여행 계획 보기</p>
          </div>
          
          <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-md cursor-pointer transition-all">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 bg-gray-50 text-gray-600 rounded-lg">
                <Settings size={24} />
              </div>
            </div>
            <h3 className="font-bold text-lg mb-1">앱 설정</h3>
            <p className="text-sm text-gray-500">알림 및 환경설정</p>
          </div>
        </div>

        {/* 최근 여행 계획 섹션 */}
        <h3 className="text-lg font-bold mb-3">최근 여행 계획</h3>
        {recentTrip ? (
          <div 
            onClick={() => navigate('/saved')} 
            className="bg-white rounded-xl overflow-hidden border border-gray-100 shadow-sm hover:shadow-md cursor-pointer flex items-center h-24 transition-all"
          >
            <img 
              src={getCityImage(recentTrip.destination)} 
              alt="trip" 
              className="w-24 h-full object-cover" 
            />
            <div className="px-5 py-3 flex-1">
              <h4 className="font-bold text-gray-800 mb-1">{recentTrip.trip_summary}</h4>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Calendar size={14} /> {recentTrip.start_date || '날짜 미정'}
              </div>
            </div>
            <div className="px-5 text-gray-400">
              <ChevronRight />
            </div>
          </div>
        ) : (
          <div className="text-center py-8 bg-gray-50 rounded-xl border border-dashed border-gray-300 text-gray-400 text-sm">
            아직 저장된 여행 계획이 없습니다.
          </div>
        )}

        <div className="mt-10 text-center">
          <button 
            onClick={handleLogout} 
            className="text-gray-400 hover:text-red-500 text-sm font-medium flex items-center justify-center gap-2 mx-auto transition-colors"
          >
            <LogOut size={16} /> 로그아웃
          </button>
        </div>
      </main>
    </div>
  );
}