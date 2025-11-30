// src/pages/LoginPage.jsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

// --- 아이콘 컴포넌트 ---
const UserIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>;
const LockIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>;
const EmailIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>;
const GoogleIcon = () => (<svg className="w-5 h-5" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.0001 12.2272c0-.8182-.0727-1.6-.2045-2.3636h-9.6091v4.4545h5.4a4.622 4.622 0 0 1-1.9909 3.0364v2.8864h3.7091c2.1682-2.0091 3.4182-4.9455 3.4182-8.0136z"/><path fill="#34A853" d="M12.1865 22c3.2182 0 5.9273-1.0636 7.9-2.8864l-3.7091-2.8864c-1.0636.7182-2.4364 1.1455-3.9545 1.1455-3.0455 0-5.6182-2.0682-6.5455-4.8545H1.9274v2.9818C3.9001 20.109 7.8092 22 12.1865 22z"/><path fill="#FBBC05" d="M5.641 14.1545c-.2182-.7182-.3455-1.4636-.3455-2.2273s.1273-1.5091.3455-2.2273V6.7182H1.9274c-.7818 1.5636-1.2364 3.2909-1.2364 5.1091s.4545 3.5455 1.2364 5.1091l3.7136-2.9818z"/><path fill="#EA4335" d="M12.1865 5.5273c1.7545 0 3.3273.6091 4.5636 1.7818l3.2818-3.2818C18.1092 2.1545 15.4 1 12.1865 1c-4.3773 0-8.2864 2.8909-10.2591 6.7182l3.7136 2.9818c.9273-2.7864 3.5-4.8545 6.5455-4.8545z"/></svg>);
const NaverIcon = () => (<span className="w-5 h-5 flex items-center justify-center font-bold text-lg text-white">N</span>);

const SocialButton = ({ provider, icon, text, bgColor, textColor }) => (
  <button className={`flex items-center justify-center w-full py-3 px-4 rounded-lg shadow-sm transition-colors ${bgColor} ${textColor} font-semibold`} onClick={() => alert(`${provider} 로그인 (준비중)`)}>{icon} <span className="ml-3">{text}</span></button>
);

// 💡 백엔드 API 주소
const API_BASE_URL = "http://127.0.0.1:8080/api/auth";

// --- 로그인 폼 ---
const LoginForm = ({ setPage }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
        // 💡 백엔드 로그인 요청
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.message || "로그인 실패");
        }

        // ✅ JWT 토큰 저장 (핵심 부분)
        if (data.access_token) {
            localStorage.setItem('token', data.access_token);
            console.log('✅ 토큰 저장 완료:', data.access_token.substring(0, 20) + '...');
        } else {
            throw new Error('서버에서 토큰을 받지 못했습니다.');
        }

        // ✅ 사용자 정보 저장
        if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user));
            console.log('✅ 사용자 정보 저장:', data.user.username);
        }

        // 성공 메시지
        alert(`환영합니다, ${data.user?.username || '사용자'}님!`);
        
        // 메인 페이지로 이동
        navigate('/');

    } catch (err) {
        console.error('❌ 로그인 실패:', err);
        setError(err.message);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <h1 className="text-3xl font-bold text-center text-gray-900 mb-4">로그인</h1>
      <p className="text-gray-600 text-center mb-8">TripMind에 다시 오신 것을 환영합니다!</p>
      <form onSubmit={handleLogin} className="space-y-6">
        <div><label className="block text-sm font-medium text-gray-700 mb-2">이메일 주소</label><div className="relative"><span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"><EmailIcon /></span><input type="email" required className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email@example.com"/></div></div>
        <div><label className="block text-sm font-medium text-gray-700 mb-2">비밀번호</label><div className="relative"><span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"><LockIcon /></span><input type="password" required className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="비밀번호"/></div></div>
        {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}
        <div className="text-right"><button type="button" onClick={() => navigate('/forgot-password')} className="text-sm font-medium text-blue-600 hover:text-blue-500 hover:underline">비밀번호를 잊으셨나요?</button></div>
        <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:bg-blue-700 transition-all disabled:opacity-75">{loading ? '로그인 중...' : '로그인'}</button>
        <div className="relative my-6"><div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-300"></div></div><div className="relative flex justify-center text-sm"><span className="px-2 bg-white text-gray-500">또는</span></div></div>
        <div className="space-y-4"><SocialButton provider="google" icon={<GoogleIcon />} text="Google 계정으로 로그인" bgColor="bg-white border border-gray-300 hover:bg-gray-50" textColor="text-gray-700"/><SocialButton provider="naver" icon={<NaverIcon />} text="네이버 아이디로 로그인" bgColor="bg-[#03C75A] hover:bg-[#03b350]" textColor="text-white"/></div>
      </form>
      <p className="text-center text-sm text-gray-600 mt-8">계정이 없으신가요? <button onClick={() => setPage('register')} className="font-semibold text-blue-600 hover:text-blue-500">회원가입</button></p>
    </div>
  );
};

