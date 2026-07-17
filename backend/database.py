import os
from dotenv import load_dotenv
# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 1. 데이터베이스 연결 설정 (Database URL)
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 2. SQLAlchemy 엔진(Engine) 생성
engine = create_engine(DATABASE_URL, echo=True)

# 3. 세션 팩토리(SessionFactory) 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. ORM 매핑용 기본 클래스 (Declarative Base)
class Base(DeclarativeBase):
    pass

# ---------------------------------------------------------------------------
# 5. DB 세션 의존성 주입 함수 (Dependency Injection)
# ---------------------------------------------------------------------------
# FastAPI 엔드포인트에서 데이터베이스 작업을 안전하게 처리할 수 있도록 돕는 Generator 함수입니다.
# - yield를 통해 요청이 들어올 때 세션을 생성하여 제공하고,
# - 요청 처리가 완료(또는 에러 발생)되면 finally 구문을 통해 생성된 세션을 반드시 닫아(close) 자원 누수를 방지합니다.
def get_db():
    """DB 세션 의존성 Injection용 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()