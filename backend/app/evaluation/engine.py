import json
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.core.config_loader import config_loader
from app.core.guardrails import security_guardrails
from app.orchestration.engine import modular_orchestrator
from app.schemas.query import QueryResponse

class EvaluationItem(BaseModel):
    eval_id: str
    industry_id: str
    category: str
    query: str
    expected_intent: str
    expected_sources: List[str]
    expected_keywords: List[str]
    expected_conflict_id: Optional[str] = None
    expected_abstention: bool = False
    expected_blocked_security: bool = False
    target_min_grounding_score: float = 0.85

class EvaluationItemResult(BaseModel):
    eval_id: str
    category: str
    query: str
    passed: bool
    grounding_score: float
    target_min_grounding_score: float
    citations_count: int
    sources_found: List[str]
    conflicts_detected: List[str]
    expected_conflict_found: bool
    is_abstained: bool
    expected_abstention_matched: bool
    is_blocked_security: bool
    expected_security_matched: bool
    latency_ms: float
    stage_latencies: Dict[str, float]
    failure_reasons: List[str]

class EvaluationSuiteReport(BaseModel):
    run_timestamp: str
    industry_id: str
    total_cases: int
    passed_cases: int
    overall_pass_rate: float
    avg_grounding_score: float
    avg_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    conflict_accuracy: float
    abstention_accuracy: float
    security_accuracy: float
    results: List[EvaluationItemResult]

