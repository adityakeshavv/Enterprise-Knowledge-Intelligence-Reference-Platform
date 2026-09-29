# Configuration vs. Code Boundary Specification

## 1. Architectural Guardrail
> **Reviewer Note (PRD & Timeline)**:
> *"The target is a reusable platform, not just a Manufacturing UI. Any core-code change required solely to switch industry should be flagged."*

This document defines the strict demarcation between **Core Platform Code** (which must never mention manufacturing-specific or retail-specific concepts) and **Industry Configuration Packs** (which supply all domain models, schemas, prompts, and evaluation data).

---

## 2. Demarcation Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CORE PLATFORM CODE (Language: Python/TS)             │
│                                                                        │
│  - Agent State Machine & Orchestrator                                  │
│  - Dynamic YAML Configuration Ingestion Engine                        │
│  - SQL AST Validator & Safe Query Execution Sandbox                   │
│  - Hybrid Vector Search (BM25 + Dense) Abstraction Layer              │
│  - Sentence Grounding & Conflict Detection Algorithms                 │
│  - JWT Authentication, RBAC Evaluation, & Audit Logging               │
│  - Reusable Executive UI Shell (Layout, Chat, Drawers, Tables)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Dynamic Ingestion via Config Loader
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             INDUSTRY CONFIGURATION PACKS (/config/industries/)         │
│                                                                        │
│  /manufacturing/                      /retail_cpg/                     │
│    ├── industry.yaml                    ├── industry.yaml              │
│    ├── terminology.yaml                 ├── terminology.yaml           │
│    ├── sources.yaml                     ├── sources.yaml               │
│    ├── prompts.yaml                     ├── prompts.yaml               │
│    ├── scenarios.yaml                   ├── scenarios.yaml             │
│    └── evaluation.yaml                  └── evaluation.yaml            │
└────────────────────────────────────────────────────────────────────────┘
```

| Dimension | Configurable Industry Pack | Core Platform Code |
| :--- | :--- | :--- |
| **Terminology & Synonyms** | Domain jargon, acronyms (e.g. `OEE`, `MTBF`, `SKU`, `Sell-through`) | General dictionary lookup and token replacement engine |
| **Data Schema & Catalogs** | Table names, column descriptions, foreign keys, document paths | Database connection management, query execution, vector indexing |
| **Agent Prompt Directives** | Domain guidelines, KPI prioritization rules, executive framing | Agent execution framework, chain-of-thought orchestration, JSON parsing |
| **Demonstration Scenarios** | Curated questions, target narrative paths, sample answers | Scenario selector UI, session dispatcher, history manager |
| **Discrepancy Heuristics** | Numerical tolerance thresholds (e.g., 5% variance for downtime) | Conflict detection engine, side-by-side discrepancy comparator |
| **Security Roles** | Industry roles (e.g. `Plant_Manager`, `Store_Manager`) | Role-based authorization filter, token issuer, session verifier |
| **Evaluation Benchmarks** | 20–30 domain QA pairs, expected evidence IDs, ground truth | Automated benchmark test harness, accuracy calculation, report generator |

---

## 3. Directory Structure

```text
Enterprise Knowledge Interface/
├── backend/
│   ├── app/
│   │   ├── core/           <-- IMMUTABLE CORE PLATFORM
│   │   ├── agents/         <-- IMMUTABLE AGENT FRAMEWORK
│   │   ├── api/            <-- IMMUTABLE REST/WS API
│   │   ├── db/             <-- IMMUTABLE SQL/VECTOR INTERFACES
│   │   └── config_loader/  <-- Dynamic YAML Parser
├── frontend/
│   └── src/
│       ├── components/     <-- IMMUTABLE REUSABLE UI COMPONENTS
│       ├── context/        <-- Dynamic Industry Context
│       └── views/          <-- CXO Views driven by config
└── config/
    └── industries/         <-- 100% DECLARATIVE INDUSTRY PACKS
        ├── manufacturing/
        └── retail_cpg/
```

### Prohibited Code Smells (Flagged in Code Reviews)
- Hardcoding strings like `"Plant A"`, `"OEE"`, `"hydraulic valve"`, or `"retail"` in `backend/app/` or `frontend/src/components/`.
- Switching logic based on `if (industry === 'manufacturing') { runSpecialManufacturingCode(); }`.
- Direct file imports linking core platform code to `/config/industries/manufacturing/` instead of through the generic `ConfigLoader` interface.
