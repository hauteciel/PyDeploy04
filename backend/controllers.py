# 파일 처리 비즈니스 로직 및 REST API 엔드포인트를 정의. 
# 파일 저장, 용량 검증, 파일 조회 및 스트리밍 다운로드가 이루어집니다.

import os
import uuid
import storage
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from models import UploadedFile
from schemas import FileApiResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

"""
📌UploadFile
FastAPI에서 제공하는 UploadFile은 클라이언트가 폼(Form) 데이터로 전송한 
업로드 파일에 접근하고, 이를 효율적으로 다루기 위해 사용하는 객체입니다.
파이썬의 기본 자식 프레임워크인 Starlette의 UploadFile을 기반으로 만들어졌으며, 
대용량 파일 업로드 시 발생할 수 있는 메모리 문제를 우아하게 해결해 줍니다.

장점1: 스풀 파일(Spooled File) 메커니즘을 통한 메모리 최적화
장점2: 파일 객체 인터페이스(File-like object) 지원
      read(), write(), seek(), tell() 등의 메서드를 동일하게 지원

주요속성
    file: 실제 파이썬 파일 객체(정확히는 SpooledTemporaryFile)에 직접 접근할 수 있는 포인터입니다.
    filename: 클라이언트가 업로드한 원본 파일 이름 문자열입니다. (예: profile_photo.png)
    size: 파일의 크기(바이트 단위)입니다. (FastAPI 최신 버전에서는 이 속성이 기본 제공되지만, 버전에 따라 seek와 tell을 활용하기도 합니다.)
    headers: 파일과 함께 전송된 HTTP 헤더 정보입니다. (예: Content-Type: image/jpeg)

UploadFile은 비동기(async/await) 환경에서 논블로킹(Non-blocking)으로 동작
    이 경우 사용할때 await 붙여주어야 함.    
"""

"""
📌FileResponse
FileResponse는 서버에 존재하는 물리적 파일(이미지, PDF, 압축파일, 텍스트 등)을 
클라이언트(브라우저)에게 스트리밍 형태로 안전하고 효율적으로 전송하기 위해 사용하는 
특수 응답(Response) 객체입니다.

FastAPI의 기반이 되는 ASGI 툴킷인 Starlette에서 가져온 기능으로, 
큰 파일을 전송할 때 메모리를 과도하게 점유하지 않고 청크(Chunk) 단위로 
나누어 보낼 수 있도록 설계되어 있습니다

장점1: 효율적인 메모리 관리 (비동기 스트리밍)
장점2: HTTP 표준 헤더의 자동 처리 (Content-Length, Content-Type, Last-Modified)

핵심매개변수
FileResponse(
    path="서버_내의_실제_파일_경로",  (필수)
    filename="클라이언트가_받아볼_파일_이름",  (선택)
    media_type="MIME_타입_지정",  (선택)
    status_code=200
)

"""


# ---------------------------------------------------------------------------
# 라우터 객체 생성
# ---------------------------------------------------------------------------
# prefix="/api/files" 설정을 통해 이 라우터 안의 모든 URL 경로 앞에 공통 주소가 붙습니다.
router = APIRouter(prefix="/api/files", tags=["files"])

# ---------------------------------------------------------------------------
# 설정 변수 (Configuration)
# : 제한 용량 (2MB). 실제 저장 위치(local 디스크 / S3)는 storage.py 가 담당합니다.
# ---------------------------------------------------------------------------
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


