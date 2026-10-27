"""
Multi-Agent definitions and execution engines following the Google Cloud ADK pattern.
Defines Agent 1 (Planner), Agent 2 (Auditor), and Agent 3 (Communicator) with strict context barriers.
"""

import os
import json
from typing import List, Dict, Any, Optional
from models import (
    OperationalCandidate,
    PlannerOutput,
    SaturdayAssignment,
    AuditorOutput,
    LocationAudit,
    CommunicatorOutput,
    CommunityFlyer,
    EquityMetrics,
)


# ===========================================================================
# System Prompts & Calibrations
# ===========================================================================

PLANNER_SYSTEM_PROMPT = """You are the Lead Logistics & Operations Planner for a mobile health clinic in Fulton County, Georgia.
Your mandate is to site a single mobile medical van across exactly 4 distinct Saturdays in an upcoming month.

OPERATIONAL PARAMETERS:
- Vehicle: High-roof sprinter mobile clinic van (length 24 ft, turning radius 25 ft).
- Patient target: ~40 patients per Saturday (9:00 AM to 3:00 PM).
- Staging required: At least 8-10 contiguous parking spots for van parking, generator clearance, waiting canopy, and patient triage.
- Surface priority: Paved asphalt or level lots with safe pedestrian ingress/egress. Avoid unpaved or permit-restricted bottlenecks unless essential.
- Spatial dispersion: Aim for geographic balance across diverse quadrants (e.g., Westside, South Fulton, South Atlanta) to prevent van clumping.

STRICT CONTEXT BARRIER:
You do NOT have access to income data, poverty metrics, uninsured rates, or demographic indicators.
Base your siting rationales strictly on physical parking feasibility, vehicle ingress, pedestrian safety, and foot traffic.

You must return a structured JSON response matching the PlannerOutput schema with exactly 4 Saturday assignments."""


AUDITOR_SYSTEM_PROMPT = """You are the Senior Public Health Equity Auditor for the Fulton County Department of Health & Human Services.
Your mandate is to evaluate the 4 mobile clinic locations selected by the Logistics Planner against restricted equity and healthcare disparity datasets.

BACKGROUND CONTEXT:
Fulton County has 326 neighborhoods, 135 of which are further from a clinic accepting uninsured patients than from a general clinic.
Mobile health vans are a scarce public health resource. If the van parks in transit-rich or affluent areas simply because parking is convenient, it fails to reach vulnerable, uninsured residents.

AUDIT CRITERIA & CONVENIENCE TRAP DETECTION:
1. Evaluate each selected site using:
   - Uninsured rate (% lacking health coverage)
   - Distance to safety-net clinics (e.g., Grady Health System, FQHCs)
   - Transit travel time and bus transfers required to reach care
2. "Convenience Trap" Flag: Flag `convenience_trap_flag = True` if a location has low uninsured rate (<15%) or quick access to care, yet was chosen because of spacious parking lots (e.g., Midtown, Buckhead, Sandy Springs).
3. Need Tiers:
   - "Critical Need": Uninsured rate >= 22%, safety-net desert or >45 min transit time.
   - "Moderate Need": Uninsured rate 15-21% or moderate transit barriers.
   - "Low Need (Mismatched)": Uninsured rate < 15%, low travel burden.
4. If any site is flagged as Low Need, recommend high-need replacement tracts from the restricted dataset.

You must return a structured JSON response matching the AuditorOutput schema."""


COMMUNICATOR_SYSTEM_PROMPT = """You are the Community Engagement Communicator for the Fulton County Mobile Health Program.
Your role is to translate the audited 4-Saturday mobile clinic schedule into clear, reassuring public communications for residents.

TARGET AUDIENCE:
Community members standing at a MARTA bus stop, local laundromat, recreation center, or library.
Target Reading Level: 6th-grade reading level (Flesch-Kincaid), plain language, direct, and welcoming.

COMMUNICATION CONSTRAINTS:
1. Clinic Scope: Clearly explain services offered: Free nurse practitioner consultation, blood pressure checks, and fingerstick blood glucose (glucometer) testing.
2. Boundaries: Explicitly clarify that the van cannot perform emergency room care, surgeries, or overnight stays.
3. Trust & Access: Reassure residents that care is 100% FREE, with NO health insurance needed, and NO government ID required.
4. Transit Directions: Provide realistic walking and MARTA bus advice for each stop.
5. Tone: Respectful, clear, empathetic, and jargon-free. Avoid medical abbreviations like 'HTN' or 'DM2'.

You must return a structured JSON response matching the CommunicatorOutput schema."""


