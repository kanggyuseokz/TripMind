import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastProvider } from './components/Toast';

import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import PlannerPage from './pages/PlannerPage';
import ResultPage from './pages/ResultPage';
import SavedTripsPage from './pages/SavedTripsPage';
import MyPage from './pages/MyPage';
import EditProfilePage from './pages/EditProfilePage';
import ForgotPasswordPage from './pages/ForgotPasswordPage'; // 👈 추가
import ViewTripPage from './pages/ViewTripPage';

export default function App() {
  return (
    <ToastProvider>
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/planner" element={<PlannerPage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/saved" element={<SavedTripsPage />} />
          <Route path="/trip/:id" element={<ViewTripPage />} />
          <Route path="/mypage" element={<MyPage />} />
          <Route path="/mypage/edit" element={<EditProfilePage />} />
          
          {/* 비밀번호 찾기 라우트 추가 */}
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        </Route>
      </Routes>
    </Router>
    </ToastProvider>
  );
}