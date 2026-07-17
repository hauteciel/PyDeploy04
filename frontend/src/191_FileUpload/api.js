import axios from 'axios';

// Axios 인스턴스 기본 설정 객체 생성
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/files', // 백엔드 기본 API 주소
  timeout: 5000, // 5초 초과 시 타임아웃 오류
  headers: {
    // 멀티파트 업로드 및 일반 요청에 유연하게 대응하기 위해 
    // 기본 Header 설정 (필요시 요청 메서드에서 자동 변경됨)
    'Accept': 'application/json',
  }
});

export default api;