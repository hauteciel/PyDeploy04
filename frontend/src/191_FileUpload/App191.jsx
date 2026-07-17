import React, { useState, useEffect } from 'react';
import { Container, Form, Button, Table, Modal, Alert, Card } from 'react-bootstrap';
import api from './api'; 

import 'bootstrap/dist/css/bootstrap.min.css';

// 분리한 컴포넌트 임포트
import FileForm from './components/FileForm';
import FileTable from './components/FileTable';
import ImageModal from './components/ImageModal';

const App191 = () => {
  // ---------------------------------------------------------------------------
  // [공통 State 상태 관리 정의]
  // ---------------------------------------------------------------------------  
  const [files, setFiles] = useState([]);   // 백엔드로부터 응답받은 파일 목록 상태 배열

  const [title, setTitle] = useState('');   // 사용자가 새로 작성 중인 파일 설명란 값
  const [selectedFile, setSelectedFile] = useState(null); // 사용자가 선택한 이진 물리 파일 바디 객체
  
  const [error, setError] = useState('');               // 화면에 상단에 노출할 경고/에러 텍스트 메시지
  const [success, setSuccess] = useState('');           // 화면 상단에 노출할 성공 처리 알림 메시지

  const [showModal, setShowModal] = useState(false);       // 이미지 미리보기 모달 노출 여부 스위치 플래그
  const [currentImgUrl, setCurrentImgUrl] = useState('');  // 모달 이미지 태그가 추적할 전용 스트리밍 경로
  const [modalTitle, setModalTitle] = useState('');         // 모달 상단에 노출할 해당 이미지의 타이틀 정보

  // ---------------------------------------------------------------------------
  // [1] 파일 목록 가져오기
  //     백엔드로부터 전체 업로드 목록을 수신하는 비동기 함수
  // ---------------------------------------------------------------------------  
  const fetchFiles = async () => {
    try {
      // api.js의 베이스 엔드포인트 주소(http://127.0.0.1:8000/api/files)로 GET 요청
      const response = await api.get('');      
      setFiles(response.data);  // Axios는 응답 성공 시 JSON 파싱 결과를 즉시 response.data에 매핑해 줍니다.
    } catch (err) {
      // optional chaining(?.)을 사용해 안전하게 백엔드가 던진 HTTPException 상세 내역을 파싱하여 경고창에 반영합니다.
      setError(err.response?.data?.detail || '목록을 불러오는 데 실패했습니다.');
    }
  };

  // 컴포넌트가 브라우저에 최초 마운트(렌더링 완성)되는 시점에 1회 리스트 조회를 트리거합니다.
  useEffect(() => {
    fetchFiles();
  }, []);

  // 파일 선택 핸들러
  // 파일 인풋 컴포넌트에서 파일 변동 감지 시 상태 기록 핸들러
  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]); // 첫 번째 단일 선택 파일을 타겟팅하여 반영
    setError(''); // 기존에 떠있던 에러창 청소
  };

  // ---------------------------------------------------------------------------
  // [2] 파일 업로드 핸들러
  //     폼 서브밋: 파일 및 정보 업로드 비동기 핸들러
  // ---------------------------------------------------------------------------  
  const handleUpload = async (e) => {
    e.preventDefault(); // 폼 전송 시 브라우저가 강제로 페이지 새로고침(Refresh)하는 동작 차단
    setError('');
    setSuccess('');

    if (!selectedFile) {
      setError('업로드할 파일을 선택해주세요.');
      return;
    }
    if (!title.trim()) {
      setError('파일 설명을 입력해주세요.');
      return;
    }

    // 백엔드와 규격을 일치시켜 프론트 단에서 먼저 2MB 용량 초과 파일을 필터링합니다.
    if (selectedFile.size > 2 * 1024 * 1024) {
      setError('파일 용량은 2MB를 초과할 수 없습니다.');
      return;
    }

    // 파일 전송용 특수 바이너리 포맷 객체인 FormData 인스턴스 생성 및 주입
    const formData = new FormData();
    formData.append('file', selectedFile);  // 백엔드 파라미터 변수명인 'file' 키로 바디 설정

    try {
      const response = await api.post('/upload', formData, {
        params: { title: title },
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // 정상적인 상태 코드를 받으면 상태 초기화 및 화면 새로고침 수행
      if (response.status === 200 || response.status === 201) {
        setSuccess('✅파일이 성공적으로 업로드되었습니다.');
        setTitle('');
        setSelectedFile(null);
        document.getElementById('fileInput').value = ''; // Input 초기화 // 실제 HTML 파일 인풋창 물리 초기화 리셋
        fetchFiles(); // 새 파일이 반영되도록 리스트 강제 재동기화 갱신
      }
    } catch (err) {
      setError(err.response?.data?.detail || '💥업로드 중 서버 오류가 발생했습니다.');
    }
  };

  // ---------------------------------------------------------------------------
  // [3] 파일 다운로드 처리
  //     다운로드 가로채기 동작 정의
  // ---------------------------------------------------------------------------  
  const handleDownload = (id) => {
    // Axios 비동기 구조 대신 브라우저의 전역 네이티브 스트림 다운로드를 실행하기 위해
    // 강제 주소 이동 링크 스트리밍을 수행합니다.    
    window.location.href = `${api.defaults.baseURL}/download/${id}`;
  };

  // ---------------------------------------------------------------------------
  // [4] 이미지 보기 처리 (모달 팝업 실행)
  //     이미지 팝업 모달 실행용 제어 지시 핸들러
  // ---------------------------------------------------------------------------  
  const handleViewImage = (id, fileTitle) => {
    setCurrentImgUrl(`${api.defaults.baseURL}/view/${id}`);
    setModalTitle(fileTitle);
    setShowModal(true);
  };

  return (
    <Container className="my-5">
      <h2 className="mb-4 text-center fw-bold text-primary">파일 업로드 및 관리 시스템</h2>
      
      {/* 알림 메시지 배너 영역 (조건부 토글 렌더링) */}
      {error && <Alert variant="danger" onClose={() => setError('')} dismissible>{error}</Alert>}
      {success && <Alert variant="success" onClose={() => setSuccess('')} dismissible>{success}</Alert>}

      {/* [컴포넌트 1] 업로드 입력 및 전송 처리 폼 카드 */}
      <FileForm 
        title={title}
        setTitle={setTitle}
        handleFileChange={handleFileChange}
        handleUpload={handleUpload}
      />

      {/* [컴포넌트 2 & 3] 업로드된 파일 목록 테이블 (내부적으로 Row 컴포넌트 호출) */}
      <h4 className="mb-3 fw-semibold">업로드된 파일 목록</h4>
      <FileTable 
        files={files}
        handleDownload={handleDownload}
        handleViewImage={handleViewImage}
      />

      {/* [컴포넌트 4] 이미지 미리보기 팝업 모달 */}
      <ImageModal 
        showModal={showModal}
        setShowModal={setShowModal}
        currentImgUrl={currentImgUrl}
        modalTitle={modalTitle}
      />
    </Container>
  );
};

export default App191;