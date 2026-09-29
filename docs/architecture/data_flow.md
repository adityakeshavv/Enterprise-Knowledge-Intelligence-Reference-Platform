# End-to-End Data Flow Specification

## 1. Request Lifecycle Overview
This document specifies the exact sequence of data transformations and inter-agent messages from user prompt submission to rendered executive response.

```mermaid
sequenceDiagram
    autonumber
    actor User as CXO / Business User
    participant Gateway as FastAPI Gateway
    participant Auth as RBAC & Auth Filter
    participant Router as Query Router / Planner
    participant Blackboard as State Blackboard
    participant DocAgent as Document Agent
    participant DataAgent as Structured Data Agent
    participant ValAgent as Evidence / Validation Agent
    participant SynthAgent as Synthesis Agent
    participant Audit as Audit Logger

    User->>Gateway: POST /api/query { query, industry_id, session_token }
    Gateway->>Auth: Validate JWT & User Permissions
    Auth-->>Gateway: Authorized (Role: Executive, AllowedWorkspaces: [Plant_A, Plant_B])
    
    Gateway->>Router: Analyze Query (with Industry Config & Terminology)
    Router->>Router: Decompose into sub-queries
    Router->>Blackboard: Initialize execution plan
    
    par Document Retrieval
        Router->>DocAgent: Query: "hydraulic valve seizure downtime history"
        DocAgent->>DocAgent: Hybrid search (vector + BM25) with plant filter
        DocAgent-->>Blackboard: Store passages [Doc: SOP-MNT-402, Page: 14; Incident-Memo-Q3, Page 2]
    and Structured Data Query
        Router->>DataAgent: Metric: "Downtime hours by cause code Plant A Q3"
        DataAgent->>DataAgent: Generate SQL -> AST Safety Validation -> Execute read-only
        DataAgent-->>Blackboard: Store tabular rows [Machine: ARM-02, Downtime: 14.2 hrs, Cause: Valve]
    end

    Blackboard->>ValAgent: Evaluate (Passages + Tabular Data + Proposed Claims)
    ValAgent->>ValAgent: Verify grounding of facts against sources
    ValAgent->>ValAgent: Detect discrepancies (Database says Valve Seizure vs Incident Memo says Sensor Timeout)
    ValAgent-->>Blackboard: Validation Report (Grounding: 0.94, Conflicts: [Conflict_1])

    Blackboard->>SynthAgent: Synthesize Final Executive Response
    SynthAgent->>SynthAgent: Format into standard executive schema
    SynthAgent-->>Gateway: Final Answer Payload

    Gateway->>Audit: Record Query, Latency, Agents, Citations, Tokens, User ID
    Gateway-->>User: Stream / Return Final Response + Evidence Drawer Data
```

---

## 2. Data Contracts & JSON Schemas

### 2.1 Query Request Contract
```json
{
  "query": "What are the major factors contributing to production downtime at Plant A, and what actions have previously reduced similar downtime?",
  "industry_id": "manufacturing",
  "workspace_id": "plant_a",
  "filters": {
    "date_range": {
      "start": "2026-07-01",
      "end": "2026-09-30"
    }
  }
}
```

### 2.2 Final Executive Answer Response Contract
```json
{
  "query_id": "qry_8923fbc0",
  "industry_id": "manufacturing",
  "execution_time_ms": 3420,
  "executive_summary": "Production downtime at Plant A during Q3 was primarily driven by recurring hydraulic valve seizures on Robotic Arm Line 2 (accounting for 14.2 hours) and secondary upstream sensor calibration drift. Previous preventive valve flushing reduced downtime by 68% in Q1.",
  "key_findings": [
    "Line 2 experienced 14.2 hours of unscheduled stoppage in August due to hydraulic actuator pressure loss.",
    "Root cause investigation memo dated Aug 18 highlights upstream sensor drift as an unaddressed contributing factor.",
    "Vendor service advisory OEM-ADV-2026-08 recommends replacing O-ring seal compounds with high-temperature nitrile."
  ],
  "metrics_table": {
    "headers": ["Line ID", "Equipment", "Downtime Hours", "Primary Recorded Cause", "Cost Impact ($)"],
    "rows": [
      ["Line 2", "Robotic Arm ARM-02", 14.2, "Hydraulic Valve Seizure", 42600],
      ["Line 1", "Conveyor Motor M-04", 4.5, "Bearing Overheating", 11250],
      ["Line 3", "Packaging Sealer S-01", 2.1, "Heating Element Failure", 4800]
    ]
  },
  "grounding_confidence": 0.94,
  "citations": [
    {
      "citation_id": "cit_1",
      "source_type": "document",
      "source_name": "SOP-MNT-402_Hydraulic_Assembly_Maintenance.pdf",
      "page_number": 14,
      "section": "4.2 Preventative Flushing Protocols",
      "excerpt": "Quarterly solvent flushing of high-pressure proportional valves has demonstrated a 68% decrease in seizure incidents."
    },
    {
      "citation_id": "cit_2",
      "source_type": "structured_data",
      "source_name": "downtime_events",
      "query_executed": "SELECT line_id, equipment_id, SUM(duration_hours) FROM downtime_events WHERE plant='Plant A' AND quarter='Q3' GROUP BY 1, 2",
      "record_count": 3
    }
  ],
  "conflicts": [
    {
      "conflict_id": "cnf_1",
      "topic": "Line 2 Root Cause Discrepancy",
      "statement_a": "Maintenance Work Order #8401 reports downtime caused by mechanical valve seizure.",
      "statement_b": "Shift Supervisor Investigation Memo (Aug 18) reports valve was functional, failure caused by upstream sensor communication fault.",
      "resolution_note": "Unresolved. Maintenance report was filed Aug 14 at incident time; memo was submitted Aug 18 after teardown inspection."
    }
  ],
  "agent_trace": [
    {"agent": "Router", "action": "Decomposed query into 1 SQL task and 2 document retrieval tasks", "duration_ms": 310},
    {"agent": "Structured Data Agent", "action": "Queried downtime_events table (3 records retrieved)", "duration_ms": 520},
    {"agent": "Document Agent", "action": "Retrieved 4 relevant sections from SOP-MNT-402 and Q3 Memo", "duration_ms": 1180},
    {"agent": "Validation Agent", "action": "Verified claim support and flagged 1 discrepancy", "duration_ms": 640},
    {"agent": "Synthesis Agent", "action": "Compiled executive report with verified citations", "duration_ms": 770}
  ]
}
```
