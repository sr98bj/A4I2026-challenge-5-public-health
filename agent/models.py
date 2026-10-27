"""
Data contracts and Pydantic schemas for the Fulton County Mobile Clinic Multi-Agent System.
Enforces strict schema separation between operational feasibility and equity metrics.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. Raw & Projection Candidate Models
# ---------------------------------------------------------------------------

class EquityMetrics(BaseModel):
    """Restricted demographic, economic, and healthcare accessibility metrics.
    STRICTLY WITHHELD FROM AGENT 1 (Planner).
    """
    uninsured_rate_pct: float = Field(
        ..., description="Percentage of adult population lacking health insurance (0-100)"
    )
    poverty_rate_pct: float = Field(
        ..., description="Percentage of population living below federal poverty line"
    )
    transit_travel_time_to_care_min: float = Field(
        ..., description="Average transit travel time to nearest primary care facility (minutes)"
    )
    bus_transfers_required: int = Field(
        ..., description="Number of MARTA bus/rail transfers needed to reach safety-net care"
    )
    dist_to_safety_net_clinic_miles: float = Field(
        ..., description="Straight-line distance to nearest safety-net clinic (e.g. Grady primary care, FQHC)"
    )
    dist_to_general_clinic_miles: float = Field(
        ..., description="Distance to any general clinic (commercial or private)"
    )
    safety_net_desert: bool = Field(
        ..., description="True if tract is further from safety-net clinic than general clinic"
    )
    composite_vulnerability_index: float = Field(
        ..., description="Overall social/health vulnerability index (0.0 to 1.0, 1.0 = highest need)"
    )


class OperationalCandidate(BaseModel):
    """Sanitized operational data permissible for Agent 1 (Planner).
    Zero equity, demographic, or uninsured attributes are present here.
    """
    tract_id: str = Field(..., description="Census tract identifier (e.g. 'CT_13121008200')")
    neighborhood_name: str = Field(..., description="Common neighborhood name in Fulton County")
    intersection: str = Field(..., description="Proposed intersection / landmark for van parking")
    quadrant: str = Field(..., description="Geographic quadrant (e.g. 'South Fulton', 'Westside', 'North Fulton')")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    parking_capacity_spots: int = Field(..., description="Number of contiguous parking spots available")
    surface_type: str = Field(..., description="Parking surface: asphalt, gravel, street curb, paved lot")
    permit_required: bool = Field(..., description="Whether a special municipal parking permit is required")
    foot_traffic_level: str = Field(..., description="Qualitative Saturday foot traffic: Low, Moderate, High")
    operational_notes: str = Field(..., description="Physical van clearance and accessibility details")


class NeighborhoodCandidate(BaseModel):
    """Complete candidate tract combining operational feasibility and equity metrics.
    Stored in database / master registry; partitioned by context boundary.
    """
    operational: OperationalCandidate
    equity: EquityMetrics


# ---------------------------------------------------------------------------
# 2. Agent 1 (Planner) Output Schema
# ---------------------------------------------------------------------------

class SaturdayAssignment(BaseModel):
    """Planner's selection for a single Saturday in the monthly cycle."""
    saturday_index: int = Field(..., ge=1, le=4, description="Saturday week index (1 to 4)")
    tract_id: str = Field(..., description="Selected census tract ID")
    neighborhood_name: str = Field(..., description="Neighborhood name")
    intersection: str = Field(..., description="Specific parking street intersection or facility")
    operational_rationale: str = Field(
        ..., description="Why this site was chosen based on physical parking, turning radius, and safety"
    )
    estimated_patient_capacity: int = Field(
        default=40, description="Target capacity (~40 patients per Saturday)"
    )


class PlannerOutput(BaseModel):
    """Structured output returned by Agent 1 (Planner).
    Contains exactly 4 distinct Saturday site assignments.
    """
    schedule: List[SaturdayAssignment] = Field(
        ..., min_length=4, max_length=4, description="Exactly 4 distinct Saturday assignments"
    )
    overall_logistics_summary: str = Field(
        ..., description="Logistics coordinator summary explaining route feasibility and vehicle staging"
    )


# ---------------------------------------------------------------------------
# 3. Agent 2 (Auditor) Output Schema
# ---------------------------------------------------------------------------

