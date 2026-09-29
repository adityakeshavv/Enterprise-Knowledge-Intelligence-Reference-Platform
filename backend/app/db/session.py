import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Tuple
import sqlglot
from sqlglot import exp
from app.core.config import settings
from app.core.logging import logger

class SafeDatabaseManager:
    """Safe read-only database query execution manager with AST validation."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def validate_sql_readonly(self, query: str) -> Tuple[bool, str]:
        """Strict AST parsing using sqlglot to ensure ONLY SELECT statements are permitted."""
        try:
            parsed = sqlglot.parse_one(query)
            if not isinstance(parsed, exp.Select):
                return False, f"Blocked: Only SELECT statements are permitted. Detected statement type: {parsed.__class__.__name__}"
            
            # Check for forbidden mutations
            forbidden_expressions = (
                exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, 
                exp.Alter, exp.Command
            )
            for node in parsed.walk():
                if isinstance(node, forbidden_expressions):
                    return False, f"Blocked: Disallowed SQL mutation expression detected: {node.__class__.__name__}"
                    
            return True, "Valid SELECT query"
        except Exception as e:
            return False, f"SQL Syntax Validation Failed: {str(e)}"

    def execute_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Executes validated SELECT query against database and returns rows and columns."""
        is_valid, msg = self.validate_sql_readonly(query)
        if not is_valid:
            return {
                "success": False,
                "error": msg,
                "columns": [],
                "rows": [],
                "row_count": 0
            }

        try:
            # Enforce read-only SQLite URI mode
            uri = f"file:{self.db_path.as_posix()}?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=5.0)
            cursor = conn.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchmany(limit)
            conn.close()
            
            return {
                "success": True,
                "columns": columns,
                "rows": [list(r) for r in rows],
                "row_count": len(rows),
                "error": None
            }
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return {
                "success": False,
                "error": str(e),
                "columns": [],
                "rows": [],
                "row_count": 0
            }

# Default manufacturing DB instance
mfg_db_path = settings.ROOT_DIR / "data" / "manufacturing" / "manufacturing.db"
db_manager = SafeDatabaseManager(mfg_db_path)
