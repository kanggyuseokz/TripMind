import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, Settings, LogOut, Plane, ChevronRight, MapPin, Calendar, Mail 
} from 'lucide-react';

export default function MyPage() {
  const navigate = useNavigate();

  // [Mock Data] 로그인된 사용자 정보 (나중에는 전역 상태나 API로 가져옴)
  const user = {
    username: "여행자123",
    email: "traveler@example.com",
    joinDate: "2025.01.15",
    tripCount: 3
  };

  // [Mock Data] 최근 본 여행 (예시)
  const recentTrip = {
    destination: "오사카/간사이",
    date: "2025.10.23 - 10.26",
    image: "https://images.unsplash.com/photo-1590559399607-57523cd47a61?w=800&q=80"
  };

  const handleLogout = () => {
    // 1. 토큰 삭제 (localStorage.removeItem('token'))
    // 2. 로그인 페이지로 이동
    alert("로그아웃 되었습니다.");
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
      {/* 상단 헤더 */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
            <Plane size={24} className="text-blue-600" strokeWidth={2.5} />
            <span className="text-xl font-bold tracking-tight">TripMind</span>
          </div>
          <button onClick={() => navigate('/')} className="text-sm font-medium text-gray-500 hover:text-gray-900">
            메인으로
          </button>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">마이페이지</h1>

        {/* 1. 프로필 카드 */}
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

        {/* 2. 메뉴 그리드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          {/* 보관함 바로가기 */}
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

          {/* 계정 설정 (더미) */}
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

        {/* 3. 최근 본 여행 (카드) */}
        <h3 className="text-lg font-bold mb-3">최근 여행 계획</h3>
        <div 
          onClick={() => navigate('/saved')}
          className="bg-white rounded-xl overflow-hidden border border-gray-100 shadow-sm hover:shadow-md cursor-pointer flex items-center h-24 transition-all"
        >
          <img src={recentTrip.image} alt="trip" className="w-24 h-full object-cover" />
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

        {/* 4. 로그아웃 버튼 */}
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