import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Layout from './components/Layout'; // 👈 추가
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import PlannerPage from './pages/PlannerPage';
import ResultPage from './pages/ResultPage';
import SavedTripsPage from './pages/SavedTripsPage';
import MyPage from './pages/MyPage';
import EditProfilePage from './pages/EditProfilePage';

export default function App() {
  return (
    <Router>
      <Routes>
        {/* 모든 페이지를 Layout으로 감쌉니다 */}
        <Route element={<Layout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/planner" element={<PlannerPage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/saved" element={<SavedTripsPage />} />
          <Route path="/mypage" element={<MyPage />} />
          <Route path="/mypage/edit" element={<EditProfilePage />} />
        </Route>
      </Routes>
    </Router>
  );
}