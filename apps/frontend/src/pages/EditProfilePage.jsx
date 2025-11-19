import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Lock, Mail, Save, Loader2, CheckCircle } from 'lucide-react';

export default function EditProfilePage() {
  const navigate = useNavigate();
  
  // [Mock Data] 초기값
  const [formData, setFormData] = useState({
    username: "여행자123",
    email: "traveler@example.com", // 이메일은 보통 변경 불가
    currentPassword: "",
    newPassword: "",
    confirmPassword: ""
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError(""); // 입력 시 에러 초기화
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    // 1. 유효성 검사 (프론트엔드)
    if (formData.newPassword && formData.newPassword.length < 8) {
      setError("새 비밀번호는 8자 이상이어야 합니다.");
      setLoading(false);
      return;
    }
    if (formData.newPassword !== formData.confirmPassword) {
      setError("새 비밀번호가 일치하지 않습니다.");
      setLoading(false);
      return;
    }

    // 2. 백엔드 API 호출 시뮬레이션
    setTimeout(() => {
      setLoading(false);
      // 성공 처리
      setSuccess("회원 정보가 성공적으로 수정되었습니다.");
      // 2초 뒤 마이페이지로 이동
      setTimeout(() => navigate('/mypage'), 1500);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 h-16 flex items-center justify-between">
          <button onClick={() => navigate('/mypage')} className="text-gray-500 hover:text-gray-900 flex items-center gap-1 font-medium">
            <ArrowLeft size={20} /> 취소
          </button>
          <span className="text-lg font-bold">정보 수정</span>
          <div className="w-16"></div> {/* 중앙 정렬을 위한 더미 */}
        </div>
      </header>

      <main className="max-w-xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
          
          <div className="text-center mb-8">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 text-4xl">
              👤
            </div>
            <button className="text-sm text-blue-600 font-medium hover:underline">
              프로필 사진 변경
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 이메일 (읽기 전용) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">이메일</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"><Mail size={18}/></span>
                <input 
                  type="email" 
                  name="email"
                  value={formData.email} 
                  disabled 
                  className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-500 cursor-not-allowed"
                />
              </div>
            </div>

            {/* 사용자 이름 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">사용자 이름</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"><User size={18}/></span>
                <input 
                  type="text" 
                  name="username"
                  value={formData.username} 
                  onChange={handleChange}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>

            <div className="border-t border-gray-100 my-6 pt-6">
              <h3 className="text-sm font-bold text-gray-900 mb-4">비밀번호 변경</h3>
              
              {/* 현재 비밀번호 */}
              <div className="mb-4">
                <label className="block text-xs text-gray-500 mb-1">현재 비밀번호</label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"><Lock size={18}/></span>
                  <input 
                    type="password" 
                    name="currentPassword"
                    value={formData.currentPassword}
                    onChange={handleChange}
                    placeholder="변경하려면 입력하세요"
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              {/* 새 비밀번호 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">새 비밀번호</label>
                  <input 
                    type="password" 
                    name="newPassword"
                    value={formData.newPassword}
                    onChange={handleChange}
                    placeholder="8자 이상"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">새 비밀번호 확인</label>
                  <input 
                    type="password" 
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="한 번 더 입력"
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 outline-none ${
                      formData.newPassword && formData.newPassword !== formData.confirmPassword 
                        ? 'border-red-300 focus:ring-red-200' 
                        : 'border-gray-300 focus:ring-blue-500'
                    }`}
                  />
                </div>
              </div>
            </div>

            {/* 상태 메시지 */}
            {error && <div className="text-red-500 text-sm text-center bg-red-50 p-3 rounded-lg">{error}</div>}
            {success && (
              <div className="text-green-600 text-sm text-center bg-green-50 p-3 rounded-lg flex items-center justify-center gap-2">
                <CheckCircle size={16} /> {success}
              </div>
            )}

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-black text-white font-bold py-4 rounded-xl shadow-lg hover:bg-gray-800 transition-all flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Save size={20} />}
              저장하기
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}