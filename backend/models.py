from datetime import datetime
from database import Base
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

# ---------------------------------------------------------------------------
# UploadedFile: 데이터베이스 테이블과 매핑되는 ORM 모델 클래스
# ---------------------------------------------------------------------------
class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    # [SQLAlchemy 2.0 스타일 매핑 설명]
    # - Mapped[타입]: Python의 타입 힌팅을 지원하여 IDE의 자동완성과 정적 분석을 극대화합니다.
    # - mapped_column(): 실제 SQL 필드의 제약 조건(기본키, 널 허용 여부, 인덱스 등)을 설정합니다.    

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(30), nullable=False) # 파일 설명
    original_name: Mapped[str] = mapped_column(String(100), nullable=False) # 원본 파일명
    uploaded_name: Mapped[str] = mapped_column(String(100), nullable=False) # 저장된 파일명
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )