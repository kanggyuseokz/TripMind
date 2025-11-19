import React, { useState } from 'react';
import { Send, Plane, Calendar, Loader2, AlertCircle, Menu, X, Search } from 'lucide-react';

function App() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // 백엔드 API 주소
  const API_URL = 'http://127.0.0.1:8080/api/llm/complete';

  const handlePlanTrip = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError('');
    setResult('');

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          system: "당신은 전문적인 여행 플래너입니다. 사용자의 요청에 맞춰 하루 단위의 상세한 여행 일정, 추천 맛집, 이동 동선, 팁 등을 포함하여 한국어로 친절하게 답변해주세요."
        }),
      });

      if (!response.ok) throw new Error(`서버 오류: ${response.status}`);

      const data = await response.json();
      setResult(data.output || '답변이 비어있습니다.');
    } catch (err) {
      console.error(err);
      setError('여행 계획을 가져오는 데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 사진 속 느낌을 내기 위한 더미 데이터 (우측 카드 리스트용)
  const destinations = [
    { city: 'OSAKA', name: '오사카', image: 'https://images.unsplash.com/photo-1590559399607-57523cd47a61?w=400&q=80' },
    { city: 'TOKYO', name: '도쿄', image: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&q=80' },
    { city: 'DANANG', name: '다낭', image: 'https://images.unsplash.com/photo-1559592413-7cec430aaec3?w=400&q=80' },
    { city: 'NEW YORK', name: '뉴욕', image: 'https://images.unsplash.com/photo-1496442226666-8d4a0e2907eb?w=400&q=80' },
    { city: 'PARIS', name: '파리', image: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400&q=80' },
    { city: 'JEJU', name: '제주', image: 'https://images.unsplash.com/photo-1548115184-bc6544d06a58?w=400&q=80' },
  ];

  return (
    <div className="min-h-screen bg-white font-sans text-gray-900">
      {/* 헤더 (네비게이션) */}
      <header className="fixed top-0 left-0 right-0 bg-white/90 backdrop-blur-md z-50 h-20 flex items-center border-b border-gray-100">
        <div className="container mx-auto px-6 lg:px-12 flex justify-between items-center w-full">
          {/* 로고 */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center text-white">
              <Plane size={20} strokeWidth={2.5} />
            </div>
            <span className="text-xl font-bold tracking-tight text-gray-900">TRIPMIND</span>
          </div>

          {/* 데스크탑 메뉴 */}
          <nav className="hidden md:flex items-center gap-8 text-[15px] font-medium text-gray-600">
            <a href="#" className="hover:text-black transition-colors">여행지</a>
            <a href="#" className="hover:text-black transition-colors">고객지원</a>
            <a href="#" className="hover:text-black transition-colors">이용방법</a>
            <a href="#" className="hover:text-black transition-colors">로그인</a>
          </nav>

          {/* 모바일 메뉴 버튼 */}
          <button className="md:hidden" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </header>

      {/* 메인 콘텐츠 (좌우 분할 레이아웃) */}
      <main className="pt-20 min-h-screen flex flex-col lg:flex-row">
        
        {/* 좌측: 텍스트 & 설명 영역 */}
        <div className="flex-1 flex flex-col justify-center px-6 lg:px-16 py-12 lg:py-0 bg-white z-10">
          <div className="max-w-xl mx-auto lg:mx-0">
            <h1 className="text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold leading-[1.2] tracking-tight text-gray-900 mb-6">
              기존에 경험하지 못한<br />
              새로운 여행 플래너
            </h1>
            <p className="text-lg text-gray-500 mb-10 leading-relaxed">
              고민만 하던 여행 계획을 TripMind를 통해 몇 분 만에 스케줄링 해보세요.<br className="hidden sm:block"/>
              AI가 당신의 취향에 맞는 완벽한 일정을 제안합니다.
            </p>
            
            {/* 시작하기 버튼 */}
            <button 
              onClick={() => document.getElementById('ai-input').focus()}
              className="bg-black text-white px-10 py-4 text-lg font-semibold rounded-sm hover:bg-gray-800 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              TripMind로 시작하기
            </button>
          </div>
        </div>

        {/* 우측: 기능 & 비주얼 영역 (사진 속 우측 화면 구현) */}
        <div className="flex-1 bg-gray-50 p-6 lg:p-12 flex items-center justify-center relative overflow-hidden">
          {/* 배경 장식 원 */}
          <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-100 rounded-full opacity-50 blur-3xl pointer-events-none"></div>

          {/* 목업 컨테이너 (사진 속 하얀색 박스 영역) */}
          <div className="bg-white w-full max-w-2xl rounded-3xl shadow-2xl border border-gray-100 overflow-hidden flex flex-col max-h-[800px] relative z-10">
            
            {/* 1. 상단 AI 입력바 (사진 속 검색창 위치) */}
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
                  id="ai-input"
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

            {/* 2. 결과 또는 추천 여행지 리스트 */}
            <div className="flex-1 overflow-y-auto p-6 bg-gray-50/50">
              
              {/* 에러 메시지 */}
              {error && (
                <div className="mb-6 bg-red-50 text-red-600 p-4 rounded-xl text-sm flex items-center gap-2">
                  <AlertCircle size={16} /> {error}
                </div>
              )}

              {/* 결과가 있을 때: 결과 표시 */}
              {result ? (
                <div className="prose prose-sm max-w-none">
                   <div className="flex items-center gap-2 mb-4 text-blue-600 font-bold">
                    <Calendar size={18} />
                    <span>생성된 여행 플랜</span>
                   </div>
                   <div className="whitespace-pre-wrap text-gray-700 bg-white p-6 rounded-xl border border-gray-100 shadow-sm leading-7">
                     {result}
                   </div>
                   <button 
                    onClick={() => setResult('')}
                    className="mt-4 text-xs text-gray-500 underline hover:text-black w-full text-center"
                   >
                    다시 검색하기
                   </button>
                </div>
              ) : (
                /* 결과가 없을 때: 사진처럼 여행지 카드 그리드 표시 */
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
                      {/* 뱃지 예시 */}
                      {idx < 2 && (
                        <div className="absolute top-2 right-2 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded">HOT</div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
