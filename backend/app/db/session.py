import os
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings, BASE_DIR

_is_db_initialized = False

# Handle SQLite connect_args for thread safety if using SQLite
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 30}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def ensure_database_initialized():
    global _is_db_initialized
    if _is_db_initialized:
        return

    # 1. If using SQLite, check if file exists or needs to be copied from pre-seeded asset
    if settings.DATABASE_URL.startswith("sqlite:///"):
        raw_path = settings.DATABASE_URL.replace("sqlite:///", "")
        db_path = Path(raw_path)
        
        needs_seed_copy = not db_path.exists() or (db_path.exists() and db_path.stat().st_size < 1024)
        if needs_seed_copy:
            candidates = [
                BASE_DIR / "nebula9_reference.db",
                BASE_DIR.parent / "nebula9_reference.db",
                Path.cwd() / "backend" / "nebula9_reference.db",
                Path.cwd() / "nebula9_reference.db",
                Path(__file__).resolve().parent.parent.parent / "nebula9_reference.db",
                Path(__file__).resolve().parent.parent.parent.parent / "nebula9_reference.db",
            ]
            source_found = None
            for cand in candidates:
                try:
                    if cand.resolve() != db_path.resolve() and cand.exists() and cand.stat().st_size > 1024:
                        source_found = cand
                        break
                except Exception:
                    continue
            
            if source_found:
                try:
                    db_path.parent.mkdir(parents=True, exist_ok=True)
                    if db_path.exists():
                        try:
                            db_path.unlink()
                        except Exception:
                            pass
                    shutil.copy2(str(source_found), str(db_path))
                    print(f"[{settings.APP_NAME}] Copied pre-seeded database from {source_found} to {db_path} ({db_path.stat().st_size} bytes)")
                except Exception as copy_err:
                    print(f"[{settings.APP_NAME}] Warning copying database: {copy_err}")

    # 2. Verify schema and default personas
    try:
        from app.db.seeder import seed_database
        from app.db.models import User
        
        db = SessionLocal()
        try:
            user_count = db.query(User).count()
            if user_count == 0:
                print(f"[{settings.APP_NAME}] Users table empty. Running seed_database()...")
                seed_database()
            _is_db_initialized = True
        except Exception as query_err:
            print(f"[{settings.APP_NAME}] Table query error ({query_err}). Running seed_database()...")
            seed_database()
            _is_db_initialized = True
        finally:
            db.close()
    except Exception as e:
        print(f"[{settings.APP_NAME}] Error verifying database initialization: {e}")

# Execute eager initialization at module load
try:
    ensure_database_initialized()
except Exception as init_err:
    print(f"[{settings.APP_NAME}] Eager DB initialization error: {init_err}")

def get_db():
    if not _is_db_initialized:
        ensure_database_initialized()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
