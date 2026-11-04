import sys
import os
from pathlib import Path

# Add backend directory to sys.path so app imports work
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

# In serverless/Vercel environments, ensure writable database in /tmp
if os.environ.get("VERCEL"):
    import shutil
    tmp_db = Path("/tmp/nebula9_reference.db")
    src_db = ROOT_DIR / "nebula9_reference.db"
    if not tmp_db.exists() and src_db.exists():
        try:
            shutil.copy2(src_db, tmp_db)
        except Exception:
            pass
    os.environ.setdefault("DATABASE_URL", f"sqlite:////tmp/nebula9_reference.db")

from app.main import app