// --- 회원가입 폼 ---
const RegisterForm = ({ setPage }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    // 비밀번호 확인
    if (password !== passwordConfirm) { 
        setError('비밀번호가 일치하지 않습니다.'); 
        setLoading(false); 
        return; 
    }

    // 비밀번호 길이 확인
    if (password.length < 8) {
        setError('비밀번호는 최소 8자 이상이어야 합니다.');
        setLoading(false);
        return;
    }
    
    try {
        // 💡 백엔드 회원가입 요청
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.message || "회원가입 실패");
        }

        // 성공 시 로그인 페이지로 이동
        alert("회원가입 성공! 로그인해주세요.");
        setPage('login');

    } catch (err) {
        console.error('❌ 회원가입 실패:', err);
        setError(err.message);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <h1 className="text-3xl font-bold text-center text-gray-900 mb-4">회원가입</h1>
      <p className="text-gray-600 text-center mb-8">TripMind와 함께 여행을 계획해 보세요.</p>
      <form onSubmit={handleRegister} className="space-y-6">
        <div><label className="block text-sm font-medium text-gray-700 mb-2">사용자 이름</label><div className="relative"><span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"><UserIcon /></span><input type="text" required className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="이름을 입력하세요"/></div></div>
        <div><label className="block text-sm font-medium text-gray-700 mb-2">이메일 주소</label><div className="relative"><span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"><EmailIcon /></span><input type="email" required className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email@example.com"/></div></div>
        <div><label className="block text-sm font-medium text-gray-700 mb-2">비밀번호</label><div className="relative"><span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"><LockIcon /></span><input type="password" required className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="비밀번호 (8자 이상)"/></div></div>
        <div><label className="block text-sm font-medium text-gray-700 mb-2">비밀번호 확인</label><div className="relative"><span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"><LockIcon /></span><input type="password" required className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" value={passwordConfirm} onChange={(e) => setPasswordConfirm(e.target.value)} placeholder="비밀번호 다시 입력"/></div></div>
        {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}
        <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:bg-blue-700 transition-all disabled:opacity-75">{loading ? '계정 생성 중...' : '계정 생성하기'}</button>
      </form>
      <p className="text-center text-sm text-gray-600 mt-8">이미 계정이 있으신가요? <button onClick={() => setPage('login')} className="font-semibold text-blue-600 hover:text-blue-500">로그인</button></p>
    </div>
  );
};

export default function LoginPage() {
  const [page, setPage] = useState('login');
  const navigate = useNavigate();
  return (
    <div className="min-h-screen flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 relative">
      <button onClick={() => navigate('/')} className="absolute top-6 left-6 flex items-center gap-2 text-gray-500 hover:text-black transition-colors font-medium"><ArrowLeft size={20} /> 메인으로</button>
      <div className="mb-8"><a href="/" className="text-4xl font-extrabold font-inter text-gray-900">TripMind</a></div>
      <div className="w-full max-w-md p-8 sm:p-10 bg-white rounded-xl shadow-2xl overflow-hidden border border-gray-100">{page === 'login' ? <LoginForm setPage={setPage} /> : <RegisterForm setPage={setPage} />}</div>
    </div>
  );
}