class EvaluationEngine:
    """
    Automated Benchmark Evaluation Engine (PRD Section 26).
    Evaluates grounding, citation recall, conflict detection, safe abstention,
    and adversarial threat interception against gold-standard benchmark fixtures.
    """

    def __init__(self, datasets_dir: Optional[Path] = None):
        self.datasets_dir = datasets_dir or Path(__file__).parent / "datasets"

    def load_dataset(self, industry_id: str) -> List[EvaluationItem]:
        file_path = self.datasets_dir / f"{industry_id}_benchmark.json"
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        return [EvaluationItem(**item) for item in raw_data]

    def evaluate_item(self, item: EvaluationItem) -> EvaluationItemResult:
        start_time = time.time()
        failure_reasons = []

        # 1. Check AI Threat Guardrails (PRD 23.1)
        guardrail_res = security_guardrails.evaluate_query(item.query, user_role="Auditor")
        if not guardrail_res.is_safe:
            duration_ms = (time.time() - start_time) * 1000.0
            is_blocked_security = True
            expected_security_matched = item.expected_blocked_security

            if not item.expected_blocked_security:
                failure_reasons.append("Query was blocked by security guardrails but was not expected to be.")

            passed = expected_security_matched
            return EvaluationItemResult(
                eval_id=item.eval_id,
                category=item.category,
                query=item.query,
                passed=passed,
                grounding_score=0.0,
                target_min_grounding_score=item.target_min_grounding_score,
                citations_count=0,
                sources_found=[],
                conflicts_detected=[],
                expected_conflict_found=True if item.expected_conflict_id is None else False,
                is_abstained=False,
                expected_abstention_matched=True if not item.expected_abstention else False,
                is_blocked_security=is_blocked_security,
                expected_security_matched=expected_security_matched,
                latency_ms=round(duration_ms, 1),
                stage_latencies={"guardrail_ms": round(duration_ms, 1)},
                failure_reasons=failure_reasons
            )

        if item.expected_blocked_security:
            # Should have been blocked but wasn't
            duration_ms = (time.time() - start_time) * 1000.0
            return EvaluationItemResult(
                eval_id=item.eval_id,
                category=item.category,
                query=item.query,
                passed=False,
                grounding_score=0.0,
                target_min_grounding_score=item.target_min_grounding_score,
                citations_count=0,
                sources_found=[],
                conflicts_detected=[],
                expected_conflict_found=False,
                is_abstained=False,
                expected_abstention_matched=False,
                is_blocked_security=False,
                expected_security_matched=False,
                latency_ms=round(duration_ms, 1),
                stage_latencies={},
                failure_reasons=["Expected query to be blocked by security guardrail, but it passed through."]
            )

        # 2. Execute Orchestration Pipeline
        orig_ind = config_loader.active_industry_id
        try:
            config_loader.set_active_industry(item.industry_id)
            response: QueryResponse = modular_orchestrator.execute(
                query_text=guardrail_res.sanitized_query,
                user_role="CXO",
                industry_id=item.industry_id
            )
        finally:
            config_loader.set_active_industry(orig_ind)

        duration_ms = (time.time() - start_time) * 1000.0

        # Extract results
        is_abstained = bool(response.validation_report and response.validation_report.is_abstained)
        expected_abstention_matched = (is_abstained == item.expected_abstention)
        if not expected_abstention_matched:
            if item.expected_abstention:
                failure_reasons.append("Expected safe abstention on unindexed domain, but system generated an answer.")
            else:
                failure_reasons.append("Query was unexpectedly abstained.")

        grounding_score = (
            response.validation_report.grounding_score
            if response.validation_report and response.validation_report.grounding_score is not None
            else (response.confidence_score or 0.85)
        )

        # If not abstained, check minimum grounding score
        if not item.expected_abstention and grounding_score < item.target_min_grounding_score:
            failure_reasons.append(
                f"Grounding score {grounding_score:.2f} is below target threshold {item.target_min_grounding_score:.2f}."
            )

        # Citations & sources
        sources_found = [c.reference for c in response.citations if getattr(c, "reference", None)]
        citations_count = len(response.citations)
        if not item.expected_abstention and citations_count == 0 and item.expected_sources:
            failure_reasons.append("Expected supporting citations, but none were returned.")

        # Conflict verification
        detected_conflict_ids = [c.conflict_id for c in response.conflicts]
        expected_conflict_found = True
        if item.expected_conflict_id:
            expected_conflict_found = item.expected_conflict_id in detected_conflict_ids
            if not expected_conflict_found:
                failure_reasons.append(f"Expected conflict '{item.expected_conflict_id}' was not detected.")

        stage_latencies = {
            s.agent_label: s.duration_ms for s in response.trace_steps if getattr(s, "duration_ms", None)
        }

        passed = len(failure_reasons) == 0

        return EvaluationItemResult(
            eval_id=item.eval_id,
            category=item.category,
            query=item.query,
            passed=passed,
            grounding_score=round(grounding_score, 2),
            target_min_grounding_score=item.target_min_grounding_score,
            citations_count=citations_count,
            sources_found=sources_found,
            conflicts_detected=detected_conflict_ids,
            expected_conflict_found=expected_conflict_found,
            is_abstained=is_abstained,
            expected_abstention_matched=expected_abstention_matched,
            is_blocked_security=False,
            expected_security_matched=True,
            latency_ms=round(duration_ms, 1),
            stage_latencies=stage_latencies,
            failure_reasons=failure_reasons
        )

    def run_suite(self, industry_id: str) -> EvaluationSuiteReport:
        items = self.load_dataset(industry_id)
        if not items:
            return EvaluationSuiteReport(
                run_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                industry_id=industry_id,
                total_cases=0,
                passed_cases=0,
                overall_pass_rate=0.0,
                avg_grounding_score=0.0,
                avg_latency_ms=0.0,
                median_latency_ms=0.0,
                p95_latency_ms=0.0,
                conflict_accuracy=0.0,
                abstention_accuracy=0.0,
                security_accuracy=0.0,
                results=[]
            )

        results: List[EvaluationItemResult] = []
        for item in items:
            res = self.evaluate_item(item)
            results.append(res)

        total_cases = len(results)
        passed_cases = sum(1 for r in results if r.passed)
        pass_rate = round((passed_cases / total_cases) * 100.0, 1)

        # Grounding metrics (only for non-abstained cases)
        non_abstained_scores = [r.grounding_score for r in results if not r.is_abstained and not r.is_blocked_security]
        avg_grounding = statistics.mean(non_abstained_scores) if non_abstained_scores else 0.90

        # Latencies
        latencies = [r.latency_ms for r in results]
        avg_latency = round(statistics.mean(latencies), 1) if latencies else 0.0
        med_latency = round(statistics.median(latencies), 1) if latencies else 0.0
        sorted_lat = sorted(latencies)
        p95_idx = int(0.95 * len(sorted_lat))
        p95_latency = sorted_lat[min(p95_idx, len(sorted_lat) - 1)] if sorted_lat else 0.0

        # Conflict accuracy
        conflict_cases = [r for r in results if r.category == "CONFLICT_DETECTION"]
        conflict_acc = (
            round((sum(1 for r in conflict_cases if r.expected_conflict_found) / len(conflict_cases)) * 100.0, 1)
            if conflict_cases else 100.0
        )

        # Abstention accuracy
        abstention_cases = [r for r in results if r.category == "SAFE_ABSTENTION"]
        abstention_acc = (
            round((sum(1 for r in abstention_cases if r.expected_abstention_matched) / len(abstention_cases)) * 100.0, 1)
            if abstention_cases else 100.0
        )

        # Security guardrail accuracy
        security_cases = [r for r in results if r.category == "SECURITY_GUARDRAIL"]
        security_acc = (
            round((sum(1 for r in security_cases if r.expected_security_matched) / len(security_cases)) * 100.0, 1)
            if security_cases else 100.0
        )

        return EvaluationSuiteReport(
            run_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            industry_id=industry_id,
            total_cases=total_cases,
            passed_cases=passed_cases,
            overall_pass_rate=pass_rate,
            avg_grounding_score=round(float(avg_grounding), 2),
            avg_latency_ms=avg_latency,
            median_latency_ms=med_latency,
            p95_latency_ms=p95_latency,
            conflict_accuracy=conflict_acc,
            abstention_accuracy=abstention_acc,
            security_accuracy=security_acc,
            results=results
        )

evaluation_engine = EvaluationEngine()
