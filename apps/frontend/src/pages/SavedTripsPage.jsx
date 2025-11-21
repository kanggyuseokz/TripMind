import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, Calendar, MapPin, ArrowRight, Trash2, ArrowLeft } from 'lucide-react';

// 💡 [TIP] 도시별 대표 이미지 매핑 함수
// 백엔드에서 이미지를 안 보내줄 때, 프론트에서 이름으로 찾아서 보여줍니다.
const getCityImage = (destination) => {
  const keyword = destination.split('/')[0].trim(); // "오사카/간사이" -> "오사카"
  
  const images = {
    '오사카': 'https://images.unsplash.com/photo-1590559399607-57523cd47a61?w=800&q=80',
    '도쿄': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80',
    '다낭': 'https://images.unsplash.com/photo-1559592413-7cec430aaec3?w=800&q=80',
    '제주': 'https://images.unsplash.com/photo-1548115184-bc6544d06a58?w=800&q=80',
    '파리': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80',
    '뉴욕': 'https://images.unsplash.com/photo-1496442226666-8d4a0e2907eb?w=800&q=80',
    '방콕': 'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800&q=80',
    '런던': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&q=80',
  };

  // 매핑된 이미지가 있으면 반환, 없으면 랜덤 여행 이미지(기본값) 반환
  return images[keyword] || 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80';
};

export default function SavedTripsPage() {
  const navigate = useNavigate();

  // 백엔드에서 받아올 데이터 예시 (이미지가 없다고 가정)
  const savedTrips = [
    {
      id: 1,
      destination: '오사카/간사이 (KIX)',
      title: '오사카 먹방 투어',
      startDate: '2025-10-23',
      endDate: '2025-10-26',
      durationText: '3박 4일',
      cost: '1,000,000',
      partySize: 2
    },
    {
      id: 2,
      destination: '파리/샤를드골 (CDG)',
      title: '낭만의 파리 일주일',
      startDate: '2025-12-20',
      endDate: '2025-12-27',
      durationText: '6박 7일',
      cost: '3,500,000',
      partySize: 1
    },
    {
      id: 3,
      destination: '제주 (CJU)',
      title: '가을 제주 힐링 여행',
      startDate: '2025-11-10',
      endDate: '2025-11-12',
      durationText: '2박 3일',
      cost: '500,000',
      partySize: 4
    },
    {
      id: 4,
      destination: '뉴욕 (JFK)',
      title: '뉴욕 시티 탐방',
      startDate: '2026-01-01',
      endDate: '2026-01-10',
      durationText: '9박 10일',
      cost: '5,000,000',
      partySize: 2
    }
  ];

  const handleCardClick = (trip) => {
    const tripData = {
      destination: trip.destination,
      startDate: trip.startDate,
      endDate: trip.endDate,
      partySize: trip.partySize,
      budget: trip.cost.replace(/,/g, ''),
      durationText: trip.durationText
    };
    navigate('/result', { state: { tripData } });
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
            <Plane size={24} className="text-blue-600" strokeWidth={2.5} />
            <span className="text-xl font-bold tracking-tight">TripMind</span>
          </div>
          <button onClick={() => navigate('/')} className="text-gray-500 hover:text-gray-900 flex items-center gap-1 text-sm font-medium">
            <ArrowLeft size={18} /> 메인으로
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">나의 여행 보관함</h1>
            <p className="text-gray-500 mt-2">저장된 여행 계획을 확인하고 관리해보세요.</p>
          </div>
          <button 
            onClick={() => navigate('/planner')}
            className="bg-black text-white px-5 py-2.5 rounded-lg font-semibold text-sm hover:bg-gray-800 transition-colors shadow-sm"
          >
            + 새 여행 만들기
          </button>
        </div>

        {savedTrips.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedTrips.map((trip) => (
              <div 
                key={trip.id} 
                onClick={() => handleCardClick(trip)}
                className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl border border-gray-100 transition-all duration-300 cursor-pointer group relative"
              >
                <div className="h-48 overflow-hidden relative">
                  {/* 💡 여기서 getCityImage 함수를 사용하여 이미지를 불러옵니다 */}
                  <img 
                    src={getCityImage(trip.destination)} 
                    alt={trip.destination} 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-60"></div>
                  <div className="absolute bottom-4 left-4 text-white">
                    <p className="text-xs font-medium opacity-90 mb-1 flex items-center gap-1">
                      <MapPin size={12} /> {trip.destination.split('(')[0]}
                    </p>
                    <h3 className="text-xl font-bold">{trip.title}</h3>
                  </div>
                </div>

                <div className="p-5">
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <div className="flex items-center gap-1.5">
                      <Calendar size={16} className="text-blue-500" />
                      <span>{trip.startDate} ({trip.durationText})</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="text-sm font-medium text-gray-900">
                      예산 <span className="text-blue-600">{trip.cost}원</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <button 
                        onClick={(e) => { e.stopPropagation(); alert('삭제 기능 준비중'); }}
                        className="text-gray-400 hover:text-red-500 transition-colors"
                      >
                        <Trash2 size={18} />
                      </button>
                      <div className="bg-gray-50 p-2 rounded-full group-hover:bg-blue-50 transition-colors">
                        <ArrowRight size={18} className="text-gray-400 group-hover:text-blue-600" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-300">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-400">
              <Plane size={32} />
            </div>
            <h3 className="text-lg font-medium text-gray-900">저장된 여행이 없습니다</h3>
            <p className="text-gray-500 mt-1 mb-6">새로운 여행 계획을 만들어보세요!</p>
            <button onClick={() => navigate('/planner')} className="text-blue-600 font-semibold hover:underline">
              여행 계획하러 가기
            </button>
          </div>
        )}
      </main>
    </div>
  );
}