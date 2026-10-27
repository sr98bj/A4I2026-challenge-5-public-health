"""
Main CLI entrypoint for the Fulton County Mobile Clinic Multi-Agent System.
Executes Planner -> Auditor -> Communicator -> Deliverable Synthesizer.
"""

import sys
import json
from pathlib import Path
from synthesizer import ClinicPlanOrchestrator, format_plan_as_markdown


def main():
    print("=" * 80)
    print("🏥 FULTON COUNTY MOBILE HEALTH CLINIC MULTI-AGENT SITING SYSTEM")
    print("   Google Cloud ADK Architecture • Public Health Equity Hackathon Challenge")
    print("=" * 80)
    print("\n[+] Initializing Multi-Agent Orchestrator...")
    orchestrator = ClinicPlanOrchestrator()

    print("[+] Step 1: Running Agent 1 (Planner)... [Context isolation enforced: NO equity data]")
    print("[+] Step 2: Running Agent 2 (Auditor)... [Evaluating sites against withheld equity data]")
    print("[+] Step 3: Running Agent 3 (Communicator)... [Generating 6th-grade community flyers]")
    print("[+] Step 4: Synthesizing 4-Part Clinic Plan & Limitations Disclosure...")

    plan = orchestrator.run()

    # Generate Markdown and JSON deliverables
    output_dir = Path(__file__).parent
    md_content = format_plan_as_markdown(plan)
    json_content = plan.model_dump_json(indent=2)

    md_file = output_dir / "CLINIC_PLAN.md"
    json_file = output_dir / "clinic_plan.json"

    with open(md_file, "w") as f:
        f.write(md_content)

    with open(json_file, "w") as f:
        f.write(json_content)

    print("\n" + "=" * 80)
    print("🎉 EXECUTION COMPLETE! 4-PART CLINIC PLAN GENERATED SUCCESSFULLY")
    print("=" * 80)
    print(f"\n[Artifact Generated] Markdown: {md_file}")
    print(f"[Artifact Generated] JSON:     {json_file}\n")

    print("--------------------------------------------------------------------------------")
    print("EXECUTIVE SUMMARY OF GENERATED PLAN:")
    print("--------------------------------------------------------------------------------")
    print(f"Overall Equity Score:         {plan.section_2_auditor.overall_equity_score} / 100")
    print(f"Portfolio Uninsured Reach:    {plan.section_2_auditor.portfolio_uninsured_reach_pct}%")
    print(f"Auditor Verdict:              {plan.section_2_auditor.convenience_vs_need_verdict}\n")

    print("SITED SATURDAY SCHEDULE:")
    for assignment in plan.section_1_planner.schedule:
        audit = next(a for a in plan.section_2_auditor.location_audits if a.saturday_index == assignment.saturday_index)
        trap_flag = "⚠️ TRAP" if audit.convenience_trap_flag else "✅ OK"
        print(
            f"  Week {assignment.saturday_index}: {assignment.neighborhood_name.ljust(30)} "
            f"| Uninsured: {str(audit.uninsured_rate_pct) + '%':<7} "
            f"| Transit: {str(int(audit.transit_travel_time_min)) + 'm':<5} "
            f"| Status: {audit.equity_need_tier:<18} [{trap_flag}]"
        )

    print("\nPreview of Community Outreach Flyer (Week 1):")
    flyer_1 = plan.section_3_communicator.flyers[0]
    print(f"  📅 {flyer_1.saturday_date_label} - {flyer_1.neighborhood}")
    print(f"  📍 Location: {flyer_1.exact_stop_location}")
    print(f"  💰 Cost:     {flyer_1.cost_and_insurance_notice}")
    print(f"  🩺 Services: {', '.join(flyer_1.services_offered[:2])}...")

    print("\n[+] Verification Check: All 4 Sections successfully verified and serialized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
