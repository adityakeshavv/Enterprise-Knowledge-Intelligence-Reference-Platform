import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

def generate_flowchart():
    # Dimensions and high resolution
    fig, ax = plt.subplots(figsize=(26, 20), dpi=200)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 2600)
    ax.set_ylim(0, 2000)
    ax.axis('off')

    # Color Palette
    BG_CARD = '#161F30'
    BORDER_CARD = '#2A3B53'
    TEXT_TITLE = '#F8FAFC'
    TEXT_MUTED = '#94A3B8'
    TEXT_CODE = '#38BDF8'
    ACCENT_CYAN = '#0EA5E9'
    ACCENT_INDIGO = '#6366F1'
    ACCENT_EMERALD = '#10B981'
    ACCENT_AMBER = '#F59E0B'
    ACCENT_ROSE = '#F43F5E'
    ACCENT_PURPLE = '#A855F7'

    # Title & Subtitle Banner
    ax.text(1300, 1940, "Nebula9 Enterprise Knowledge Intelligence", 
            ha='center', va='center', fontsize=26, fontweight='bold', color=TEXT_TITLE, fontfamily='sans-serif')
    ax.text(1300, 1905, "End-to-End Modular Agent Orchestration Flowchart • Tool Invocations & Artifact Contributions", 
            ha='center', va='center', fontsize=15, color=ACCENT_CYAN, fontfamily='sans-serif')
    
    # Header Columns Bar
    col_y = 1845
    headers = [
        ("STAGE & SPECIALIZED AGENT", 380, ACCENT_CYAN),
        ("TOOLS & ADAPTERS INVOKED", 1120, ACCENT_INDIGO),
        ("DATA CONTRACT & STAGE OUTPUT CONTRIBUTION", 1950, ACCENT_EMERALD)
    ]
    for title, x_pos, col in headers:
        rect = patches.FancyBboxPatch((x_pos - 320, col_y - 25), 640, 42,
                                     boxstyle="round,pad=0.2", facecolor='#1E293B',
                                     edgecolor=col, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x_pos, col_y - 4, title, ha='center', va='center', fontsize=12, fontweight='bold', color=col)

    # Stages Data: (Stage Num, Agent Name, Badge Color, Tools List, Outputs List, Y-center)
    stages = [
        {
            "num": "STAGE 1",
            "name": "Query Understanding Agent",
            "class": "QueryUnderstandingAgent",
            "color": ACCENT_CYAN,
            "y": 1720,
            "tools": [
                "• Entity Regex Pattern Matchers (Plant, Line, Error Code, Part #)",
                "• Time-Range & Period Parser (e.g., 'March 10', 'Q1')",
                "• Semantic Normalizer (Colloquial term standardizer)",
                "• Ambiguity & Missing Scope Detector"
            ],
            "outputs": [
                "• QueryUnderstandingResult (Typed Contract)",
                "• Normalized query: 'Line 3 Plant A downtime root causes'",
                "• Extracted entities: {'plant_id': 'Plant A', 'line_id': 'Line 3'}",
                "• Ambiguity & Clarification status (False / True)"
            ]
        },
        {
            "num": "STAGE 2",
            "name": "Intent Classification Agent",
            "class": "IntentClassificationAgent",
            "color": ACCENT_INDIGO,
            "y": 1550,
            "tools": [
                "• Configurable IntentTaxonomy (Signal regex & keyword sets)",
                "• Multi-Intent Density Evaluator",
                "• Confidence & Uncertainty Scoring Engine",
                "• Fallback Mechanism (Gate threshold: < 0.55)"
            ],
            "outputs": [
                "• IntentClassificationResult (Typed Contract)",
                "• Predicted intent: CROSS_SOURCE_INVESTIGATION",
                "• Target sources: ['SQL_DATABASE', 'DOCUMENT_STORE']",
                "• Confidence score: 0.92 | Strategy: PARALLEL"
            ]
        },
        {
            "num": "STAGE 3",
            "name": "Query Routing Agent",
            "class": "QueryRoutingAgent",
            "color": ACCENT_PURPLE,
            "y": 1380,
            "tools": [
                "• AgentRegistry Manifest Resolver (Dynamic capability lookup)",
                "• Role-Based Access Control Validator (validate_authorization)",
                "• Workflow Dispatcher (Single-agent vs Parallel multi-agent)"
            ],
            "outputs": [
                "• RoutingDecision (Typed Contract)",
                "• Selected: ['structured_document_agent', 'unstructured_document_agent']",
                "• Skipped: [] | Execution Mode: PARALLEL",
                "• Security check: CXO role validated for all sources"
            ]
        },
        {
            "num": "STAGE 4",
            "name": "Investigation Planning Agent",
            "class": "InvestigationPlanningAgent",
            "color": ACCENT_AMBER,
            "y": 1210,
            "tools": [
                "• DAG Task Graph Generator",
                "• Sub-Question Decomposer & Dependency Resolver",
                "• Completion Criteria & Fallback Policy Builder"
            ],
            "outputs": [
                "• InvestigationPlan (Typed Contract with task graph)",
                "• Task 1: task_structured_retrieval (SQL_DATABASE)",
                "• Task 2: task_unstructured_retrieval (DOCUMENT_STORE)",
                "• Strict completion criteria & fallback policies defined"
            ]
        },
        {
            "num": "STAGE 5 & 6",
            "name": "Parallel Investigation Agents",
            "class": "StructuredDocumentAgent & UnstructuredDocumentAgent",
            "color": ACCENT_EMERALD,
            "y": 1000,
            "tools": [
                "• Structured: Safe SQL Sandbox, AST Parser (sqlglot), Allowlist Validator",
                "• Structured: Read-only SQLite/PostgreSQL Engine, Row Formatter",
                "• Unstructured: BM25Okapi Lexical Index + Dense Semantic Retriever",
                "• Unstructured: Defensive XML Bounding Fence (<retrieved_evidence>)"
            ],
            "outputs": [
                "• StructuredRetrievalResult: 1,080 mins downtime on Line 3 [SQL-01]",
                "• UnstructuredRetrievalResult: SOP Part AFD-SEAL-882 & 250 hr cycle",
                "• CitationItem records with page #, line #, cell ranges",
                "• 0 SQL injection risks, 0 prompt injection overrides"
            ]
        },
        {
            "num": "STAGE 7",
            "name": "Evidence & Detail Extraction Agent",
            "class": "EvidenceExtractionAgent",
            "color": ACCENT_CYAN,
            "y": 790,
            "tools": [
                "• Empirical Fact & Metric Normalizer (minutes, hours, PPM, bar)",
                "• Timestamp & Period Correlator",
                "• Temporal Conflict Detection Engine (CONF-01 / CONF-02 rules)",
                "• Fact vs. Analytical Inference Classifier"
            ],
            "outputs": [
                "• List[ExtractedEvidenceItem] (Typed empirical facts)",
                "• Conflict CONF-01: Shift log completed Mar 10 vs Telemetry event Mar 14",
                "• Verified Facts count: 4 | Inferences count: 1",
                "• All metrics tagged with units, timestamps, and source locations"
            ]
        },
        {
            "num": "STAGE 8",
            "name": "Summarizer Agent",
            "class": "SummarizerAgent (SynthesisAgent)",
            "color": ACCENT_INDIGO,
            "y": 590,
            "tools": [
                "• Ground-Truth Briefing Engine (Zero-speculation rule)",
                "• Dynamic KPI Metric Card Synthesizer",
                "• Auditable Inline Citation Anchorer ([SQL-01], [DOC-01])",
                "• Format Adapter (Factual Brief, SOP Guide, Supplier Audit)"
            ],
            "outputs": [
                "• SummarizationResult (Executive briefing markdown)",
                "• Dynamic KPI Cards: Total Downtime, Hydraulic Cavitation, OEE",
                "• Operational Conflict Notice with resolution recommendations",
                "• 100% claim-to-citation anchoring"
            ]
        },
        {
            "num": "STAGE 9",
            "name": "Traceability & Audit Agent",
            "class": "TraceabilityAuditAgent (ExecutionTracer)",
            "color": ACCENT_ROSE,
            "y": 380,
            "tools": [
                "• Cross-Cutting ExecutionTracer (Lifecycle telemetry recorder)",
                "• Evidence Lineage Mapper (Claims -> Evidence Items -> Sources)",
                "• Citation Integrity Auditor (Anti-hallucination verification)",
                "• Knowledge Boundary & Safe Abstention Evaluator"
            ],
            "outputs": [
                "• ExecutionTraceRecord & TraceValidationReport",
                "• Completeness score: 100% | Citations verified: True",
                "• Verified lineage graph for all empirical claims",
                "• Write-ahead immutable database AuditLog record"
            ]
        },
        {
            "num": "DELIVERY",
            "name": "Unified Output & Visualization",
            "class": "QueryResponse & EvidenceGraphView",
            "color": ACCENT_EMERALD,
            "y": 180,
            "tools": [
                "• Interactive EvidenceGraphBuilder (2D topology compiler)",
                "• SSE Async Event Streamer (Real-time trace step emitter)",
                "• Tri-Mode Frontend Switcher (Brief / Graph / Full Trace)"
            ],
            "outputs": [
                "• QueryResponse: Executive Summary + Findings + KPI Metrics",
                "• Interactive Evidence Graph: Grounding, Contradictions, Lineage",
                "• Real-time SSE Trace Steps streamed to executive interface"
            ]
        }
    ]

    # Draw Stage Rows and Content
    for i, s in enumerate(stages):
        y = s["y"]
        color = s["color"]

        # 1. Agent Box (Col 1)
        w1, h1 = 660, 125
        card1 = patches.FancyBboxPatch((70, y - h1/2), w1, h1,
                                      boxstyle="round,pad=0.3", facecolor=BG_CARD,
                                      edgecolor=color, linewidth=2.0)
        ax.add_patch(card1)
        
        # Stage Badge
        badge = patches.FancyBboxPatch((90, y + h1/2 - 28), 95, 20,
                                      boxstyle="round,pad=0.2", facecolor=color,
                                      edgecolor='none')
        ax.add_patch(badge)
        ax.text(137, y + h1/2 - 18, s["num"], ha='center', va='center', fontsize=9, fontweight='bold', color='#0B0F19')
        
        # Agent Name & Class
        ax.text(90, y + 8, s["name"], fontsize=13, fontweight='bold', color=TEXT_TITLE)
        ax.text(90, y - 18, s["class"], fontsize=10, color=color, fontfamily='monospace')

        # 2. Tools Box (Col 2)
        w2, h2 = 820, 125
        card2 = patches.FancyBboxPatch((770, y - h2/2), w2, h2,
                                      boxstyle="round,pad=0.3", facecolor=BG_CARD,
                                      edgecolor=BORDER_CARD, linewidth=1.5)
        ax.add_patch(card2)
        
        ty = y + 36
        for line in s["tools"]:
            ax.text(790, ty, line, fontsize=9.5, color='#E2E8F0')
            ty -= 24

        # 3. Output Contribution Box (Col 3)
        w3, h3 = 880, 125
        card3 = patches.FancyBboxPatch((1630, y - h3/2), w3, h3,
                                      boxstyle="round,pad=0.3", facecolor=BG_CARD,
                                      edgecolor=BORDER_CARD, linewidth=1.5)
        ax.add_patch(card3)

        oy = y + 36
        for line in s["outputs"]:
            c_text = ACCENT_AMBER if "CONF-01" in line or "Conflict" in line else '#CBD5E1'
            ax.text(1650, oy, line, fontsize=9.5, color=c_text)
            oy -= 24

        # Connecting vertical arrow down to next stage
        if i < len(stages) - 1:
            next_y = stages[i+1]["y"]
            arrow = patches.FancyArrowPatch((400, y - h1/2), (400, next_y + stages[i+1]["y"] - next_y + 62),
                                           arrowstyle='->', mutation_scale=15,
                                           color=color, linewidth=2, linestyle='-')
            ax.add_patch(arrow)
            
            # Flow arrow from Col 2 to Col 3
            arrow_mid = patches.FancyArrowPatch((1592, y), (1628, y),
                                               arrowstyle='->', mutation_scale=12,
                                               color='#475569', linewidth=1.5)
            ax.add_patch(arrow_mid)
            
            arrow_in = patches.FancyArrowPatch((732, y), (768, y),
                                              arrowstyle='->', mutation_scale=12,
                                              color='#475569', linewidth=1.5)
            ax.add_patch(arrow_in)

    # Save to script report assets and artifact directory
    out_dir_local = Path("backend/scripts/report_assets")
    out_dir_local.mkdir(parents=True, exist_ok=True)
    out_file_local = out_dir_local / "diagram_agent_orchestration_flowchart.png"
    plt.savefig(out_file_local, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none', dpi=200)

    # Also save directly to artifact directory
    artifact_dir = Path(r"C:\Users\KIIT0001\.gemini\antigravity\brain\73297338-b3a8-4bdf-9c32-dc263901b78f")
    out_file_artifact = artifact_dir / "Nebula9_Agent_Orchestration_Flowchart.png"
    plt.savefig(out_file_artifact, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none', dpi=200)
    plt.close()

    print(f"Flowchart successfully generated at:")
    print(f"1. {out_file_local} ({os.path.getsize(out_file_local):,} bytes)")
    print(f"2. {out_file_artifact} ({os.path.getsize(out_file_artifact):,} bytes)")

if __name__ == "__main__":
    generate_flowchart()
