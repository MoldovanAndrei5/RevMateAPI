from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from utils.logger import get_logger


logger = get_logger(__name__)
load_dotenv(override=False)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

logger.info(f"[DB CONFIG] Host: {DB_HOST}, Port: {DB_PORT}, DB: {DB_NAME}, User: {DB_USERNAME}")

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0
    )
    logger.info("DB engine created successfully")
except Exception as e:
    logger.error(f"Failed to create DB engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    logger.info("Opening DB session")
    db = SessionLocal()
    try:
        yield db
        logger.info("DB session used successfully")
    except Exception as e:
        logger.error(f"DB session error: {e}")
        raise
    finally:
        db.close()
        logger.info("DB session closed")