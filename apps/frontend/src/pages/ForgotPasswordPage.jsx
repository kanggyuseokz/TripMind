import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, CheckCircle, Copy, KeyRound } from 'lucide-react';

// 💡 백엔드 API 주소 (포트 8080)
const API_BASE_URL = "http://127.0.0.1:8080/api/auth";

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  
  // 임시 비밀번호 상태
  const [tempPassword, setTempPassword] = useState(''); 
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setTempPassword('');

    if (!email || !email.includes('@')) {
      setError('올바른 이메일 주소를 입력해주세요.');
      setLoading(false);
      return;
    }

    try {
        // 백엔드에 요청
        const response = await fetch(`${API_BASE_URL}/forgot-password`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || "요청 실패");
        }
        
        // 성공 시 임시 비밀번호 저장
        setTempPassword(data.temp_password);

    } catch (err) {
        setError(err.message);
    } finally {
        setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(tempPassword);
    alert("비밀번호가 복사되었습니다.");
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 relative font-sans text-gray-900">
      
      <button 
        onClick={() => navigate('/login')} 
        className="absolute top-6 left-6 flex items-center gap-2 text-gray-500 hover:text-black transition-colors font-medium"
      >
        <ArrowLeft size={20} /> 로그인으로 돌아가기
      </button>

      <div className="w-full max-w-md p-8 sm:p-10 bg-white rounded-xl shadow-2xl border border-gray-100">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">비밀번호 찾기</h1>
          <p className="text-gray-500 text-sm mt-2">
            가입하신 이메일을 입력하시면<br/>
            임시 비밀번호를 발급해 드립니다.
          </p>
        </div>

        {tempPassword ? (
          // [결과 화면] 임시 비밀번호 표시
          <div className="text-center animate-in fade-in zoom-in-95 duration-300">
            <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <KeyRound size={32} />
            </div>
            <h3 className="text-lg font-bold text-gray-800 mb-2">임시 비밀번호 발급 완료</h3>
            <p className="text-gray-600 text-sm mb-4">
              아래 비밀번호로 로그인 후 변경해주세요.
            </p>
            
            <div className="bg-gray-100 p-4 rounded-lg border border-gray-200 flex items-center justify-between mb-6">
              <span className="font-mono text-lg font-bold text-gray-800 tracking-wider">{tempPassword}</span>
              <button onClick={copyToClipboard} className="text-gray-500 hover:text-blue-600 p-2">
                <Copy size={20} />
              </button>
            </div>

            <button 
              onClick={() => navigate('/login')}
              className="w-full bg-black text-white py-3 rounded-lg font-bold hover:bg-gray-800 transition-colors"
            >
              로그인 하러 가기
            </button>
          </div>
        ) : (
          // [입력 화면] 이메일 폼
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">이메일 주소</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                  <Mail size={20} />
                </span>
                <input 
                  id="email"
                  type="email" 
                  required 
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all" 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  placeholder="email@example.com"
                />
              </div>
            </div>

            {error && <div className="text-red-600 text-sm text-center font-medium">{error}</div>}
            
            <button 
              type="submit" 
              disabled={loading} 
              className="w-full bg-blue-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:bg-blue-700 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="animate-spin" size={20}/>
                  발급 중...
                </span>
              ) : '임시 비밀번호 받기'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

function Loader2({ className, size }) {
    return (
        <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
        </svg>
    )
}