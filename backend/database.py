import os
from dotenv import load_dotenv
# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development | production

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 1. 데이터베이스 연결 설정 (Database URL)
# dev: localhost MySQL / prod: RDS 엔드포인트 (.env 의 DB_HOST 로 전환)
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 2. SQLAlchemy 엔진(Engine) 생성
# echo(SQL 로그 출력)는 개발 환경에서만 켜고, 운영 환경에서는 끕니다.
# pool_pre_ping: 커넥션을 내주기 전 살아있는지 검사 후 죽어있으면 자동 재연결
#   (RDS wait_timeout이나 네트워크 idle timeout으로 끊긴 커넥션을 오래 붙잡고 있다 실패하는 것 방지)
# pool_recycle: 이 시간(초)이 지난 커넥션은 서버가 끊기 전에 선제적으로 재생성
engine = create_engine(
    DATABASE_URL,
    echo=(ENVIRONMENT == "development"),
    pool_pre_ping=True,
    pool_recycle=1800,
)

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