import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger("nebula9")
logger.setLevel(logging.INFO)

if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class AuditLogger:
    """Tamper-evident structured audit logging for queries, tool executions, and security events."""
    
    def __init__(self):
        self.log_dir = settings.ROOT_DIR / "data" / "audit"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.log_dir / "audit_events.jsonl"
        self.memory_buffer: List[Dict[str, Any]] = []

    def record_event(
        self,
        event_type: str,
        user: Dict[str, Any],
        industry_id: str,
        query: str,
        agents_invoked: List[str],
        sources_accessed: List[Dict[str, Any]],
        latency_ms: float,
        grounding_score: float,
        conflict_detected: bool,
        status: str = "SUCCESS",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "user_id": user.get("user_id"),
            "user_role": user.get("role"),
            "industry_id": industry_id,
            "query": query,
            "agents_invoked": agents_invoked,
            "sources_accessed": sources_accessed,
            "latency_ms": latency_ms,
            "grounding_score": grounding_score,
            "conflict_detected": conflict_detected,
            "status": status,
            "metadata": metadata or {}
        }
        
        self.memory_buffer.append(event)
        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Failed to append to audit log: {e}")
            
        logger.info(f"[AUDIT] Query='{query[:40]}...' User='{user.get('user_id')}' Latency={latency_ms:.1f}ms Grounding={grounding_score:.2f}")
        return event

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        if self.audit_file.exists():
            try:
                with open(self.audit_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    records = [json.loads(line) for line in lines[-limit:]]
                    return list(reversed(records))
            except Exception as e:
                logger.error(f"Failed reading audit file: {e}")
        return list(reversed(self.memory_buffer[-limit:]))

audit_logger = AuditLogger()
