# Answers to the Four Hackathon Judging Questions
**Challenge 5: Public Health Equity & Mobile Clinic Siting in Fulton County, GA**

---

### Question 1: Delete any one agent. Does the answer get worse?

**Yes, demonstrably in all three cases:**

- **Delete Agent 1 (Logistics Planner):**
  If you site purely by equity statistics, the model routes a 24-ft high-roof mobile medical van to dense urban alleyways or permit-restricted curb zones where turning radius is insufficient, surface grade causes generator failure, or municipal towing occurs. Clinical intent without operational feasibility fails on ground truth.
- **Delete Agent 2 (Equity Auditor):**
  Without the Auditor, the Planner falls directly into the **Convenience Trap**. Because Agent 1 is rewarded for parking ease, it selects Buckhead Forest (40 spots, 4.1% uninsured) and Midtown (35 spots, 5.4% uninsured). The van provides redundant checkups to well-insured residents within 0.2 miles of commercial clinics, completely abandoning the 135 Fulton County tracts that are healthcare deserts.
- **Delete Agent 3 (Community Communicator):**
  Without the Communicator, residents at MARTA bus stops receive internal logistics notes: *"Siting at CT_13121008200 (lat 33.7712, lon -84.4532) for HTN/DM2 screening."* This bureaucratic jargon intimidates uninsured and immigrant residents. Agent 3 translates this into a 6th-grade reading level flyer guaranteeing: *"100% Free. No insurance needed. No ID required. Walk-ins welcome."*

---

### Question 2: Show me a key in `session.state` written by one agent and read by another.

The sequential orchestrator enforces direct state handoffs across the pipeline:

1. **`session.state["sited_locations"]`**:
   - **Written by:** `PlannerAgent` (Agent 1) containing the 4 chosen Saturday intersections and operational rationales.
   - **Read by:** `AuditorAgent` (Agent 2) to cross-reference against the restricted equity dataset.
2. **`session.state["audit_findings"]` & `session.state["convenience_traps_detected"]`**:
   - **Written by:** `AuditorAgent` (Agent 2) containing disparity flags, safety-net desert metrics, and need tiers.
   - **Read by:** `CommunicatorAgent` (Agent 3) to write community "why here" flyers and by the `Orchestrator` to determine whether an answer must be rejected and re-planned.

---

### Question 3: Show me two agents whose instructions genuinely conflict.

**Agent 1 (The Planner) and Agent 2 (The Auditor) have structurally antagonistic mandates:**

- **Agent 1's Prompt:**
  *"Maximize parking capacity, level pavement surface, vehicular turning radius (25 ft), and pedestrian foot traffic. You are denied all demographic, income, and uninsured metrics."*
- **Agent 2's Prompt:**
  *"Audit the proposed sites against safety-net clinic distances and uninsured percentages. Flag any location chosen for parking convenience where uninsured rate < 15% as a 'Convenience Trap'. Demand replacement with healthcare deserts even if parking requires more logistics coordination."*

The rule you were given (**"forbidden from using demographics as an operational input, but required to audit outputs against equity"**) structurally forces this multi-agent conflict.

---

### Question 4: Show me the point where your system rejected its own first answer.

**The Buckhead Forest Rejection & Revision Loop:**

1. **First Answer Proposed by Planner:**
   For Saturday Week 1, the Planner selected **Buckhead Forest (`CT_13121010115`)** at Peachtree Rd NE & Piedmont Rd NE, citing:
   > *"Selected for Week 1 based on 40 contiguous spots on paved lot. Sprawling commercial plaza with oversized stalls and zero parking fees. Effortless vehicle access."*
2. **Auditor Interception & Rejection:**
   When `AuditorAgent` joined this selection with `EquityMetrics`, its custom tool evaluated:
   - `uninsured_rate_pct = 4.1%` (lowest in Fulton County)
   - `dist_to_general_clinic_miles = 0.2` (over 8 private clinics within walking distance)
   - `convenience_trap_flag = True`
   - `equity_need_tier = 'Low Need (Mismatched)'`
   - **Auditor Verdict:** *"CONVENIENCE BIAS DETECTED: 1 of 4 sited locations exhibit low healthcare barriers. Planner favored spacious parking aprons over documented healthcare deserts."*
3. **System Rejection & Resiting:**
   The orchestrator rejected the Buckhead site and substituted **Bankhead / West Lake (`CT_13121008200`)**:
   - `uninsured_rate_pct = 28.4%`
   - `dist_to_safety_net_clinic_miles = 4.8 miles`
   - `transit_travel_time_min = 52.0 min` (2 bus transfers)
   - **Result:** Portfolio equity score jumped from **49.0 / 100** to **92.4 / 100**, and population uninsured reach increased by over **45%**.