@router.post("/upload", response_model=FileApiResponse)
async def upload_file(
    title: str, file: UploadFile, db: Session = Depends(get_db)
):
    # 1. 파일 용량 체크
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail="파일 용량은 2MB를 초과할 수 없습니다."
            # 400: Bat Request
        )

    # 2. 파일명 중복 방지를 위한 Rename 처리
    ext = os.path.splitext(file.filename)[1]  # 파일 확장자
    unique_filename = f"{uuid.uuid4().hex}{ext}" # 고유한 파일명 생성

    # 3. 저장소에 파일 저장 (STORAGE_BACKEND=local -> 로컬 디스크 / s3 -> S3 버킷)
    try:
        content = await file.read()  # UploadFile 객체는 async 함수에서는 비동기로 동작?
        storage.save_file(unique_filename, content)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"파일 저장 중 오류가 발생했습니다: {str(e)}"
        )

    # 4. 데이터베이스에 기록 저장 (SQLAlchemy 2.0)
    db_file = UploadedFile(
        title=title,
        original_name=file.filename,
        uploaded_name=unique_filename,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return db_file

# ---------------------------------------------------------------------------
# [GET] /api/files : 업로드된 파일 전체 목록 조회 API
# ---------------------------------------------------------------------------
@router.get("", response_model=list[FileApiResponse])
def get_files(db: Session = Depends(get_db)):
    """업로드된 파일 전체 목록 조회 API"""
    # 🌟 SQLAlchemy 2.0 스타일 수정: select().order_by() 사용
    stmt = select(UploadedFile).order_by(UploadedFile.id.desc())
    result = db.scalars(stmt).all()
    return result

# ---------------------------------------------------------------------------
# [GET] /api/files/download/{file_id} : 안전한 파일 다운로드 API (원본 파일명 복원)
# ---------------------------------------------------------------------------
@router.get("/download/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db)):
    """파일 다운로드 API (원본 파일명 복원)"""
    # 🌟 SQLAlchemy 2.0 스타일 수정: select().where() 사용
    stmt = select(UploadedFile).where(UploadedFile.id == file_id)
    db_file = db.scalar(stmt)

    if not db_file:
        raise HTTPException(
            status_code=404, detail="파일을 찾을 수 없습니다."
        )

    if not storage.file_exists(db_file.uploaded_name):
        raise HTTPException(
            status_code=404, detail="서버에 실제 파일이 존재하지 않습니다."
        )

    # local: 서버에 저장된 파일을 직접 스트리밍
    # s3: 클라이언트를 S3 임시 서명 URL로 리다이렉트하여 서버를 거치지 않고 바로 다운로드
    if storage.STORAGE_BACKEND == "s3":
        url = storage.get_presigned_url(
            db_file.uploaded_name, download_name=db_file.original_name
        )
        return RedirectResponse(url=url)

    return FileResponse(
        path=storage.get_local_path(db_file.uploaded_name),
        filename=db_file.original_name,
        media_type="application/octet-stream",
    )

# ---------------------------------------------------------------------------
# [GET] /api/files/view/{file_id} : 이미지 보기용 파일 스트리밍 API (팝업 전용)
# ---------------------------------------------------------------------------
@router.get("/view/{file_id}")
def view_file(file_id: int, db: Session = Depends(get_db)):
    """이미지 보기용 파일 스트리밍 API"""

    # 파일 다운로드와 로직은 유사하지만, 브라우저가 강제 다운로드하지 않고 
    # 브라우저 내부 화면(모달 창 등)에 직접 렌더링할 수 있도록 돕는 엔드포인트입니다.
    stmt = select(UploadedFile).where(UploadedFile.id == file_id)
    db_file = db.scalar(stmt)

    if not db_file:
        raise HTTPException(
            status_code=404, detail="파일을 찾을 수 없습니다."
        )

    # 물리적인 파일 존재 여부 검증
    if not storage.file_exists(db_file.uploaded_name):
        raise HTTPException(
            status_code=404, detail="서버에 실제 파일이 존재하지 않습니다."
        )

    # local: filename= 매개변수를 제외하고 전송하여 브라우저가 인라인 스트리밍으로 렌더링하게 만듭니다
    # s3: S3 임시 서명 URL로 리다이렉트 (브라우저가 직접 S3에서 이미지를 받아옴)
    if storage.STORAGE_BACKEND == "s3":
        return RedirectResponse(url=storage.get_presigned_url(db_file.uploaded_name))

    return FileResponse(path=storage.get_local_path(db_file.uploaded_name))