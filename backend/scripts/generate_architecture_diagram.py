import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_overall_architecture_image():
    base_dir = Path("c:/Users/KIIT0001/Desktop/Enterprise Knowlegde Interface")
    output_png = base_dir / "Nebula9_Overall_System_Architecture.png"
    docs_png = base_dir / "Documents/Nebula9_Overall_System_Architecture.png"
    artifact_png = Path("C:/Users/KIIT0001/.gemini/antigravity/brain/73297338-b3a8-4bdf-9c32-dc263901b78f/Nebula9_Overall_System_Architecture.png")

    fig = plt.figure(figsize=(16, 10), dpi=300)
    ax = fig.add_subplot(111)
    
    # Background
    bg_color = "#0B0F19"
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def draw_card(x, y, w, h, title, subtitle, items, border_color, header_bg="#111827", body_bg="#161F30"):
        # Main body
        body = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.2,rounding_size=1.5",
            facecolor=body_bg, edgecolor=border_color, linewidth=1.8,
            zorder=2
        )
        ax.add_patch(body)

        # Header bar
        header_h = 3.8
        header = patches.FancyBboxPatch(
            (x, y + h - header_h), w, header_h,
            boxstyle="round,pad=0.2,rounding_size=1.5",
            facecolor=header_bg, edgecolor=border_color, linewidth=1.5,
            zorder=3
        )
        ax.add_patch(header)

        # Title text
        ax.text(x + w/2, y + h - 2.0, title, color="white", fontsize=10.5, fontweight="bold", ha="center", va="center", zorder=4)
        
        # Subtitle
        if subtitle:
            ax.text(x + w/2, y + h - 5.2, subtitle, color=border_color, fontsize=8.0, fontweight="bold", ha="center", va="center", zorder=4)

        # Items
        start_y = y + h - 7.5
        for idx, item in enumerate(items):
            ax.text(x + 1.8, start_y - (idx * 2.3), f"• {item}", color="#E2E8F0", fontsize=7.8, va="center", zorder=4)

    # ------------------ TITLE & HEADER ------------------
    ax.text(50, 96.5, "NEBULA9 ENTERPRISE KNOWLEDGE INTELLIGENCE", color="white", fontsize=16, fontweight="bold", ha="center")
    ax.text(50, 93.8, "Industrial-Grade Dual-Agent Grounded Architecture with Zero-Trust Security & Tiered Hybrid Parsers", color="#94A3B8", fontsize=9.5, ha="center")

    # ------------------ LAYER 1: CLIENT & EXPERIENCE LAYER ------------------
    # Outer container
    client_box = patches.FancyBboxPatch((3, 76), 94, 15, boxstyle="round,pad=0.5,rounding_size=1.5", facecolor="#0E1626", edgecolor="#38BDF8", linewidth=1.2, linestyle="--")
    ax.add_patch(client_box)
    ax.text(5, 89.5, "1. PRESENTATION & EXPERIENCE LAYER (React 19 + Vite TypeScript)", color="#38BDF8", fontsize=9, fontweight="bold")

    draw_card(5, 77.5, 27, 10.5, "CXO Executive Interface", "React 19 / Tailwind / Lucide", [
        "Natural language executive prompt bar",
        "Multi-industry switcher (Mfg/Retail/Health)",
        "Dynamic KPI Metric Cards (Downtime/ROI)",
        "Timeline conflict alerts ([CONF-01])"
    ], "#38BDF8")

    draw_card(36.5, 77.5, 27, 10.5, "Interactive Evidence Drawer", "Clickable Provenance [DOC / SQL]", [
        "Verified SQL queries with execution timing",
        "Raw database rows & column inspector",
        "PDF excerpt highlights with page numbers",
        "Visual diagram viewer with metadata"
    ], "#38BDF8")

    draw_card(68, 77.5, 27, 10.5, "Agent Reasoning Trace", "Real-Time Telemetry Drawer", [
        "Step-by-step agent workflow visualization",
        "Execution latency per stage (ms)",
        "Server-Sent Events (SSE) live streaming",
        "Sub-task status badges (completed/warning)"
    ], "#38BDF8")

    # ------------------ LAYER 2: GATEWAY & GOVERNANCE LAYER ------------------
    gw_box = patches.FancyBboxPatch((3, 56), 94, 16.5, boxstyle="round,pad=0.5,rounding_size=1.5", facecolor="#12132A", edgecolor="#A855F7", linewidth=1.2, linestyle="--")
    ax.add_patch(gw_box)
    ax.text(5, 71.0, "2. API GATEWAY, RBAC & ORCHESTRATION LAYER (FastAPI)", color="#A855F7", fontsize=9, fontweight="bold")

    draw_card(5, 57.5, 27, 11.5, "API Gateway & Security", "Zero-Trust Enforcement", [
        "JWT Authentication + PBKDF2 hashing",
        "RBAC clearance (Public -> Restricted)",
        "Role filters: CXO, Plant Mgr, Analyst",
        "Write-ahead SQLite / Postgres audit logs"
    ], "#A855F7")

    draw_card(36.5, 57.5, 27, 11.5, "Query Router & DAG Planner", "Intent Decomposition Engine", [
        "Classifies: SQL / Document / Cross-Source",
        "Decomposes complex inquiries into DAG",
        "Parallel sub-task scheduling",
        "WorkflowState context isolation"
    ], "#A855F7")

    draw_card(68, 57.5, 27, 11.5, "Executive Synthesis Agent", "Consolidated Grounding", [
        "Merges SQL rows with narrative text",
        "Extracts dynamic executive KPI cards",
        "Surfaces cross-source discrepancies",
        "Cryptographic citation anchoring"
    ], "#10B981")

    # ------------------ LAYER 3: MULTI-AGENT INTELLIGENCE LAYER ------------------
    intel_box = patches.FancyBboxPatch((3, 26), 94, 26.5, boxstyle="round,pad=0.5,rounding_size=1.5", facecolor="#141E28", edgecolor="#F59E0B", linewidth=1.2, linestyle="--")
    ax.add_patch(intel_box)
    ax.text(5, 51.0, "3. SPECIALIZED INTELLIGENCE & DATA ACCESS LAYER", color="#F59E0B", fontsize=9, fontweight="bold")

    # Structured Data Agent & Safe Sandbox
    draw_card(5, 27.5, 42, 21.5, "Structured Data Intelligence", "Agent + Safe Read-Only SQL Sandbox", [
        "Text-to-SQL Synthesizer (Gemini API with deterministic fallback)",
        "sqlglot AST Inspection: Enforces SELECT root expressions only",
        "Zero-Tolerance Mutation Blocker: Rejects DROP, DELETE, INSERT, ALTER",
        "Chained Statement Blocker: Halts semicolon injection attacks",
        "Strict Allowlist: plant_downtime, work_orders, supplier_quality, oee",
        "Catalog Protection: Denies access to 'users' and 'sqlite_master'",
        "Auto Limit Injection: Enforces & clamps queries to LIMIT 100",
        "Deep Provenance: Emits execution time (ms), rows, and [SQL-01]"
    ], "#60A5FA")

    # Document Intelligence & Tiered Parsers
    draw_card(53, 27.5, 42, 21.5, "Multi-Modal Document Intelligence", "Document Agent + Tiered Hybrid Parsers", [
        "Tier 1 (High-Speed): PyMuPDF4LLM for sub-50ms text extraction",
        "Tier 2 (Structural): OpenDataLoader PDF with XY-Cut++ reading order",
        "Tier 3 (Layout): IBM Docling + TableFormer for borderless tables",
        "Air-Gapped Vision: 100% on-premise ONNX RapidOCR & SVG analysis",
        "Tabular Sheets: openpyxl for multi-sheet Excel incident workbooks",
        "Hybrid Search Index: BM25 exact part codes (VLV-4401) + semantic vector",
        "Clearance Filter: Enforces document classification per user role",
        "XML Inert Evidence Fencing: Neutralizes indirect prompt injections"
    ], "#F59E0B")

    # ------------------ LAYER 4: STORAGE & CONFIGURATION ------------------
    store_box = patches.FancyBboxPatch((3, 3), 94, 19.5, boxstyle="round,pad=0.5,rounding_size=1.5", facecolor="#0F172A", edgecolor="#94A3B8", linewidth=1.2, linestyle="--")
    ax.add_patch(store_box)
    ax.text(5, 21.0, "4. PERSISTENCE, DATA STORES & REUSABILITY CONFIGURATION", color="#94A3B8", fontsize=9, fontweight="bold")

    draw_card(5, 4.5, 27, 14.5, "Relational Databases", "Sandboxed Operational DB", [
        "SQLite / PostgreSQL Connection",
        "plant_downtime_events",
        "maintenance_work_orders",
        "supplier_component_quality",
        "production_line_metrics (OEE)"
    ], "#93C5FD")

    draw_card(36.5, 4.5, 27, 14.5, "Unstructured Assets", "On-Prem Document Store", [
        "PDF SOPs & Equipment Manuals",
        "Excel Shift Logs (.xlsx)",
        "Inspection Scans (.png/.jpg)",
        "Vector SVG Architecture Diagrams"
    ], "#FDE68A")

    draw_card(68, 4.5, 27, 14.5, "Hot Industry Packs", "/config/industries/ (Zero-Downtime)", [
        "Manufacturing (Line OEE / Downtime)",
        "Retail & CPG (POS / Stockout ROI)",
        "Healthcare (EHR / Bed Utilization)",
        "ontology.yaml & sources.yaml"
    ], "#C084FC")

    # ------------------ CONNECTING ARROWS ------------------
    arrow_blue = dict(arrowstyle="->", color="#38BDF8", lw=2, mutation_scale=12)
    arrow_purple = dict(arrowstyle="->", color="#A855F7", lw=2, mutation_scale=12)
    arrow_green = dict(arrowstyle="->", color="#10B981", lw=2, mutation_scale=12)
    arrow_dashed = dict(arrowstyle="->", color="#94A3B8", lw=1.5, linestyle="--", mutation_scale=10)

    # UI to Gateway
    ax.annotate("", xy=(18.5, 69), xytext=(18.5, 77.5), arrowprops=arrow_blue)
    # Gateway to Router
    ax.annotate("", xy=(36.5, 63.2), xytext=(32, 63.2), arrowprops=arrow_purple)
    # Router to Structured Agent
    ax.annotate("", xy=(26, 49), xytext=(40, 57.5), arrowprops=arrow_purple)
    # Router to Document Agent
    ax.annotate("", xy=(74, 49), xytext=(60, 57.5), arrowprops=arrow_purple)

    # Agents to DBs
    ax.annotate("", xy=(18.5, 19), xytext=(18.5, 27.5), arrowprops=arrow_dashed)
    ax.annotate("", xy=(50, 19), xytext=(60, 27.5), arrowprops=arrow_dashed)

    # Agents back to Synthesizer
    ax.annotate("", xy=(75, 57.5), xytext=(35, 49), arrowprops=arrow_green)
    ax.annotate("", xy=(85, 57.5), xytext=(78, 49), arrowprops=arrow_green)

    # Synthesizer to Evidence Drawer
    ax.annotate("", xy=(50, 77.5), xytext=(78, 69), arrowprops=arrow_green)

    # Save outputs
    plt.tight_layout()
    plt.savefig(output_png, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.savefig(docs_png, facecolor=fig.get_facecolor(), edgecolor="none")
    
    # Save to artifacts directory for inline chat viewing
    artifact_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(artifact_png, facecolor=fig.get_facecolor(), edgecolor="none")
    
    plt.close()
    print(f"Generated architecture diagram at:\n- {output_png}\n- {docs_png}\n- {artifact_png}")

if __name__ == "__main__":
    generate_overall_architecture_image()