# ===========================================================================
# Agent 1: Logistics Planner
# ===========================================================================

class PlannerAgent:
    """Agent 1: Logistics & Siting Planner.
    Enforces that only OperationalCandidate data is accepted into the prompt context.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

    def run(self, candidates: List[OperationalCandidate]) -> PlannerOutput:
        """Run the Planner Agent on operational-only data."""
        # Sanity check: Ensure input contains NO equity metrics
        for c in candidates:
            assert not hasattr(c, "uninsured_rate_pct"), "Security breach: Equity data leaked to Planner!"
            assert not hasattr(c, "poverty_rate_pct"), "Security breach: Poverty data leaked to Planner!"

        if self.api_key:
            return self._run_llm(candidates)
        return self._run_deterministic(candidates)

    def _run_deterministic(self, candidates: List[OperationalCandidate]) -> PlannerOutput:
        """High-fidelity deterministic fallback matching ADK contract."""
        # Planner evaluates physical parking capacity, surface type, and foot traffic
        # Priority: large capacity, paved lot, high foot traffic, permit-free
        sorted_candidates = sorted(
            candidates,
            key=lambda c: (
                c.surface_type == "paved lot",
                not c.permit_required,
                c.parking_capacity_spots,
                c.foot_traffic_level == "High"
            ),
            reverse=True
        )

        # Select 4 geographically distributed sites from available quadrants
        selected: List[OperationalCandidate] = []
        quadrants_seen = set()

        for c in sorted_candidates:
            if c.quadrant not in quadrants_seen and len(selected) < 4:
                selected.append(c)
                quadrants_seen.add(c.quadrant)

        # Fill remaining slots if needed
        for c in sorted_candidates:
            if c not in selected and len(selected) < 4:
                selected.append(c)

        schedules = [
            SaturdayAssignment(
                saturday_index=i + 1,
                tract_id=candidate.tract_id,
                neighborhood_name=candidate.neighborhood_name,
                intersection=candidate.intersection,
                operational_rationale=(
                    f"Selected for Week {i+1} based on {candidate.parking_capacity_spots} contiguous spots "
                    f"on {candidate.surface_type}. High pedestrian visibility at {candidate.intersection} "
                    f"with safe turning radius and {'no permit required' if not candidate.permit_required else 'permit pre-cleared'}."
                ),
                estimated_patient_capacity=40
            )
            for i, candidate in enumerate(selected)
        ]

        return PlannerOutput(
            schedule=schedules,
            overall_logistics_summary=(
                "Selected 4 sites balancing vehicle turning radius (25 ft), paved lot staging, "
                "and pedestrian foot traffic across diverse Fulton County sectors. "
                "Each site accommodates a 24-ft mobile clinic van, patient intake canopy, and safe triage zone."
            )
        )

    def _run_llm(self, candidates: List[OperationalCandidate]) -> PlannerOutput:
        """Execute against Gemini API using structured JSON output."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            candidates_json = json.dumps([c.model_dump() for c in candidates], indent=2)

            prompt = (
                f"{PLANNER_SYSTEM_PROMPT}\n\n"
                f"AVAILABLE OPERATIONAL SITES:\n{candidates_json}\n\n"
                "Select exactly 4 distinct sites for Saturdays 1 through 4."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PlannerOutput,
                    temperature=0.2,
                ),
            )
            return PlannerOutput.model_validate_json(response.text)
        except Exception as e:
            # Fallback smoothly to deterministic planner if API call fails
            return self._run_deterministic(candidates)


# ===========================================================================
# Agent 2: Public Health Equity Auditor
# ===========================================================================

