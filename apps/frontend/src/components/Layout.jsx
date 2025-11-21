import React, { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Plane, ArrowLeft, ShoppingBag, Menu, User } from 'lucide-react';
import Sidebar from './Sidebar';

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const isResultPage = location.pathname === '/result';
  const isLoginPage = location.pathname === '/login';

  // 헤더 우측 버튼 (메뉴 버튼 제거됨)
  const renderHeaderActions = () => {
    if (isLoginPage) return null;

    return (
      <div className="flex items-center gap-3">
        {isResultPage && (
          <button 
            onClick={() => {
              alert("여행이 보관함에 저장되었습니다!");
              navigate('/saved');
            }}
            className="group flex items-center p-2 text-gray-500 hover:text-white hover:bg-black rounded-full transition-all duration-300 ease-in-out mr-2" 
            title="저장"
          >
            <ShoppingBag size={20} />
            <span className="max-w-0 overflow-hidden opacity-0 group-hover:max-w-xs group-hover:opacity-100 group-hover:ml-2 transition-all duration-300 ease-in-out whitespace-nowrap text-sm font-medium">
              저장하기
            </span>
          </button>
        )}

        <button 
          onClick={() => navigate('/mypage')}
          className="hidden md:flex items-center justify-center w-9 h-9 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-full transition-colors"
          title="마이페이지"
        >
          <User size={18} />
        </button>
      </div>
    );
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 font-sans text-gray-900">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* 💡 좌측: 메뉴 버튼 + 로고 */}
          <div className="flex items-center gap-4">
            {/* 메뉴 버튼: 로그인 페이지가 아닐 때만 표시 */}
            {!isLoginPage && (
              <button 
                onClick={() => setIsSidebarOpen(true)} 
                className="p-2 -ml-20 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors"
              >
                <Menu size={24} />
              </button>
            )}

            <div className="flex ml-3 items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
              <Plane size={24} className="text-blue-600" strokeWidth={2.5} />
              <span className="text-xl font-bold tracking-tight">TripMind</span>
            </div>
          </div>

          {/* 우측: 액션 버튼들 */}
          {renderHeaderActions()}
        </div>
      </header>

      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}