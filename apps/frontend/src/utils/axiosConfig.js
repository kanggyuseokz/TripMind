// apps/frontend/src/utils/axiosConfig.js
/**
 * Axios 인터셉터 설정
 * 모든 API 요청에 자동으로 Authorization 헤더 추가
 */

import axios from 'axios';

// 기본 URL 설정
axios.defaults.baseURL = 'http://localhost:8080';

// ✅ 요청 인터셉터: 모든 요청에 토큰 자동 추가
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔑 토큰 자동 추가:', token.substring(0, 20) + '...');
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ✅ 응답 인터셉터: 401 에러 시 자동 로그아웃
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('⚠️ 토큰 만료, 로그아웃 처리');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axios;