class LocationAudit(BaseModel):
    """Equity audit assessment for a single sited location."""
    saturday_index: int
    tract_id: str
    neighborhood_name: str
    uninsured_rate_pct: float
    safety_net_clinic_distance_miles: float
    transit_travel_time_min: float
    bus_transfers_required: int
    safety_net_desert: bool
    convenience_trap_flag: bool = Field(
        ..., description="Flagged if high parking convenience was chosen despite low healthcare need"
    )
    equity_need_tier: str = Field(
        ..., description="Assessment of clinical need: 'Critical Need', 'Moderate Need', 'Low Need (Mismatched)'"
    )
    audit_findings: str = Field(
        ..., description="Detailed disparity evaluation comparing clinical need vs convenience"
    )


class AuditorOutput(BaseModel):
    """Structured equity evaluation returned by Agent 2 (Auditor)."""
    location_audits: List[LocationAudit] = Field(
        ..., description="Audits for each of the 4 planned locations"
    )
    overall_equity_score: float = Field(
        ..., ge=0.0, le=100.0, description="Overall portfolio equity alignment score (0-100)"
    )
    portfolio_uninsured_reach_pct: float = Field(
        ..., description="Estimated population-weighted uninsured rate across the 4 locations"
    )
    convenience_vs_need_verdict: str = Field(
        ..., description="Summary of whether mobile resources are deployed equitably or trapped in convenience"
    )
    recommended_adjustments: List[str] = Field(
        ..., description="Actionable replacement tracts if any sited locations fail equity benchmarks"
    )


# ---------------------------------------------------------------------------
# 4. Agent 3 (Communicator) Output Schema
# ---------------------------------------------------------------------------

class CommunityFlyer(BaseModel):
    """Accessible, 6th-grade reading level flyer for a specific Saturday location."""
    saturday_index: int
    saturday_date_label: str = Field(..., description="e.g. 'Saturday Week 1 - 9:00 AM to 3:00 PM'")
    neighborhood: str
    exact_stop_location: str = Field(..., description="Simple landmark or intersection")
    how_to_get_there: str = Field(
        ..., description="Plain-language transit advice (e.g. 'Across from MARTA bus stop #3, walk 50 steps')"
    )
    services_offered: List[str] = Field(
        ..., description="Exact nurse practitioner screenings (blood pressure, blood sugar/glucometer, basic checkup)"
    )
    cost_and_insurance_notice: str = Field(
        ..., description="Clear assurance: Free, no insurance needed, no ID required"
    )
    what_to_bring: str = Field(
        ..., description="Plain advice: list of current medicines or empty pill bottles, water, comfortable shoes"
    )
    service_limits_notice: str = Field(
        ..., description="Clear explanation that this van does not provide emergency surgery or hospital beds"
    )


class CommunicatorOutput(BaseModel):
    """Plain-language communication suite returned by Agent 3."""
    reading_level_target: str = Field(default="6th Grade (Flesch-Kincaid)")
    flyers: List[CommunityFlyer] = Field(
        ..., description="Flyers for the 4 sited Saturdays"
    )
    general_community_announcement: str = Field(
        ..., description="Overarching announcement for community boards, churches, and radio"
    )


# ---------------------------------------------------------------------------
# 5. Final Synthesizer Deliverable Schema
# ---------------------------------------------------------------------------

class DataLimitationsDisclosure(BaseModel):
    """Section 4: Rigorous disclosure on resolution gaps and statistical limitations."""
    ecological_fallacy_risk: str = Field(
        ..., description="Why census tract aggregates can obscure micro-pockets of vulnerability or wealth"
    )
    spatial_resolution_gap: str = Field(
        ..., description="Why 4-decimal coordinates (approx 11m) do not guarantee physical parking realities"
    )
    transit_schedule_discrepancy: str = Field(
        ..., description="Disparities between published transit timetables and weekend MARTA headways"
    )
    uninsured_rate_recency: str = Field(
        ..., description="Limitations of ACS 5-year rolling survey estimates vs current post-Medicaid unwinding reality"
    )


class ClinicPlan(BaseModel):
    """The synthesized 4-Part Mobile Clinic Plan deliverable."""
    title: str = Field(default="Fulton County Mobile Health Clinic 4-Saturday Equity Deployment Plan")
    target_county: str = Field(default="Fulton County, Georgia")
    van_profile: str = Field(
        default="1 Van, 1 Nurse Practitioner, Blood Pressure Cuff, Glucometer, ~40 Patients/Day"
    )
    section_1_planner: PlannerOutput = Field(..., description="Section 1: Where the van goes and why")
    section_2_auditor: AuditorOutput = Field(..., description="Section 2: Who the plan lands on / Disparity audit")
    section_3_communicator: CommunicatorOutput = Field(..., description="Section 3: Community-facing plain text")
    section_4_limitations: DataLimitationsDisclosure = Field(..., description="Section 4: Data limitations & resolution gaps")
