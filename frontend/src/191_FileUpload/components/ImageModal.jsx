// 이미지 미리보기 팝업 모달

import React from 'react';
import { Modal, Button } from 'react-bootstrap';

/**
 * ---------------------------------------------------------------------------
 * ImageModal Component
 * ---------------------------------------------------------------------------
 * @param {boolean} showModal - 모달 팝업의 활성화/숨김 여부 상태 변수
 * @param {function} setShowModal - 모달 노출 상태를 제어하는 상태 변경 함수 (false를 주어 닫기 수행)
 * @param {string} currentImgUrl - 모달 내부에 바인딩될 백엔드 이미지 스트리밍 전용 URL
 * @param {string} modalTitle - 상단 헤더 영역에 노출될 파일의 원래 설명 명칭
 */
function ImageModal({ showModal, setShowModal, currentImgUrl, modalTitle }) {
  return (
    // centered 속성으로 화면 정확히 정중앙에 배치, size="lg"로 큰 규격 레이아웃 채택
    <Modal show={showModal} onHide={() => setShowModal(false)} size="lg" centered>
      
      {/* 모달 상단부 헤더: 제목 및 X버튼(closeButton) */}
      <Modal.Header closeButton>
        <Modal.Title>{modalTitle}</Modal.Title>
      </Modal.Header>
      
      {/* 모달 중앙 본문: 백엔드 이미지 라우터 소스를 직접 바라보는 <img> 태그 배치 */}
      <Modal.Body className="text-center bg-light">
        {/* currentImgUrl 이 있는 경우만 <img> 조건부 렌더링 */}
        {currentImgUrl && (
          <img 
            src={currentImgUrl} 
            alt={modalTitle} 
            style={{ maxWidth: '100%', maxHeight: '70vh', objectFit: 'contain' }} 
            className="rounded shadow-sm"
          />
        )}
      </Modal.Body>

      {/* 모달 하단 하이라이트: 제어 액션 영역 */}
      <Modal.Footer>
        <Button variant="secondary" onClick={() => setShowModal(false)}>
          닫기
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default ImageModal;