# Fulton County Mobile Health Clinic Siting Multi-Agent System
**Agents for Impact Code Challenge • Public Health Equity Siting System**

This repository implements a sequential multi-agent system built using the **Google Cloud ADK (Agent Development Kit)** architectural pattern. It addresses mobile medical van siting in Fulton County, Georgia, across 4 Saturdays in a month, ensuring care reaches vulnerable, uninsured populations rather than being trapped in convenient parking locations.

---

## 🏛️ Architecture: Enforced Context Separation

A strict **context barrier** is programmatically enforced between operational siting and equity evaluation:

```
[Full Fulton County Dataset: 10 Representative Tracts]
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
[Physical Feasibility Only]     [Restricted Equity Data]
 (Parking, Turning Radius,       (Uninsured %, Poverty %,
  Surface, Foot Traffic)          Transit Times, Clinic Dists)
             │                           │
             ▼                           │
┌─────────────────────────┐              │
│  Agent 1: Planner       │              │
│  (Operational Siting)   │              │
└────────────┬────────────┘              │
             │                           │
             ▼ (4 Sited Locations)       │
             └─────────────┬─────────────┘
                           ▼
             ┌───────────────────────────┐
             │  Agent 2: Auditor         │
             │  (Disparity Evaluation)   │
             └─────────────┬─────────────┘
                           ▼
             ┌───────────────────────────┐
             │  Agent 3: Communicator    │
             │  (6th-Grade Community)    │
             └─────────────┬─────────────┘
                           ▼
             ┌───────────────────────────┐
             │  Synthesizer              │
             │  (4-Part Deliverable)     │
             └───────────────────────────┘
```

1. **Agent 1 (The Planner):**
   - Inputs: Only `OperationalCandidate` models (tract ID, intersection, parking spot count, surface type, turning radius feasibility, foot traffic).
   - Denied: Poverty rates, uninsured rates, transit travel times, clinic distances.
   - Task: Selects 4 distinct locations for the upcoming Saturdays.

2. **Agent 2 (The Auditor):**
   - Ingests: The Planner's 4 selections joined with the withheld `EquityMetrics` dataset.
   - Task: Calculates health disparity metrics, flags "Convenience Traps" (locations with low uninsured rates picked purely for parking convenience), and computes the portfolio equity alignment score.

3. **Agent 3 (The Communicator):**
   - Ingests: Audited plan and selected sites.
   - Task: Generates 6th-grade reading level public flyers for MARTA stops and community boards. Accurately scopes care to nurse practitioner screenings (blood pressure cuff, glucometer) and clarifies that no ID, money, or insurance is needed.

4. **Deliverable Synthesizer:**
   - Assembles the 4-part **Clinic Plan**:
     * **Section 1:** Where the van goes and why (Planner)
     * **Section 2:** Who the plan lands on / disparity audit (Auditor)
     * **Section 3:** Community-facing plain-language text (Communicator)
     * **Section 4:** Data limitations & resolution gaps disclosure (acknowledging why 4-decimal data does not equal precise ground-truth resolution)

---

## 📁 Repository Structure

```
fulton_mobile_clinic/
├── models.py            # Pydantic data contracts (OperationalCandidate, PlannerOutput, AuditorOutput, etc.)
├── data.py              # 10 representative Fulton County tracts & strict context accessors
├── agents.py            # Planner, Auditor, and Communicator definitions with system prompts
├── synthesizer.py       # Orchestrator & 4-part Clinic Plan synthesizer (Markdown/JSON)
├── main.py              # CLI entry point to execute the pipeline end-to-end
├── test_pipeline.py     # Automated test suite (context barrier, schema validation, convenience trap)
└── README.md            # System documentation
```

---

## 🚀 Quickstart & Execution

### 1. Run End-to-End Pipeline
```bash
python3 main.py
```
This runs the full 3-agent pipeline and automatically generates:
- `CLINIC_PLAN.md`: Formatted publication-ready Markdown report.
- `clinic_plan.json`: Validated structured JSON artifact.

### 2. Run Test Suite
```bash
pytest -v test_pipeline.py
```
Validates context isolation security, Pydantic serialization, convenience trap triggers, and Section 1-4 completeness.
