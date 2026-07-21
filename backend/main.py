import os

import database
import uvicorn
from controllers import router as file_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development | production

# 앱 생성 시점에 DB 테이블 자동 생성 (서버 시작 시 실행)
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="File Management System")

# 프론트엔드 결합을 위한 CORS 설정
# ALLOWED_ORIGINS: .env 에서 콤마(,)로 구분된 허용 주소 목록을 읽어옵니다.
# dev 기본값은 Vite 로컬 개발 서버, prod 에서는 실제 배포 도메인을 .env 에 지정합니다.
origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(file_router)

if __name__ == "__main__":
    # 개발(development): 코드 변경 시 자동 재시작(reload) + localhost 바인딩
    # 운영(production): reload 비활성화 + 0.0.0.0 바인딩(Nginx 등 리버스 프록시가 앞단에 위치)
    is_dev = ENVIRONMENT == "development"
    uvicorn.run(
        "main:app",
        host="127.0.0.1" if is_dev else "0.0.0.0",
        port=8000,
        reload=is_dev,
    )