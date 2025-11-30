import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Lock, Mail, Save, Loader2, CheckCircle, Camera } from 'lucide-react';

const API_BASE_URL = "http://127.0.0.1:8080/api/auth";

export default function EditProfilePage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    currentPassword: "",
    newPassword: "",
    confirmPassword: ""
  });

  const [profileImage, setProfileImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [loading, setLoading] = useState(false);
  const [fetchingProfile, setFetchingProfile] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      alert("로그인이 필요합니다.");
      navigate('/login');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        alert("로그인 세션이 만료되었습니다.");
        navigate('/login');
        return;
      }

      if (!response.ok) {
        throw new Error('프로필을 불러오지 못했습니다.');
      }

      const data = await response.json();
      
      setFormData({
        username: data.username || "",
        email: data.email || "",
        currentPassword: "",
        newPassword: "",
        confirmPassword: ""
      });

      // 프로필 이미지 설정
      if (data.profile_image) {
        setImagePreview(`http://127.0.0.1:8080${data.profile_image}`);
      }

    } catch (err) {
      console.error('프로필 로딩 실패:', err);
      setError(err.message);
    } finally {
      setFetchingProfile(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError("");
  };

  // ✅ 이미지 선택
  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    
    if (!file) return;

    // 파일 크기 체크 (3MB)
    if (file.size > 3 * 1024 * 1024) {
      setError("파일 크기는 3MB 이하여야 합니다.");
      return;
    }

    // 파일 형식 체크
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError("PNG, JPG, JPEG, GIF, WEBP 형식만 업로드 가능합니다.");
      return;
    }

    setProfileImage(file);
    setImagePreview(URL.createObjectURL(file));
    setError("");

    // 자동 업로드
    uploadImage(file);
  };

  // ✅ 이미지 업로드
  const uploadImage = async (file) => {
    const token = localStorage.getItem('token');
    setUploadingImage(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append('profile_image', file);

      const response = await fetch(`${API_BASE_URL}/profile/image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.status === 401) {
        localStorage.removeItem('token');
        alert("로그인 세션이 만료되었습니다.");
        navigate('/login');
        return;
      }

      if (!response.ok) {
        throw new Error(data.error || "이미지 업로드 실패");
      }

      // 성공
      setSuccess("프로필 사진이 변경되었습니다.");
      setTimeout(() => setSuccess(""), 2000);

      // localStorage의 user 정보 업데이트
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      user.profile_image = data.image_url;
      localStorage.setItem('user', JSON.stringify(user));

    } catch (err) {
      console.error('이미지 업로드 실패:', err);
      setError(err.message);
    } finally {
      setUploadingImage(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

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

    if (formData.newPassword && !formData.currentPassword) {
      setError("현재 비밀번호를 입력해주세요.");
      setLoading(false);
      return;
    }

    const token = localStorage.getItem('token');

    if (!token) {
      alert("로그인이 필요합니다.");
      navigate('/login');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: formData.username,
          current_password: formData.currentPassword || null,
          new_password: formData.newPassword || null
        })
      });

      const data = await response.json();

      if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        alert("로그인 세션이 만료되었습니다.");
        navigate('/login');
        return;
      }

      if (!response.ok) {
        throw new Error(data.error || "프로필 수정에 실패했습니다.");
      }

      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
      }

      setSuccess("회원 정보가 성공적으로 수정되었습니다.");
      setTimeout(() => navigate('/mypage'), 1500);

    } catch (err) {
      console.error('프로필 수정 실패:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (fetchingProfile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="animate-spin text-blue-600 mx-auto mb-4" size={48} />
          <p className="text-gray-500">프로필을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 h-16 flex items-center justify-between">
          <button onClick={() => navigate('/mypage')} className="text-gray-500 hover:text-gray-900 flex items-center gap-1 font-medium">
            <ArrowLeft size={20} /> 취소
          </button>
          <span className="text-lg font-bold">정보 수정</span>
          <div className="w-16"></div>
        </div>
      </header>

      <main className="max-w-xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
          
          {/* ✅ 프로필 이미지 업로드 */}
          <div className="text-center mb-8">
            <div className="relative w-24 h-24 mx-auto mb-4">
              {/* 이미지 미리보기 */}
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden">
                {imagePreview ? (
                  <img src={imagePreview} alt="Profile" className="w-full h-full object-cover" />
                ) : (
                  <span className="text-4xl">👤</span>
                )}
              </div>

              {/* 업로드 버튼 */}
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadingImage}
                className="absolute bottom-0 right-0 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors shadow-lg disabled:bg-gray-400"
              >
                {uploadingImage ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Camera size={16} />
                )}
              </button>
            </div>

            {/* 숨겨진 파일 input */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
              onChange={handleImageSelect}
              className="hidden"
            />

            <p className="text-xs text-gray-500">
              PNG, JPG, GIF, WEBP (최대 3MB)
            </p>
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
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>

            <div className="border-t border-gray-100 my-6 pt-6">
              <h3 className="text-sm font-bold text-gray-900 mb-4">비밀번호 변경 (선택)</h3>
              
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
              className="w-full bg-black text-white font-bold py-4 rounded-xl shadow-lg hover:bg-gray-800 transition-all flex items-center justify-center gap-2 disabled:bg-gray-400"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Save size={20} />}
              {loading ? '저장 중...' : '저장하기'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}