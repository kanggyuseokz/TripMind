import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; 
import { Send, Plane, Loader2, Menu, X, Search, Calendar } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const goLogin = () => navigate('/login');

  const handlePlanTrip = () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError('');

    // 1.5초 뒤 플래너 페이지로 이동 (입력한 내용을 state로 전달)
    setTimeout(() => {
      setLoading(false);
      navigate('/planner', { state: { initialPrompt: prompt } });
    }, 1500);
  };

  const destinations = [
    { city: 'OSAKA', name: '오사카', image: 'https://images.unsplash.com/photo-1589452271712-64b8a66c7b71?q=80&w=1742&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D' },
    { city: 'TOKYO', name: '도쿄', image: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&q=80' },
    { city: 'DANANG', name: '다낭', image: 'https://images.unsplash.com/photo-1558002890-c0b30998d1e6?q=80&w=1742&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D' },
    { city: 'NEW YORK', name: '뉴욕', image: 'https://images.unsplash.com/photo-1541336032412-2048a678540d?q=80&w=3087&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D' },
    { city: 'PARIS', name: '파리', image: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400&q=80' },
    { city: 'JEJU', name: '제주', image: 'https://images.unsplash.com/photo-1695321924057-91977a88eae1?q=80&w=550&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D' },
  ];

  return (
    <div className="min-h-screen bg-white font-sans text-gray-900">

      {/* 메인 콘텐츠 */}
      <main className="flex flex-col lg:flex-row">
        
        {/* 좌측: 텍스트 & 설명 영역 */}
        <div className="flex-1 flex flex-col justify-center lg:justify-start lg:pt-32 px-6 lg:px-16 py-12 bg-white z-10">
          <div className="max-w-xl mx-auto lg:mx-0">
            <h1 className="text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold leading-[1.2] tracking-tight text-gray-900 mb-6">
              기존에 경험하지 못한<br />
              새로운 여행 플래너
            </h1>
            <p className="text-lg text-gray-500 mb-10 leading-relaxed">
              고민만 하던 여행 계획을 TripMind를 통해 몇 분 만에 스케줄링 해보세요.<br className="hidden sm:block"/>
              AI가 당신의 취향에 맞는 완벽한 일정을 제안합니다.
            </p>
            
            <button 
              onClick={goLogin}
              className="bg-black text-white px-10 py-4 text-lg font-semibold rounded-sm hover:bg-gray-800 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              TripMind로 시작하기
            </button>
          </div>
        </div>

        {/* 우측: 기능 영역 */}
        <div className="flex-1 bg-gray-50 p-6 lg:p-12 flex items-center justify-center relative overflow-hidden">
          <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-100 rounded-full opacity-50 blur-3xl pointer-events-none"></div>
          <div className="bg-white w-full max-w-2xl rounded-3xl shadow-2xl border border-gray-100 overflow-hidden flex flex-col max-h-[800px] relative z-10">
            
            <div className="p-6 border-b border-gray-100 bg-white sticky top-0 z-20">
              <div className="text-center mb-4">
                <h3 className="text-lg font-bold text-gray-800">어디로 여행을 떠나시나요?</h3>
                <p className="text-xs text-gray-400 mt-1">AI에게 가고 싶은 곳과 일정을 말해주세요</p>
              </div>
              
              <div className="relative">
                <div className="absolute left-4 top-4 text-gray-400">
                  <Search size={20} />
                </div>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="예: 서울 출발 2박 3일 부산 여행, 바다 보이는 카페 추천해줘"
                  className="w-full pl-12 pr-14 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-black focus:border-transparent outline-none resize-none h-24 text-sm transition-all placeholder:text-gray-400"
                />
                <button
                  onClick={handlePlanTrip}
                  disabled={loading || !prompt.trim()}
                  className={`absolute right-3 bottom-3 p-2 rounded-lg transition-colors ${
                    loading || !prompt.trim() 
                      ? 'bg-gray-200 text-gray-400' 
                      : 'bg-black text-white hover:bg-gray-800'
                  }`}
                >
                  {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6 bg-gray-50/50">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {destinations.map((dest, idx) => (
                  <div 
                    key={idx} 
                    onClick={() => setPrompt(`${dest.name} 여행 계획 짜줘`)}
                    className="group cursor-pointer bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all border border-gray-100 relative aspect-[3/4]"
                  >
                    <img 
                      src={dest.image} 
                      alt={dest.name} 
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-80"></div>
                    <div className="absolute bottom-0 left-0 w-full p-3 text-white">
                      <p className="text-[10px] font-bold tracking-wider uppercase opacity-80">{dest.city}</p>
                      <p className="font-bold text-sm">{dest.name}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}