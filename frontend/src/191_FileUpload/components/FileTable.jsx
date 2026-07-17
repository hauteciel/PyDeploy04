// 업로드된 파일 목록 테이블

import React from 'react';
import { Table } from 'react-bootstrap';
import FileTableRow from './FileTableRow';

/**
 * ---------------------------------------------------------------------------
 * FileTable Component
 * ---------------------------------------------------------------------------
 * @param {array} files - 백엔드에서 응답받은 전체 업로드 파일 객체 리스트 배열
 * @param {function} handleDownload - 자식 Row 컴포넌트로 그대로 패스할 다운로드 핸들러
 * @param {function} handleViewImage - 자식 Row 컴포넌트로 그대로 패스할 이미지 보기 핸들러
 */
function FileTable({ files, handleDownload, handleViewImage }) {
  return (
    // 모바일 기기 등 화면이 좁을 때 가로 스크롤을 자동 생성해주는 table-responsive 적용
    <div className="table-responsive shadow-sm rounded">
      <Table striped bordered hover align="middle" className="m-0">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>파일 설명</th>
            <th>원본 파일명</th>
            <th>저장된 파일명</th>
            <th>업로드 시간</th>
            <th style={{ width: '200px' }}>액션</th>
          </tr>
        </thead>
        <tbody>
          {/* files 데이터가 있는 경우와 한개도 없는 경우 구분하여 렌더링 */}
          {files.length === 0 ? (
            <tr>
              <td colSpan="6" className="text-center text-muted py-4">
                업로드된 파일이 없습니다.
              </td>
            </tr>
          ) : (
            files.map((file) => (
              <FileTableRow 
                key={file.id} 
                file={file} 
                handleDownload={handleDownload}
                handleViewImage={handleViewImage}
              />
            ))
          )}
        </tbody>
      </Table>
    </div>
  );
}

export default FileTable;