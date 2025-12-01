// apps/frontend/src/components/ProfileImage.jsx
import React, { useState } from 'react';

/**
 * 프로필 이미지 컴포넌트
 * @param {string} imageUrl - 프로필 이미지 URL (백엔드에서 받은 경로)
 * @param {string} username - 사용자 이름 (이니셜 표시용)
 * @param {string} size - 크기 ('sm', 'md', 'lg', 'xl')
 * @param {string} className - 추가 CSS 클래스
 */
export default function ProfileImage({ imageUrl, username, size = 'md', className = '' }) {
  const [imageError, setImageError] = useState(false);
  
  // 크기별 클래스
  const sizeClasses = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-12 h-12 text-lg',
    lg: 'w-20 h-20 text-3xl',
    xl: 'w-24 h-24 text-4xl'
  };

  // 기본 프로필 이미지 (SVG)
  const DefaultProfileSVG = () => (
    <svg 
      className="w-full h-full text-gray-400" 
      fill="currentColor" 
      viewBox="0 0 24 24"
    >
      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
    </svg>
  );

  // 이미지가 있고 에러가 없는 경우
  if (imageUrl && !imageError) {
    return (
      <div className={`${sizeClasses[size]} rounded-full overflow-hidden bg-gray-100 flex-shrink-0 ${className}`}>
        <img 
          src={`http://127.0.0.1:8080${imageUrl}`} 
          alt="Profile" 
          className="w-full h-full object-cover"
          onError={() => setImageError(true)}
        />
      </div>
    );
  }

  // 이미지가 없거나 로드 실패 - 기본 프로필 아이콘
  return (
    <div className={`${sizeClasses[size]} rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 ${className}`}>
      <DefaultProfileSVG />
    </div>
  );
}

/**
 * 그라데이션 배경의 이니셜 프로필
 */
export function ProfileInitial({ username, size = 'md', className = '' }) {
  const sizeClasses = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-12 h-12 text-lg',
    lg: 'w-20 h-20 text-3xl',
    xl: 'w-24 h-24 text-4xl'
  };

  const initial = username ? username.charAt(0).toUpperCase() : 'U';

  return (
    <div className={`${sizeClasses[size]} rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold shadow-md flex-shrink-0 ${className}`}>
      {initial}
    </div>
  );
}