class AuditorAgent:
    """Agent 2: Equity & Disparity Auditor.
    Ingests the Planner's 4 selections and joins with the restricted equity dataset.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

    def run(
        self,
        planner_output: PlannerOutput,
        equity_lookup: Dict[str, EquityMetrics],
        all_candidates: Dict[str, Any]
    ) -> AuditorOutput:
        """Evaluate the planned schedule against healthcare accessibility barriers."""
        if self.api_key:
            return self._run_llm(planner_output, equity_lookup, all_candidates)
        return self._run_deterministic(planner_output, equity_lookup, all_candidates)

    def _run_deterministic(
        self,
        planner_output: PlannerOutput,
        equity_lookup: Dict[str, EquityMetrics],
        all_candidates: Dict[str, Any]
    ) -> AuditorOutput:
        """Deterministic public health disparity calculation."""
        location_audits: List[LocationAudit] = []
        total_uninsured = 0.0

        for assignment in planner_output.schedule:
            equity = equity_lookup[assignment.tract_id]
            total_uninsured += equity.uninsured_rate_pct

            # Convenience Trap Detection:
            # Low uninsured rate (<15%) or short transit time (<20 min) with zero bus transfers
            is_convenience_trap = equity.uninsured_rate_pct < 15.0 or (
                equity.dist_to_general_clinic_miles < 0.5 and equity.bus_transfers_required == 0
            )

            if equity.uninsured_rate_pct >= 22.0:
                tier = "Critical Need"
                findings = (
                    f"Strong equity target. Tract has {equity.uninsured_rate_pct:.1f}% uninsured rate "
                    f"and residents face {equity.transit_travel_time_to_care_min:.0f}-minute transit travel time "
                    f"with {equity.bus_transfers_required} bus transfers to reach safety-net care."
                )
            elif equity.uninsured_rate_pct >= 15.0:
                tier = "Moderate Need"
                findings = (
                    f"Moderate disparity index. Uninsured rate is {equity.uninsured_rate_pct:.1f}%. "
                    f"Transit burden is {equity.transit_travel_time_to_care_min:.0f} min."
                )
            else:
                tier = "Low Need (Mismatched)"
                findings = (
                    f"CONVENIENCE MISMATCH: Uninsured rate is only {equity.uninsured_rate_pct:.1f}% "
                    f"and private care is {equity.dist_to_general_clinic_miles:.1f} miles away. "
                    "Selected primarily for ample parking capacity rather than clinical necessity."
                )

            location_audits.append(
                LocationAudit(
                    saturday_index=assignment.saturday_index,
                    tract_id=assignment.tract_id,
                    neighborhood_name=assignment.neighborhood_name,
                    uninsured_rate_pct=equity.uninsured_rate_pct,
                    safety_net_clinic_distance_miles=equity.dist_to_safety_net_clinic_miles,
                    transit_travel_time_min=equity.transit_travel_time_to_care_min,
                    bus_transfers_required=equity.bus_transfers_required,
                    safety_net_desert=equity.safety_net_desert,
                    convenience_trap_flag=is_convenience_trap,
                    equity_need_tier=tier,
                    audit_findings=findings
                )
            )

        avg_uninsured = total_uninsured / len(planner_output.schedule)

        # Equity score calculation (0 to 100):
        # Baseline on average uninsured rate and penalties for convenience trap
        traps = sum(1 for a in location_audits if a.convenience_trap_flag)
        equity_score = min(100.0, max(0.0, (avg_uninsured * 3.5) - (traps * 18.0)))

        # Find high-need replacement candidates not currently in schedule
        sited_tracts = {a.tract_id for a in planner_output.schedule}
        high_need_unsited = [
            f"{all_candidates[tid].operational.neighborhood_name} ({eq.uninsured_rate_pct}% uninsured, {eq.transit_travel_time_to_care_min:.0f}m transit)"
            for tid, eq in equity_lookup.items()
            if tid not in sited_tracts and eq.uninsured_rate_pct >= 22.0
        ]

        if traps > 0:
            verdict = (
                f"CONVENIENCE BIAS DETECTED: {traps} of 4 sited locations exhibit low healthcare barriers. "
                "The Planner favored spacious parking aprons over documented healthcare deserts."
            )
        else:
            verdict = (
                "EQUITY ALIGNED: All 4 sited locations exhibit substantial uninsured rates "
                "and documented safety-net transit barriers. Clinical impact maximized."
            )

        return AuditorOutput(
            location_audits=location_audits,
            overall_equity_score=round(equity_score, 1),
            portfolio_uninsured_reach_pct=round(avg_uninsured, 1),
            convenience_vs_need_verdict=verdict,
            recommended_adjustments=high_need_unsited[:3]
        )

    def _run_llm(
        self,
        planner_output: PlannerOutput,
        equity_lookup: Dict[str, EquityMetrics],
        all_candidates: Dict[str, Any]
    ) -> AuditorOutput:
        """Execute Auditor with Gemini API."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            audit_input = {
                "planner_schedule": [a.model_dump() for a in planner_output.schedule],
                "restricted_equity_data": {k: v.model_dump() for k, v in equity_lookup.items()},
            }

            prompt = (
                f"{AUDITOR_SYSTEM_PROMPT}\n\n"
                f"AUDIT INPUT DATA:\n{json.dumps(audit_input, indent=2)}\n\n"
                "Audit the 4 selections and produce the AuditorOutput schema."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AuditorOutput,
                    temperature=0.2,
                ),
            )
            return AuditorOutput.model_validate_json(response.text)
        except Exception:
            return self._run_deterministic(planner_output, equity_lookup, all_candidates)


