"""
Pipeline Orchestrator and Deliverable Synthesizer.
Assembles the complete 4-part Clinic Plan:
  - Section 1: Where the van goes and why (Planner)
  - Section 2: Who the plan lands on / disparity audit (Auditor)
  - Section 3: Community-facing plain-language text (Communicator)
  - Section 4: Data limitations & resolution gaps disclosure
"""

import json
from typing import Optional
from models import ClinicPlan, DataLimitationsDisclosure
from data import (
    get_operational_candidates,
    get_equity_data_lookup,
    get_full_candidates_lookup,
)
from agents import PlannerAgent, AuditorAgent, CommunicatorAgent


def generate_limitations_disclosure() -> DataLimitationsDisclosure:
    """Rigorous academic & public health disclosure on resolution gaps and statistical biases."""
    return DataLimitationsDisclosure(
        ecological_fallacy_risk=(
            "Census tracts in Fulton County average 4,000 residents across diverse micro-environments. "
            "Attributing tract-level uninsured rates (e.g. 28.4%) to every household within the boundary "
            "commits an ecological fallacy. Pockets of severe uninsurance can exist in moderate-income tracts, "
            "and well-insured clusters can exist in high-vulnerability tracts."
        ),
        spatial_resolution_gap=(
            "Geographic coordinates with 4 decimal places provide theoretical precision of approximately "
            "11.1 meters (~36 feet). However, numerical GPS coordinates do not encode ground-truth curb realities: "
            "curb cut heights, active loading zone tow ordinances, low-hanging utility wires, generator noise "
            "ordinances, or private property towing enforcement. Ground-truthed physical scouting is essential."
        ),
        transit_schedule_discrepancy=(
            "Published General Transit Feed Specification (GTFS) travel times assume on-time bus schedules. "
            "In practice, Saturday MARTA headways frequently experience 30-to-60 minute intervals, missed connections, "
            "and service cuts. Transit times reported here (e.g. 52-68 minutes) represent optimistic lower bounds; "
            "actual patient transit burden is frequently 1.5x to 2x greater."
        ),
        uninsured_rate_recency=(
            "American Community Survey (ACS) 5-year rolling estimates lag real-time policy shocks. "
            "Specifically, Georgia's ongoing Medicaid redetermination ('unwinding') and shifts in "
            "low-income safety net qualification mean current uninsured numbers may exceed survey baselines "
            "by 15-25% in high-churn working class tracts."
        )
    )


class ClinicPlanOrchestrator:
    """Orchestrates the sequential multi-agent execution pipeline."""

    def __init__(self, api_key: Optional[str] = None):
        self.planner = PlannerAgent(api_key=api_key)
        self.auditor = AuditorAgent(api_key=api_key)
        self.communicator = CommunicatorAgent(api_key=api_key)

    def run(self) -> ClinicPlan:
        """Execute: Planner (Operational only) -> Auditor (Equity restricted) -> Communicator -> Synthesizer."""
        # 1. Fetch sanitized operational candidate list for Planner
        operational_candidates = get_operational_candidates()

        # Step 1: Execute Planner with STRICT CONTEXT ISOLATION
        planner_output = self.planner.run(operational_candidates)

        # Step 2: Fetch restricted equity data strictly for Auditor
        equity_lookup = get_equity_data_lookup()
        all_candidates = get_full_candidates_lookup()

        # Step 2: Execute Auditor to evaluate chosen sites
        auditor_output = self.auditor.run(planner_output, equity_lookup, all_candidates)

        # Step 3: Execute Communicator for plain-language community text
        communicator_output = self.communicator.run(planner_output, auditor_output)

        # Step 4: Synthesize 4-Part Deliverable
        limitations = generate_limitations_disclosure()

        clinic_plan = ClinicPlan(
            section_1_planner=planner_output,
            section_2_auditor=auditor_output,
            section_3_communicator=communicator_output,
            section_4_limitations=limitations,
        )

        return clinic_plan


