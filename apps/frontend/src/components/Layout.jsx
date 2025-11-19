import React from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Plane, ArrowLeft, ShoppingBag, X } from 'lucide-react';

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();

  // 결과 페이지인지 확인
  const isResultPage = location.pathname === '/result';

  // 헤더 우측 버튼 렌더링 로직
  const renderHeaderActions = () => {
    if (isResultPage) {
      return (
        <div className="flex items-center gap-3">
          {/* 👇 저장 버튼 (애니메이션 적용됨) */}
          <button 
            onClick={() => {
              alert("여행이 보관함에 저장되었습니다!");
              navigate('/saved');
            }}
            className="group flex items-center p-2 text-gray-500 hover:text-white hover:bg-black rounded-full transition-all duration-300 ease-in-out" 
            title="저장"
          >
            <ShoppingBag size={20} />
            <span className="max-w-0 overflow-hidden opacity-0 group-hover:max-w-xs group-hover:opacity-100 group-hover:ml-2 transition-all duration-300 ease-in-out whitespace-nowrap text-sm font-medium">
              저장하기
            </span>
          </button>

          {/* 사용자 아이콘 */}
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md">U</div>
          
          {/* 닫기 버튼 */}
          <button onClick={() => navigate('/planner')} className="p-2 text-gray-400 hover:text-gray-700 transition-colors">
            <X size={24} />
          </button>
        </div>
      );
    }
    
    // 기본 헤더 (메인으로 가기)
    return (
      <button onClick={() => navigate('/')} className="text-gray-500 hover:text-gray-900 flex items-center gap-1 text-sm font-medium">
        <ArrowLeft size={18} /> 메인으로
      </button>
    );
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 font-sans text-gray-900">
      {/* 고정 헤더 - 반투명 효과 제거 및 일반적인 흰색 배경 적용 */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
            <Plane size={24} className="text-blue-600" strokeWidth={2.5} />
            <span className="text-xl font-bold tracking-tight">TripMind</span>
          </div>
          
          {renderHeaderActions()}
        </div>
      </header>

      {/* 페이지 콘텐츠 */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}