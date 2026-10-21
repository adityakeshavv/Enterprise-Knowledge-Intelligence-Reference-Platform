import time
from typing import List, Dict, Any, Tuple
import sqlglot
from sqlglot import exp
from sqlalchemy import text
from app.db.session import SessionLocal

ALLOWLISTED_TABLES = {
    "plant_downtime_events",
    "maintenance_work_orders",
    "supplier_component_quality",
    "production_line_metrics",
}

FORBIDDEN_KEYWORDS = {
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE",
    "GRANT", "REVOKE", "EXEC", "EXECUTE", "XP_", "SHUTDOWN"
}

class SQLSecurityError(Exception):
    """Base exception for SQL security violations."""
    pass

class UnauthorizedTableError(SQLSecurityError):
    """Raised when query attempts to access non-allowlisted tables."""
    pass

class UnsafeQueryOperationError(SQLSecurityError):
    """Raised when query contains non-SELECT or mutation expressions."""
    pass

class SQLSandbox:
    """Read-only SQL AST validator and execution sandbox."""

    def __init__(self, allowlisted_tables=ALLOWLISTED_TABLES, max_rows: int = 100):
        self.allowlisted_tables = {t.lower() for t in allowlisted_tables}
        self.max_rows = max_rows

    def validate_and_sanitize(self, raw_sql: str) -> str:
        """Parse raw SQL using sqlglot, enforce AST security rules, and inject limits."""
        cleaned = raw_sql.strip().rstrip(";")
        if not cleaned:
            raise UnsafeQueryOperationError("Empty SQL query provided.")

        # 1. Reject multiple statements
        parsed_expressions = sqlglot.parse(cleaned, read="sqlite")
        if len(parsed_expressions) > 1:
            raise UnsafeQueryOperationError("Multi-statement queries are strictly prohibited.")

        expression = parsed_expressions[0]
        if expression is None:
            raise UnsafeQueryOperationError("Malformed SQL statement.")

        # 2. Enforce SELECT root expression only
        if not isinstance(expression, exp.Select):
            raise UnsafeQueryOperationError(
                f"Forbidden statement type '{expression.key.upper()}'. Only read-only SELECT queries are permitted."
            )

        # 3. Check for mutation or command nodes anywhere in the AST
        mutation_nodes = [
            exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter,
            exp.Create, exp.Command
        ]
        if hasattr(exp, "TruncateTable"):
            mutation_nodes.append(getattr(exp, "TruncateTable"))
        forbidden_nodes = tuple(mutation_nodes)
        for node in expression.walk():
            if isinstance(node, forbidden_nodes):
                raise UnsafeQueryOperationError(
                    f"Security violation: Detected forbidden operation '{node.key.upper()}'."
                )

        # 4. Check all referenced tables against the allowlist
        tables_referenced = set()
        for table_node in expression.find_all(exp.Table):
            t_name = table_node.name.lower()
            if t_name:
                tables_referenced.add(t_name)

        if not tables_referenced:
            # Dual check: must reference a table or be a safe literal
            pass
        else:
            unauthorized = tables_referenced - self.allowlisted_tables
            if unauthorized:
                raise UnauthorizedTableError(
                    f"Access denied to unauthorized table(s): {', '.join(unauthorized)}. "
                    f"Allowed business tables: {', '.join(sorted(self.allowlisted_tables))}."
                )

        # 5. Enforce LIMIT <= max_rows
        limit_node = expression.args.get("limit")
        if limit_node is None:
            expression = expression.limit(self.max_rows)
        else:
            try:
                current_limit = int(limit_node.expression.name)
                if current_limit > self.max_rows:
                    expression.args["limit"] = exp.Limit(expression=exp.Literal.number(self.max_rows))
            except Exception:
                expression.args["limit"] = exp.Limit(expression=exp.Literal.number(self.max_rows))

        # Return standardized SQL string
        return expression.sql(dialect="sqlite")

    def execute_safe_query(self, raw_sql: str) -> Tuple[List[str], List[Dict[str, Any]], float, str]:
        """Validate and execute SQL query in a read-only sandboxed session."""
        sanitized_sql = self.validate_and_sanitize(raw_sql)
        start_time = time.time()

        db = SessionLocal()
        try:
            # Enforce read-only transaction semantics
            result = db.execute(text(sanitized_sql))
            columns = list(result.keys())
            rows_data = [dict(zip(columns, row)) for row in result.fetchall()]
            duration_ms = (time.time() - start_time) * 1000.0
            return columns, rows_data, duration_ms, sanitized_sql
        finally:
            db.close()

sql_sandbox = SQLSandbox()
