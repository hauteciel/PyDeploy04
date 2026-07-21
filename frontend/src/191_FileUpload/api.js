import axios from 'axios';

// 환경별 백엔드 주소는 .env.development / .env.production 의 VITE_API_BASE_URL 값을 사용합니다.
// (Vite는 빌드 모드에 따라 .env.[mode] 파일을 자동으로 읽어 import.meta.env 에 주입합니다)
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 5000, // 5초 초과 시 타임아웃 오류
  headers: {
    // 멀티파트 업로드 및 일반 요청에 유연하게 대응하기 위해 
    // 기본 Header 설정 (필요시 요청 메서드에서 자동 변경됨)
    'Accept': 'application/json',
  }
});

export default api;