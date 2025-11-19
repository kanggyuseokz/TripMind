import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// 페이지 컴포넌트 불러오기
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import PlannerPage from './pages/PlannerPage';
import ResultPage from './pages/ResultPage'; // 👈 신규 페이지 추가
import SavedTripsPage from './pages/SavedTripPage';

export default function App() {
  return (
    <Router>
      <Routes>
        {/* 기본 경로 */}
        <Route path="/" element={<LandingPage />} />
        
        {/* 로그인 */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* 입력 폼 (Planner) */}
        <Route path="/planner" element={<PlannerPage />} />
        
        {/* 결과 화면 (Result) */}
        <Route path="/result" element={<ResultPage />} />

        <Route path="/saved" element={<SavedTripsPage />} />
      </Routes>
    </Router>
  );
}