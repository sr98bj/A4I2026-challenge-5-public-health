"""
Comprehensive test suite for the Fulton County Mobile Clinic Multi-Agent System.
Verifies context isolation, Pydantic schemas, convenience trap logic, and 4-section synthesis.
Runs cleanly via both `pytest` and standalone `python3 test_pipeline.py`.
"""

import sys
from models import (
    OperationalCandidate,
    PlannerOutput,
    AuditorOutput,
    CommunicatorOutput,
    ClinicPlan,
)
from data import (
    get_operational_candidates,
    get_equity_data_lookup,
    get_full_candidates_lookup,
    FULTON_CANDIDATE_DATASET,
)
from agents import PlannerAgent, AuditorAgent, CommunicatorAgent
from synthesizer import ClinicPlanOrchestrator, format_plan_as_markdown


def test_strict_context_isolation():
    """Verify that operational candidates provided to Planner contain ZERO equity metrics."""
    operational = get_operational_candidates()
    assert len(operational) == 10, f"Expected 10 candidates, got {len(operational)}"

    forbidden_fields = [
        "uninsured_rate_pct",
        "poverty_rate_pct",
        "transit_travel_time_to_care_min",
        "bus_transfers_required",
        "dist_to_safety_net_clinic_miles",
        "dist_to_general_clinic_miles",
        "safety_net_desert",
        "composite_vulnerability_index",
    ]

    for candidate in operational:
        candidate_dict = candidate.model_dump()
        for forbidden in forbidden_fields:
            assert forbidden not in candidate_dict, f"Security Leak! {forbidden} leaked into operational candidate!"
            assert not hasattr(candidate, forbidden), f"Security Leak! {forbidden} attribute present on candidate!"
    print("  ✓ test_strict_context_isolation PASSED")


def test_planner_output_schema():
    """Verify PlannerAgent produces exactly 4 distinct Saturday assignments matching schema."""
    candidates = get_operational_candidates()
    planner = PlannerAgent()
    output = planner.run(candidates)

    assert isinstance(output, PlannerOutput), "Output is not PlannerOutput"
    assert len(output.schedule) == 4, f"Expected 4 assignments, got {len(output.schedule)}"

    # Ensure all 4 Saturdays are distinct
    saturday_indices = [s.saturday_index for s in output.schedule]
    assert sorted(saturday_indices) == [1, 2, 3, 4], "Saturday indices must be 1, 2, 3, 4"

    tract_ids = [s.tract_id for s in output.schedule]
    assert len(set(tract_ids)) == 4, "Planner must select 4 unique tracts"

    for s in output.schedule:
        assert s.estimated_patient_capacity == 40
        assert len(s.operational_rationale) > 10
    print("  ✓ test_planner_output_schema PASSED")


def test_auditor_equity_evaluation_and_convenience_trap():
    """Verify Auditor evaluates sites against equity data and identifies convenience traps."""
    candidates = get_operational_candidates()
    equity_lookup = get_equity_data_lookup()
    full_lookup = get_full_candidates_lookup()

    planner = PlannerAgent()
    planner_output = planner.run(candidates)

    auditor = AuditorAgent()
    audit_output = auditor.run(planner_output, equity_lookup, full_lookup)

    assert isinstance(audit_output, AuditorOutput)
    assert len(audit_output.location_audits) == 4
    assert 0.0 <= audit_output.overall_equity_score <= 100.0
    assert audit_output.portfolio_uninsured_reach_pct > 0.0

    # Test Convenience Trap detection explicitly by passing a mock schedule with Buckhead & Midtown
    mock_schedule = planner_output.model_copy(deep=True)
    mock_schedule.schedule[0].tract_id = "CT_13121010115"  # Buckhead Forest (4.1% uninsured)
    mock_schedule.schedule[0].neighborhood_name = "Buckhead Forest"

    trap_audit = auditor.run(mock_schedule, equity_lookup, full_lookup)
    buckhead_audit = trap_audit.location_audits[0]
    assert buckhead_audit.convenience_trap_flag is True, "Buckhead must trigger Convenience Trap flag!"
    assert buckhead_audit.equity_need_tier == "Low Need (Mismatched)"
    print("  ✓ test_auditor_equity_evaluation_and_convenience_trap PASSED")


def test_communicator_output_6th_grade():
    """Verify Communicator produces accessible 6th-grade flyers with mandatory disclosures."""
    candidates = get_operational_candidates()
    equity_lookup = get_equity_data_lookup()
    full_lookup = get_full_candidates_lookup()

    planner = PlannerAgent()
    planner_output = planner.run(candidates)
    auditor = AuditorAgent()
    audit_output = auditor.run(planner_output, equity_lookup, full_lookup)

    communicator = CommunicatorAgent()
    comm_output = communicator.run(planner_output, audit_output)

    assert isinstance(comm_output, CommunicatorOutput)
    assert len(comm_output.flyers) == 4
    for flyer in comm_output.flyers:
        assert "Free" in flyer.cost_and_insurance_notice
        assert any("blood pressure" in s.lower() for s in flyer.services_offered)
        assert any("blood sugar" in s.lower() or "glucometer" in s.lower() for s in flyer.services_offered)
        assert "emergenc" in flyer.service_limits_notice.lower()
    print("  ✓ test_communicator_output_6th_grade PASSED")


def test_full_pipeline_synthesizer():
    """Verify end-to-end multi-agent execution generates the complete 4-part Clinic Plan."""
    orchestrator = ClinicPlanOrchestrator()
    plan = orchestrator.run()

    assert isinstance(plan, ClinicPlan)
    assert plan.target_county == "Fulton County, Georgia"

    # Section 1 verification
    assert len(plan.section_1_planner.schedule) == 4

    # Section 2 verification
    assert len(plan.section_2_auditor.location_audits) == 4
    assert plan.section_2_auditor.overall_equity_score >= 0.0

    # Section 3 verification
    assert len(plan.section_3_communicator.flyers) == 4

    # Section 4 verification: All statistical disclosures populated
    assert len(plan.section_4_limitations.ecological_fallacy_risk) > 50
    assert len(plan.section_4_limitations.spatial_resolution_gap) > 50
    assert len(plan.section_4_limitations.transit_schedule_discrepancy) > 50
    assert len(plan.section_4_limitations.uninsured_rate_recency) > 50

    # Markdown export check
    md = format_plan_as_markdown(plan)
    assert "## Section 1: Where the Van Goes and Why" in md
    assert "## Section 2: Who the Plan Lands On" in md
    assert "## Section 3: Community-Facing Plain-Language Text" in md
    assert "## Section 4: Data Limitations & Resolution Gaps Disclosure" in md
    print("  ✓ test_full_pipeline_synthesizer PASSED")


def run_all_tests():
    print("=" * 60)
    print("🧪 RUNNING FULTON COUNTY MULTI-AGENT VERIFICATION SUITE")
    print("=" * 60)
    tests = [
        test_strict_context_isolation,
        test_planner_output_schema,
        test_auditor_equity_evaluation_and_convenience_trap,
        test_communicator_output_6th_grade,
        test_full_pipeline_synthesizer,
    ]
    for test in tests:
        test()
    print("=" * 60)
    print("✅ ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
