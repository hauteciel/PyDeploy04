from datetime import datetime
from pydantic import BaseModel


class FileApiResponse(BaseModel):
    id: int
    title: str
    original_name: str
    uploaded_name: str
    uploaded_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 모델 객체를 Pydantic으로 변환 허용