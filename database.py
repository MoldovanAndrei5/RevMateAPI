from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"[DB CONFIG] Host: {DB_HOST}, Port: {DB_PORT}, DB: {DB_NAME}, User: {DB_USERNAME}")
print(f"[DB URL] {SQLALCHEMY_DATABASE_URL}")

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0
    )
    print("[DB ENGINE] Engine created successfully")
except Exception as e:
    print(f"[DB ENGINE ERROR] Failed to create engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("[SESSION] SessionLocal configured")

Base = declarative_base()
print("[BASE] Declarative base initialized")


def get_db():
    print("[DB SESSION] Opening new database session")
    db = SessionLocal()
    try:
        yield db
        print("[DB SESSION] Session used successfully")
    except Exception as e:
        print(f"[DB SESSION ERROR] {e}")
        raise
    finally:
        db.close()
        print("[DB SESSION] Session closed")