# Manufacturing Use-Case & Synthetic Dataset Specification

## 1. Scenario Background
The first complete implementation of the Nebula9 platform uses **Industrial / Advanced Manufacturing**. Manufacturing is selected because it spans heterogeneous data types:
1. **High-frequency structured operational data**: Machine downtime logs, production line yields, maintenance tickets, supplier defect metrics.
2. **Dense unstructured technical documents**: Equipment operating manuals (OEM), Standard Operating Procedures (SOP), shift handoff notes, root-cause investigation memos.
3. **Controlled external intelligence**: Component recalls, vendor service advisories, environmental/grid alerts.

---

## 2. Core CXO Demo Questions (PRD Appendix B)

1. **Root Cause & Historical Remediation**:
   > *"What are the major factors contributing to production downtime at Plant A, and what actions have previously reduced similar downtime?"*
2. **Cross-System Anomaly Detection**:
   > *"Which production lines show a combination of rising downtime and declining quality, and what evidence explains the pattern?"*
3. **Supplier Risk & Corrective Actions**:
   > *"Which suppliers are associated with the highest quality-impact events, and what do supplier documents say about corrective actions?"*
4. **Procedure Evolution Impact**:
   > *"What changed between the previous and current maintenance procedures, and is there evidence that the change affected downtime?"*
5. **Conflict & Discrepancy Discovery**:
   > *"Where do the production report and maintenance documentation disagree, and which source is more recent?"*

---

## 3. Synthetic Data Catalog & Schemas

### 3.1 Relational Tables (PostgreSQL / SQLite)

#### Table: `production_lines`
- `line_id` (TEXT, PK): e.g., `'LINE-01'`, `'LINE-02'`
- `plant_id` (TEXT): e.g., `'PLANT-A'`, `'PLANT-B'`
- `equipment_name` (TEXT): e.g., `'Robotic Welding & Assembly Cell'`
- `oee_target` (FLOAT): `0.85`
- `installed_year` (INTEGER): `2021`

#### Table: `downtime_events`
- `event_id` (TEXT, PK): e.g., `'EVT-9041'`
- `line_id` (TEXT, FK): `'LINE-02'`
- `plant_id` (TEXT): `'PLANT-A'`
- `start_time` (TIMESTAMP): `'2026-08-14 06:15:00'`
- `end_time` (TIMESTAMP): `'2026-08-14 20:27:00'`
- `duration_hours` (FLOAT): `14.2`
- `category_code` (TEXT): `'HYD-04'` (Hydraulic Failure)
- `recorded_cause` (TEXT): `'Hydraulic valve seizure on robotic arm actuator'`
- `financial_impact_usd` (FLOAT): `42600.00`

#### Table: `supplier_quality`
- `lot_id` (TEXT, PK): `'LOT-2026-441'`
- `supplier_name` (TEXT): `'Apex Hydraulics Inc'`
- `component_category` (TEXT): `'Proportional Flow Valves'`
- `defect_rate_ppm` (FLOAT): `840.5` (Threshold: `150.0`)
- `audit_status` (TEXT): `'CORRECTIVE_ACTION_REQUIRED'`

---

### 3.2 Unstructured Document Corpus

1. **`SOP-MNT-402_Hydraulic_Assembly_Maintenance.pdf`**:
   - *Sections*: Section 2 (Safety Lockout), Section 4 (Flushing and Fluid Testing), Section 7 (Seal Replacement Schedules).
   - *Key Evidence*: Section 4.2 states that quarterly high-pressure solvent flushing reduced historical valve seizure occurrences by 68%.
2. **`OEM_Manual_Vortex_Robotic_Arm_V3.pdf`**:
   - *Sections*: Specifications, Operating Temperature Range (10°C–45°C), Recommended Lubrication (ISO VG 46), Hydraulic Pressure Limits (210 bar).
3. **`Plant_A_Q3_Engineering_Investigation_Memo.pdf`**:
   - *Author*: Chief Plant Reliability Engineer.
   - *Date*: August 18, 2026.
   - *Key Evidence & Conflict*: States that upon actuator teardown, the mechanical valve was free of debris; the primary trigger was an intermittent upstream sensor calibration drift that caused the PLC safety shutdown.
4. **`Supplier_Quality_Audit_ApexHydraulics_2026.pdf`**:
   - *Date*: July 10, 2026.
   - *Details*: Audit results indicating batch seal porosity issues causing micro-leaks.

---

### 3.3 Controlled External Sources
- **`vendor_advisories/OEM-ADV-2026-08.json`**:
  - *Publisher*: Vortex Robotics Global Support
  - *Date*: August 25, 2026
  - *Content*: Recommends upgrading seal elastomers to fluorocarbon (FKM) when ambient summer plant temperatures exceed 38°C to prevent pressure loss.
