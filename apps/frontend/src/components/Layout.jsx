// apps/frontend/src/components/Layout.jsx
import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useToast } from './Toast';

// 💡 백엔드 API 주소
const API_BASE_URL = "http://127.0.0.1:8080/api/trip";

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  
  const toast = useToast();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const isResultPage = location.pathname === '/result';
  const isLoginPage = location.pathname === '/login';

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, [location.pathname]);

  // 저장하기 로직 (Layout에서 관리)
  const handleSaveTrip = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      toast('로그인이 필요한 서비스입니다.', 'info');
      navigate('/login');
      return;
    }

    const tripData = window.currentTripData || location.state?.tripData;

    if (!tripData) {
      toast('저장할 여행 데이터가 없습니다.', 'error');
      return;
    }

    try {
      setIsSaving(true);
      
      const payload = {
        trip_summary: tripData.trip_summary || `${tripData.destination} 여행`,
        destination: tripData.destination,
        start_date: tripData.start_date || tripData.startDate,
        end_date: tripData.end_date || tripData.endDate,
        total_cost: tripData.total_cost || tripData.budget,
        head_count: tripData.party_size || tripData.head_count,
        schedule: tripData.schedule || [],
        flights: tripData.flights || [],
        hotels: tripData.hotels || [],
        raw_data: tripData.raw_data || {} 
      };

      const response = await fetch(`${API_BASE_URL}/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
          if (response.status === 422 || response.status === 401) {
              throw new Error("로그인 세션이 만료되었습니다. 다시 로그인해주세요.");
          }
          const errData = await response.json();
          throw new Error(errData.error || "저장에 실패했습니다.");
      }

      toast('여행이 보관함에 저장되었습니다!', 'success');
      navigate('/saved');

    } catch (error) {
      console.error(error);
      toast(error.message || '저장 중 오류가 발생했습니다.', 'error');
      if (error.message.includes("로그인")) {
          navigate('/login');
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 font-sans text-gray-900">
      {/* 💡 분리된 헤더 컴포넌트 사용 */}
      <Header 
        isLoginPage={isLoginPage}
        isLoggedIn={isLoggedIn}
        isResultPage={isResultPage}
        isSaving={isSaving}
        onOpenSidebar={() => setIsSidebarOpen(true)}
        onNavigate={navigate}
        onSaveTrip={handleSaveTrip}
      />

      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}