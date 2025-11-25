// apps/frontend/src/components/Sidebar.jsx
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, User, Map, PlusCircle, LogOut, LogIn, Smile } from 'lucide-react';

export default function Sidebar({ isOpen, onClose }) {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  // 💡 사용자 정보를 담을 상태 추가
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    if (isOpen) {
      // 1. 토큰 확인 (로그인 여부)
      const token = localStorage.getItem('token');
      setIsLoggedIn(!!token);

      // 2. 사용자 정보 가져오기 (로그인 시 저장해둔 정보)
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        try {
          // JSON 문자열을 객체로 변환하여 상태에 저장
          setUserInfo(JSON.parse(storedUser));
        } catch (e) {
          console.error("사용자 정보 파싱 오류:", e);
          setUserInfo(null);
        }
      }
    }
  }, [isOpen]);

  const handleNavigate = (path) => {
    navigate(path);
    onClose(); 
  };

  const handleLogout = () => {
    // 로그아웃 시 토큰과 사용자 정보 모두 삭제
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    setIsLoggedIn(false);
    setUserInfo(null);
    
    alert("로그아웃 되었습니다.");
    handleNavigate('/login');
  };

  const handleLogin = () => {
    handleNavigate('/login');
  }

  return (
    <>
      {/* 배경 오버레이 */}
      <div 
        className={`fixed inset-0 bg-black/50 z-40 transition-opacity duration-300 ${
          isOpen ? 'opacity-100 visible' : 'opacity-0 invisible pointer-events-none'
        }`}
        onClick={onClose}
      />

      {/* 사이드바 패널 */}
      <div 
        className={`fixed top-0 left-0 h-full w-80 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-5 flex justify-between items-center border-b border-gray-100">
          <h2 className="font-bold text-lg text-gray-800">메뉴</h2>
          <button onClick={onClose} className="p-2 text-gray-500 hover:bg-gray-100 rounded-full transition-colors">
            <X size={24} />
          </button>
        </div>

        <div className="p-4 space-y-2">
          {isLoggedIn ? (
            <>
              {/* 💡 사용자 프로필 (백엔드 데이터 연동됨) */}
              <div 
                onClick={() => handleNavigate('/mypage')}
                className="flex items-center gap-4 p-4 bg-blue-50 rounded-xl cursor-pointer hover:bg-blue-100 transition-colors mb-6"
              >
                <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-blue-600 font-bold shadow-sm text-lg">
                  {/* 이름의 첫 글자만 따서 프로필 아이콘으로 사용 (없으면 U) */}
                  {userInfo?.username ? userInfo.username.charAt(0).toUpperCase() : 'U'}
                </div>
                <div>
                  {/* 실제 사용자 이름과 이메일 표시 */}
                  <p className="font-bold text-gray-900">
                    {userInfo?.username || '여행자'}님
                  </p>
                  <p className="text-xs text-gray-500">
                    {userInfo?.email || 'traveler@example.com'}
                  </p>
                </div>
              </div>

              <button onClick={() => handleNavigate('/mypage')} className="flex items-center gap-3 w-full p-3 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors">
                <User size={20} /> 마이페이지
              </button>
              <button onClick={() => handleNavigate('/saved')} className="flex items-center gap-3 w-full p-3 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors">
                <Map size={20} /> 나의 여행 보관함
              </button>
              <button onClick={() => handleNavigate('/planner')} className="flex items-center gap-3 w-full p-3 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors">
                <PlusCircle size={20} /> 새 여행 만들기
              </button>
            </>
          ) : (
            <>
              <div className="flex flex-col items-center justify-center p-6 bg-gray-50 rounded-xl text-center mb-6 border border-gray-100">
                <div className="bg-white p-3 rounded-full mb-3 shadow-sm">
                  <Smile size={32} className="text-blue-500" />
                </div>
                <p className="text-gray-800 font-bold mb-1">로그인이 필요해요</p>
                <p className="text-gray-500 text-xs mb-4">나만의 여행 계획을 저장하고 관리해보세요.</p>
                <button 
                  onClick={handleLogin}
                  className="w-full bg-black text-white py-2.5 rounded-lg font-bold hover:bg-gray-800 transition-colors shadow-sm text-sm flex items-center justify-center gap-2"
                >
                  <LogIn size={16} /> 로그인 / 회원가입
                </button>
              </div>
          
            </>
          )}
        </div>

        {isLoggedIn && (
          <div className="absolute bottom-0 left-0 w-full p-4 border-t border-gray-100">
            <button 
              onClick={handleLogout}
              className="flex items-center gap-2 text-red-500 hover:bg-red-50 w-full p-3 rounded-lg font-medium transition-colors"
            >
              <LogOut size={20} /> 로그아웃
            </button>
          </div>
        )}
      </div>
    </>
  );
}