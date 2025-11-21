import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, Settings, LogOut, Plane, ChevronRight, MapPin, Calendar, Mail 
} from 'lucide-react';

// 💡 도시별 이미지 매핑 함수 (공통 유틸로 분리하면 더 좋음)
const getCityImage = (destination) => {
  const keyword = destination.split('/')[0].trim();
  
  const images = {
    '오사카': 'https://images.unsplash.com/photo-1590559399607-57523cd47a61?w=800&q=80',
    '도쿄': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80',
    '다낭': 'https://images.unsplash.com/photo-1559592413-7cec430aaec3?w=800&q=80',
    '제주': 'https://images.unsplash.com/photo-1548115184-bc6544d06a58?w=800&q=80',
    '파리': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80',
    '뉴욕': 'https://images.unsplash.com/photo-1496442226666-8d4a0e2907eb?w=800&q=80',
  };

  return images[keyword] || 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80';
};

export default function MyPage() {
  const navigate = useNavigate();

  const user = {
    username: "여행자123",
    email: "traveler@example.com",
    joinDate: "2025.01.15",
    tripCount: 3
  };

  const recentTrip = {
    destination: "오사카/간사이",
    date: "2025.10.23 - 10.26"
  };

  const handleLogout = () => {
    alert("로그아웃 되었습니다.");
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">

      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">마이페이지</h1>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-6 flex items-center gap-5">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-md">
            {user.username[0]}
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              {user.username}
              <span className="text-xs font-normal text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100">
                여행 {user.tripCount}회
              </span>
            </h2>
            <div className="flex items-center gap-1 text-gray-500 text-sm mt-1">
              <Mail size={14} /> {user.email}
            </div>
            <p className="text-xs text-gray-400 mt-2">가입일: {user.joinDate}</p>
          </div>
          <button 
            onClick={() => navigate('/mypage/edit')}
            className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            정보 수정
          </button>
        </div>

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
            <p className="text-sm text-gray-500">저장된 {user.tripCount}개의 여행 계획 보기</p>
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

        <h3 className="text-lg font-bold mb-3">최근 여행 계획</h3>
        <div 
          onClick={() => navigate('/saved')}
          className="bg-white rounded-xl overflow-hidden border border-gray-100 shadow-sm hover:shadow-md cursor-pointer flex items-center h-24 transition-all"
        >
          {/* 💡 여기서 getCityImage 함수 사용 */}
          <img src={getCityImage(recentTrip.destination)} alt="trip" className="w-24 h-full object-cover" />
          <div className="px-5 py-3 flex-1">
            <h4 className="font-bold text-gray-800 mb-1">{recentTrip.destination} 여행</h4>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Calendar size={14} /> {recentTrip.date}
            </div>
          </div>
          <div className="px-5 text-gray-400">
            <ChevronRight />
          </div>
        </div>

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