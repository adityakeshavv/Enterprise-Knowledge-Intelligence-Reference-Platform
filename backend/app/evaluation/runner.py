import argparse
import json
from pathlib import Path
from typing import Dict, Any, List
from app.evaluation.engine import evaluation_engine, EvaluationSuiteReport

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent

def run_evaluation_suite(industry_id: str = "all") -> Dict[str, EvaluationSuiteReport]:
    """Runs benchmark evaluation and writes reports to disk."""
    industries = ["manufacturing", "pharma"] if industry_id == "all" else [industry_id]
    reports = {}

    for ind in industries:
        print(f"\n[EvaluationRunner] Running benchmark suite for industry: '{ind}'...")
        report = evaluation_engine.run_suite(ind)
        reports[ind] = report
        print(
            f"[EvaluationRunner] Completed {report.total_cases} tests for '{ind}': "
            f"Pass Rate = {report.overall_pass_rate}%, Avg Grounding = {report.avg_grounding_score}, "
            f"Median Latency = {report.median_latency_ms} ms, Conflict Acc = {report.conflict_accuracy}%, "
            f"Abstention Acc = {report.abstention_accuracy}%, Security Acc = {report.security_accuracy}%"
        )

    # Save JSON report
    json_path = REPORTS_DIR / "evaluation_report.json"
    serializable = {
        k: v.model_dump() for k, v in reports.items()
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)
    print(f"\n[EvaluationRunner] Saved machine-readable report to: {json_path}")

    # Generate Markdown Report
    md_content = generate_markdown_report(reports)
    md_path = REPORTS_DIR / "evaluation_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[EvaluationRunner] Saved Markdown report to: {md_path}")

    return reports

def generate_markdown_report(reports: Dict[str, EvaluationSuiteReport]) -> str:
    lines = [
        "# Nebula9 Enterprise Knowledge Intelligence - Quantitative Evaluation Report",
        "",
        "> **PRD Section 26 Quality Benchmark**: Automated evaluation of multi-agent orchestration, "
        "evidence grounding, conflict detection, safe abstention, and adversarial threat defense.",
        "",
        "## 1. Executive Summary Table",
        "",
        "| Industry Pack | Cases Evaluated | Pass Rate (%) | Avg Grounding | Median Latency | Conflict Acc | Abstention Acc | Security Acc |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    ]

    for ind, rep in reports.items():
        lines.append(
            f"| **{ind.title()}** | {rep.total_cases} | **{rep.overall_pass_rate}%** | "
            f"{(rep.avg_grounding_score * 100):.0f}% | {rep.median_latency_ms:.0f} ms | "
            f"{rep.conflict_accuracy:.0f}% | {rep.abstention_accuracy:.0f}% | {rep.security_accuracy:.0f}% |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 2. Detailed Breakdown by Benchmark Case",
        ""
    ])

    for ind, rep in reports.items():
        lines.append(f"### {ind.title()} Benchmark ({rep.passed_cases}/{rep.total_cases} Passed)")
        lines.append("")
        lines.append("| ID | Category | Query | Status | Grounding | Latency | Key Validation |")
        lines.append("| :--- | :--- | :--- | :---: | :---: | :---: | :--- |")

        for r in rep.results:
            status_badge = "✅ PASS" if r.passed else "❌ FAIL"
            notes = "Valid" if r.passed else "; ".join(r.failure_reasons)
            lines.append(
                f"| `{r.eval_id}` | `{r.category}` | {r.query[:48]}... | {status_badge} | "
                f"{(r.grounding_score * 100):.0f}% | {r.latency_ms:.0f} ms | {notes[:40]} |"
            )
        lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Nebula9 Enterprise Evaluation Suite")
    parser.add_argument("--industry", default="all", choices=["manufacturing", "pharma", "all"])
    args = parser.parse_args()
    run_evaluation_suite(args.industry)
