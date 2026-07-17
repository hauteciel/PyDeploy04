// 테이블의 각 파일 목록 행

import React from 'react';
import { Button } from 'react-bootstrap';

/**
 * ---------------------------------------------------------------------------
 * FileTableRow Component
 * ---------------------------------------------------------------------------
 * @param {object} file - 백엔드에서 받아온 단일 파일 정보 객체 (id, title, original_name 등)
 * @param {function} handleDownload - 다운로드 버튼 클릭 시 실행할 함수 (App.jsx 전달)
 * @param {function} handleViewImage - 이미지 보기 버튼 클릭 시 실행할 함수 (App.jsx 전달)
 */
function FileTableRow({ file, handleDownload, handleViewImage }) {
  /**
   * [이미지 확장자 판별 헬퍼 함수]
   * 파일 원본 이름의 확장자를 추출하여 팝업이 가능한 이미지 포맷인지 Boolean 값으로 반환합니다.
   * 이 로직을 Row 컴포넌트 내부로 격리하여 테이블 코드가 깔끔해집니다.
   */  
  const isImageFile = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(ext);
    // python : ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
  };

  return (
    <tr>
      {/* 1. 기본 식별 ID 및 설명 출력 */}
      <td>{file.id}</td>
      <td>{file.title}</td>
      <td>{file.original_name}</td>

      {/* 2. 저장된 파일 이름 출력 */}
      {/* UUID 기반의 긴 파일명이 테이블을 찌그러트리지 않도록 
          CSS(text-truncate) 처리를 통해 말줄임(...) 처리를 하고, 마우스 오버 시 전체 이름을 보여줍니다. */}      
      <td className="text-truncate" style={{ maxWidth: '150px' }} title={file.uploaded_name}>
        {file.uploaded_name}
      </td>

      {/* 3. 업로드 시간 포맷팅 */}
      {/* 백엔드의 ISO형태 UTC 시간 문자열을 사용자의 현재 지역 시간 표준 포맷 문자열로 변환합니다. */}
      <td>{new Date(file.uploaded_at).toLocaleString()}</td>

      {/* 4. 조작 버튼 영역 (액션) */}
      <td>
        {/* [다운로드 버튼] */}
        <Button 
          variant="outline-success" 
          size="sm" 
          className="me-2"
          onClick={() => handleDownload(file.id)}
        >
          다운로드
        </Button>

        {/* [이미지 보기 버튼 - 조건부 렌더링] */}
        {/* 업로드된 파일이 이미지 파일 유형에 속할 때만 '이미지 보기' 버튼이 화면에 나타납니다. */}        
        {isImageFile(file.original_name) && (
          <Button 
            variant="outline-info" 
            size="sm"
            onClick={() => handleViewImage(file.id, file.title)}
          >
            이미지 보기
          </Button>
        )}
      </td>
    </tr>
  );
}

export default FileTableRow;