# ===========================================================================
# Agent 3: Community Communicator
# ===========================================================================

class CommunicatorAgent:
    """Agent 3: Community Engagement & Plain-Language Communicator.
    Translates audited clinic sites into accessible 6th-grade flyers and notices.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

    def run(self, planner_output: PlannerOutput, auditor_output: AuditorOutput) -> CommunicatorOutput:
        """Generate community-facing plain-language flyers."""
        if self.api_key:
            return self._run_llm(planner_output, auditor_output)
        return self._run_deterministic(planner_output, auditor_output)

    def _run_deterministic(
        self, planner_output: PlannerOutput, auditor_output: AuditorOutput
    ) -> CommunicatorOutput:
        """Deterministic 6th-grade plain-language generator."""
        flyers: List[CommunityFlyer] = []

        services = [
            "Blood pressure check (test for high blood pressure)",
            "Fingerstick blood sugar check (test for diabetes)",
            "Talk with a licensed Nurse Practitioner about how you feel",
            "Help connecting to local community clinics if you need ongoing care"
        ]

        for assignment, audit in zip(planner_output.schedule, auditor_output.location_audits):
            flyers.append(
                CommunityFlyer(
                    saturday_index=assignment.saturday_index,
                    saturday_date_label=f"Saturday Week {assignment.saturday_index} • 9:00 AM – 3:00 PM",
                    neighborhood=assignment.neighborhood_name,
                    exact_stop_location=f"Mobile Health Van at {assignment.intersection}",
                    how_to_get_there=(
                        f"Look for the white health van parked at {assignment.intersection}. "
                        "Accessible by local MARTA bus lines. No stairs needed to enter."
                    ),
                    services_offered=services,
                    cost_and_insurance_notice="100% Free. No health insurance needed. No government ID required.",
                    what_to_bring=(
                        "Bring a list of your current medications or empty medicine bottles if you have them. "
                        "Wear comfortable clothes. Family and walk-ins welcome!"
                    ),
                    service_limits_notice=(
                        "Please note: The mobile van is for preventive checkups and health screenings. "
                        "We do not treat emergency injuries, perform surgeries, or have hospital beds. "
                        "For emergencies, call 911 or visit Grady Memorial Hospital."
                    )
                )
            )

        general_announcement = (
            "FREE COMMUNITY HEALTH CHECKUPS IN FULTON COUNTY THIS MONTH!\n\n"
            "A mobile health clinic van is coming to your neighborhood on Saturdays from 9 AM to 3 PM. "
            "A friendly Nurse Practitioner will check your blood pressure and blood sugar, answer your health questions, "
            "and give you healthy tips. Everything is completely FREE. You do not need health insurance, money, or an ID card. "
            "Walk-ups are welcome—first come, first served for up to 40 neighbors each Saturday. See our schedule below!"
        )

        return CommunicatorOutput(
            reading_level_target="6th Grade (Flesch-Kincaid)",
            flyers=flyers,
            general_community_announcement=general_announcement
        )

    def _run_llm(
        self, planner_output: PlannerOutput, auditor_output: AuditorOutput
    ) -> CommunicatorOutput:
        """Execute Communicator with Gemini API."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            prompt = (
                f"{COMMUNICATOR_SYSTEM_PROMPT}\n\n"
                f"SCHEDULE:\n{planner_output.model_dump_json(indent=2)}\n\n"
                f"AUDIT:\n{auditor_output.model_dump_json(indent=2)}\n\n"
                "Create the community flyer and announcements."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CommunicatorOutput,
                    temperature=0.3,
                ),
            )
            return CommunicatorOutput.model_validate_json(response.text)
        except Exception:
            return self._run_deterministic(planner_output, auditor_output)
