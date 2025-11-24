import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, CheckCircle } from 'lucide-react';

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSent, setIsSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // 이메일 유효성 검사
    if (!email || !email.includes('@')) {
      setError('올바른 이메일 주소를 입력해주세요.');
      setLoading(false);
      return;
    }

    // 백엔드 연동 시뮬레이션 (1.5초 후 성공 처리)
    setTimeout(() => {
      setLoading(false);
      setIsSent(true); // 전송 완료 상태로 변경
    }, 1500);
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 relative font-sans text-gray-900">
      
      {/* 상단 뒤로가기 버튼 */}
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
            가입하신 이메일 주소를 입력해 주세요.<br/>
            비밀번호 재설정 링크를 보내드립니다.
          </p>
        </div>

        {isSent ? (
          // 전송 완료 화면
          <div className="text-center animate-in fade-in zoom-in-95 duration-300">
            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle size={32} />
            </div>
            <h3 className="text-lg font-bold text-gray-800 mb-2">메일 전송 완료!</h3>
            <p className="text-gray-600 text-sm mb-6">
              <strong>{email}</strong>(으)로 메일을 보냈습니다.<br/>
              메일함을 확인하여 비밀번호를 재설정해주세요.
            </p>
            <button 
              onClick={() => navigate('/login')}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition-colors"
            >
              로그인 하러 가기
            </button>
          </div>
        ) : (
          // 이메일 입력 폼
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
              className="w-full bg-black text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:bg-gray-800 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  전송 중...
                </span>
              ) : '비밀번호 재설정 메일 받기'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}