def format_plan_as_markdown(plan: ClinicPlan) -> str:
    """Render the 4-part deliverable as a clean, publication-ready Markdown report."""
    md = []
    md.append(f"# {plan.title}")
    md.append(f"**Target Geography:** {plan.target_county}")
    md.append(f"**Operational Scope:** {plan.van_profile}\n")
    md.append("---\n")

    # Section 1
    md.append("## Section 1: Where the Van Goes and Why (Logistics Planner)")
    md.append(f"*{plan.section_1_planner.overall_logistics_summary}*\n")
    md.append("| Week | Neighborhood | Intersection / Landmark | Est. Patients | Operational Rationale |")
    md.append("|---|---|---|---|---|")
    for s in plan.section_1_planner.schedule:
        md.append(f"| Week {s.saturday_index} | **{s.neighborhood_name}** | {s.intersection} | ~{s.estimated_patient_capacity} | {s.operational_rationale} |")
    md.append("\n---\n")

    # Section 2
    md.append("## Section 2: Who the Plan Lands On (Public Health Equity Audit)")
    md.append(f"**Portfolio Equity Score:** {plan.section_2_auditor.overall_equity_score} / 100")
    md.append(f"**Portfolio Uninsured Reach:** {plan.section_2_auditor.portfolio_uninsured_reach_pct}%")
    md.append(f"**Auditor Verdict:** {plan.section_2_auditor.convenience_vs_need_verdict}\n")
    md.append("| Week | Neighborhood | Uninsured Rate | Safety-Net Dist | Transit Time | Desert? | Convenience Trap? | Need Tier | Audit Findings |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for a in plan.section_2_auditor.location_audits:
        trap_str = "⚠️ **YES**" if a.convenience_trap_flag else "✅ No"
        desert_str = "Yes" if a.safety_net_desert else "No"
        md.append(
            f"| Week {a.saturday_index} | **{a.neighborhood_name}** | {a.uninsured_rate_pct}% | "
            f"{a.safety_net_clinic_distance_miles} mi | {a.transit_travel_time_min:.0f} min ({a.bus_transfers_required} transfers) | "
            f"{desert_str} | {trap_str} | {a.equity_need_tier} | {a.audit_findings} |"
        )
    if plan.section_2_auditor.recommended_adjustments:
        md.append("\n**Recommended High-Need Backup Tracts:**")
        for rec in plan.section_2_auditor.recommended_adjustments:
            md.append(f"- {rec}")
    md.append("\n---\n")

    # Section 3
    md.append("## Section 3: Community-Facing Plain-Language Text (Communicator)")
    md.append(f"**Target Reading Level:** {plan.section_3_communicator.reading_level_target}\n")
    md.append(f"> **Public Announcement:**\n>\n> {plan.section_3_communicator.general_community_announcement}\n")
    md.append("### Saturday Community Flyers\n")
    for f in plan.section_3_communicator.flyers:
        md.append(f"#### 🚌 {f.saturday_date_label}: {f.neighborhood}")
        md.append(f"- **Where:** {f.exact_stop_location}")
        md.append(f"- **Transit & Arrival:** {f.how_to_get_there}")
        md.append(f"- **Cost:** **{f.cost_and_insurance_notice}**")
        md.append("- **Services You Can Get:**")
        for serv in f.services_offered:
            md.append(f"  * {serv}")
        md.append(f"- **What to Bring:** {f.what_to_bring}")
        md.append(f"- **Important Notice:** *{f.service_limits_notice}*\n")
    md.append("---\n")

    # Section 4
    md.append("## Section 4: Data Limitations & Resolution Gaps Disclosure")
    md.append("### 1. Ecological Fallacy & Spatial Aggregation")
    md.append(f"{plan.section_4_limitations.ecological_fallacy_risk}\n")
    md.append("### 2. Micro-Spatial Ground-Truth vs 4-Decimal Coordinates")
    md.append(f"{plan.section_4_limitations.spatial_resolution_gap}\n")
    md.append("### 3. Transit Schedule vs Weekend Headway Discrepancies")
    md.append(f"{plan.section_4_limitations.transit_schedule_discrepancy}\n")
    md.append("### 4. Recency Gaps in ACS Data vs Real-Time Medicaid Redetermination")
    md.append(f"{plan.section_4_limitations.uninsured_rate_recency}\n")

    return "\n".join(md)
