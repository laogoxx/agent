import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import logging
logger = logging.getLogger(__name__)

MAX_RETRY_TIME = 20  # 连接最大重试时间（秒）
# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def get_db_url() -> str:
    """Build database URL from environment."""
    # 优先使用 Render 的 DATABASE_URL 环境变量
    url = os.getenv("DATABASE_URL") or os.getenv("PGDATABASE_URL") or ""

    if url:
        return url

    # 如果没有环境变量，尝试从其他来源获取（可选）
    logger.error("DATABASE_URL or PGDATABASE_URL is not set")
    raise ValueError("DATABASE_URL or PGDATABASE_URL is not set")
_engine = None
_SessionLocal = None

def get_db_url() -> str:
    """Build database URL from environment."""
    # 优先使用 Render 的 DATABASE_URL 环境变量
    url = os.getenv("DATABASE_URL") or os.getenv("PGDATABASE_URL") or ""

    # 添加调试日志
    logger.info(f"DATABASE_URL env: {'Set' if os.getenv('DATABASE_URL') else 'Not set'}")
    logger.info(f"PGDATABASE_URL env: {'Set' if os.getenv('PGDATABASE_URL') else 'Not set'}")
    logger.info(f"Retrieved URL (first 50 chars): {url[:50] if url else 'Empty'}")

    if url:
        return url

    # 如果没有环境变量，尝试从其他来源获取（可选）
    logger.error("DATABASE_URL or PGDATABASE_URL is not set")
    raise ValueError("DATABASE_URL or PGDATABASE_URL is not set")
        _engine = _create_engine_with_retry()
    return _engine

def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def get_session():
    return get_sessionmaker()()

__all__ = [
    "get_db_url",
    "get_engine",
    "get_sessionmaker",
    "get_session",
]
