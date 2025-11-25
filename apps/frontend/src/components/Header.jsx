// apps/frontend/src/components/Header.jsx
import React from 'react';
import { Plane, ShoppingBag, Menu, User, Loader2 } from 'lucide-react';

export default function Header({ 
  isLoginPage, 
  isLoggedIn, 
  isResultPage, 
  isSaving, 
  onOpenSidebar, 
  onNavigate, 
  onSaveTrip 
}) {
  // 헤더 우측 버튼 렌더링 (로그인 여부에 따라 분기)
  const renderHeaderActions = () => {
    if (isLoginPage) return null;

    // 비로그인 상태일 때
    if (!isLoggedIn) {
      return (
        <button 
          onClick={() => onNavigate('/login')}
          className="bg-black text-white px-5 py-2 rounded-full text-sm font-bold hover:bg-gray-800 transition-colors"
        >
          로그인
        </button>
      );
    }

    // 로그인 상태일 때
    return (
      <div className="flex items-center gap-3">
        {isResultPage && (
          <button 
            onClick={onSaveTrip}
            disabled={isSaving}
            className="group flex items-center p-2 text-gray-500 hover:text-white hover:bg-black rounded-full transition-all duration-300 ease-in-out mr-2" 
            title="저장"
          >
            {isSaving ? <Loader2 size={20} className="animate-spin" /> : <ShoppingBag size={20} />}
            <span className="max-w-0 overflow-hidden opacity-0 group-hover:max-w-xs group-hover:opacity-100 group-hover:ml-2 transition-all duration-300 ease-in-out whitespace-nowrap text-sm font-medium">
              {isSaving ? '저장 중...' : '저장하기'}
            </span>
          </button>
        )}

        <button 
          onClick={() => onNavigate('/mypage')}
          className="hidden md:flex items-center justify-center w-9 h-9 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-full transition-colors"
          title="마이페이지"
        >
          <User size={18} />
        </button>
      </div>
    );
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="w-full px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* 좌측: 메뉴 버튼 + 로고 */}
        <div className="flex items-center gap-4">
          {!isLoginPage && (
            <button 
              onClick={onOpenSidebar} 
              className="p-2 -ml-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors"
            >
              <Menu size={24} />
            </button>
          )}

          <div className="flex ml-3 items-center gap-2 cursor-pointer" onClick={() => onNavigate('/')}>
            <Plane size={24} className="text-blue-600" strokeWidth={2.5} />
            <span className="text-xl font-bold tracking-tight">TripMind</span>
          </div>
        </div>

        {/* 우측: 액션 버튼들 */}
        {renderHeaderActions()}
      </div>
    </header>
  );
}