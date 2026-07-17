import database
import uvicorn
from controllers import router as file_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 앱 생성 시점에 DB 테이블 자동 생성 (서버 시작 시 실행)
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="File Management System")

# 프론트엔드 결합을 위한 CORS 설정
origins = [
    "http://localhost:5173",  # Vite 기본 포트
    "http://127.0.0.1:5173",
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)