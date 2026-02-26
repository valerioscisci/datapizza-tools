from __future__ import annotations

import shutil
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os


def _resolve_database_url() -> str:
    """Resolve the database URL, handling Vercel's read-only filesystem."""
    url = os.getenv("DATABASE_URL")

    # If a SQLite URL is provided, ensure it points to a writable location
    if url and "sqlite" in url:
        # Extract the DB file path from the SQLite URL
        db_path = url.replace("sqlite:///", "")
        if db_path.startswith("./"):
            db_path = os.path.join(os.getcwd(), db_path[2:])
        abs_path = Path(db_path).resolve()

        if abs_path.exists():
            # Test if the directory is writable
            try:
                test_file = abs_path.parent / ".db_write_test"
                test_file.touch()
                test_file.unlink()
                return url  # Directory is writable, use as-is
            except OSError:
                # Read-only filesystem — copy to /tmp
                tmp_db = "/tmp/datapizza.db"
                if not os.path.exists(tmp_db):
                    shutil.copy2(str(abs_path), tmp_db)
                return f"sqlite:///{tmp_db}"
        return url

    if url:
        return url

    # Check for bundled DB relative to this package
    bundled = Path(__file__).resolve().parent.parent.parent / "datapizza.db"

    if bundled.exists():
        tmp_db = "/tmp/datapizza.db"
        if not os.path.exists(tmp_db):
            shutil.copy2(str(bundled), tmp_db)
        if os.path.exists(tmp_db):
            return f"sqlite:///{tmp_db}"
        return f"sqlite:///{bundled}"

    return "sqlite:///./datapizza.db"


DATABASE_URL = _resolve_database_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
