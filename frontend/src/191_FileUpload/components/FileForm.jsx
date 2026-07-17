// 업로드 폼 카드
import React from 'react';
import { Card, Form, Button } from 'react-bootstrap';

/**
 * ---------------------------------------------------------------------------
 * FileForm Component
 * ---------------------------------------------------------------------------
 * @param {string} title - 사용자가 입력 중인 파일 설명 텍스트 상태 (App.jsx 제어)
 * @param {function} setTitle - title 상태를 업데이트하는 함수
 * @param {function} handleFileChange - 파일 선택창에서 파일이 변경되었을 때 실행할 핸들러
 * @param {function} handleUpload - 폼 서브밋(업로드 시작) 시 실행할 비즈니스 로직 핸들러
 */
function FileForm({ title, setTitle, handleFileChange, handleUpload }) {
  return (
    <Card className="mb-5 shadow-sm">
      <Card.Body>
        <Form onSubmit={handleUpload}>
          
          {/* [1] 파일 선택 영역 */}
          {/* controlId => 실제 "id=" 로 렌더링 */}
          <Form.Group className="mb-3" controlId="fileInput"> 
            <Form.Label className="fw-semibold">파일 선택 (최대 2MB)</Form.Label>
            <Form.Control type="file" onChange={handleFileChange} />
          </Form.Group>

          {/* [2] 파일 설명 입력 영역 */}
          <Form.Group className="mb-3" controlId="fileTitle">
            <Form.Label className="fw-semibold">파일 설명</Form.Label>
            <Form.Control 
              type="text" 
              placeholder="파일에 대한 설명을 적어주세요 (필수)" 
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </Form.Group>

          {/* [3] 전송 버튼 영역 */}
          {/* type="submit" 속성으로 인해 버튼을 누르면 Form의 onSubmit(handleUpload)이 실행됩니다. */}
          <Button variant="primary" type="submit" className="w-100">
            업로드 시작
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
}

export default FileForm;