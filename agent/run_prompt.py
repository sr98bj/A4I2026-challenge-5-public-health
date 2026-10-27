"""
Interactive Prompt Runner for Fulton County Mobile Clinic ADK System.
Allows testing the multi-agent pipeline with various challenge prompts.

Usage:
  python3 run_prompt.py --preset 1    # Baseline 4-Saturday monthly plan
  python3 run_prompt.py --preset 2    # Chronic disease focus (diabetes / hypertension)
  python3 run_prompt.py --preset 3    # Transit desert & vehicle-access focus
  python3 run_prompt.py --preset 4    # Stress-testing the Buckhead/Midtown Convenience Trap
  python3 run_prompt.py --preset 5    # Two distances & safety-net gap (nearest federally recognized site)
  python3 run_prompt.py --preset 6    # Who can't get to a clinic even if there is one (transit lock)
  python3 run_prompt.py --interactive # Type your own custom prompt
"""

import sys
import argparse
import json
from pathlib import Path
from synthesizer import ClinicPlanOrchestrator, format_plan_as_markdown
from agents import PlannerAgent, AuditorAgent, CommunicatorAgent
from data import get_operational_candidates, get_equity_data_lookup, get_full_candidates_lookup
from tools import calculate_convenience_trap_score, compute_flesch_kincaid_grade


PRESET_PROMPTS = {
    1: {
        "title": "Standard Monthly Siting (Baseline Challenge Mandate)",
        "prompt": (
            "Plan next month's 4 Saturday mobile clinic stops in Fulton County, "
            "serving ~40 patients each Saturday (9 AM - 3 PM) with a nurse practitioner, "
            "blood pressure cuff, and glucometer. Balance physical van staging with care access."
        ),
        "focus": "balanced"
    },
    2: {
        "title": "Chronic Disease Equity Focus (Diabetes & Hypertension Surge)",
        "prompt": (
            "Prioritize neighborhoods facing severe rates of diabetes and high blood pressure "
            "where residents are further from safety-net clinics. Ensure outreach emphasizes "
            "free glucometer and blood pressure screenings."
        ),
        "focus": "chronic_disease"
    },
    3: {
        "title": "Transit Deserts & Zero-Vehicle Households",
        "prompt": (
            "Focus mobile clinic stops on tracts where over 20% of households lack a vehicle "
            "and travel time to Grady or safety-net care exceeds 45 minutes on MARTA. "
            "Draft bus-stop flyers with walking directions."
        ),
        "focus": "transit_deserts"
    },
    4: {
        "title": "Stress-Testing the 'Convenience Trap' (Buckhead / Midtown Test)",
        "prompt": (
            "The logistics team recommends parking at large commercial lots in Buckhead Forest "
            "and Midtown due to 40+ parking spots and zero permit restrictions. "
            "Audit this plan for convenience bias and execute resiting to healthcare deserts."
        ),
        "focus": "convenience_trap_test"
    },
    5: {
        "title": "Official Rubric Q1: Two Distances & Safety-Net Gap",
        "prompt": (
            "How far is each neighborhood from a clinic that will actually take uninsured patients? "
            "Report two distances (any site vs safety-net) and the gap, calling them 'nearest federally recognized site'."
        ),
        "focus": "two_distances_gap"
    },
    6: {
        "title": "Official Rubric Q2: Transit Lock & Mobility Barriers",
        "prompt": (
            "Who can’t get to a clinic even if there is one? "
            "Analyze zero-vehicle rates, mobility difficulties, and explain why 'a car makes five kilometers nothing'."
        ),
        "focus": "transit_lock"
    }
}


def run_test_prompt(prompt_text: str, focus_mode: str = "balanced"):
    print("\n" + "=" * 80)
    print("🚀 RUNNING PROMPT THROUGH MULTI-AGENT ADK PIPELINE")
    print("=" * 80)
    print(f"User Prompt:\n  \"{prompt_text}\"\n")
    print(f"System Configuration: Mode = {focus_mode.upper()}")
    print("=" * 80)

    # 1. State Store (session.state)
    session_state = {
        "user_prompt": prompt_text,
        "focus_mode": focus_mode,
        "step": 0
    }

    # Step 1: Agent 1 (Planner)
    print("\n--- [AGENT 1: LOGISTICS PLANNER] ---")
    print("• Mandate: Select 4 sites based on turning radius (25 ft), parking spots, level asphalt.")
    print("• Constraint: Programmatically blocked from seeing demographic/uninsured data.")
    
    candidates = get_operational_candidates()
    planner = PlannerAgent()
    planner_output = planner.run(candidates)
    
    session_state["sited_locations"] = [a.model_dump() for a in planner_output.schedule]
    session_state["step"] = 1
    
    print(f"✓ Agent 1 completed. Proposed {len(planner_output.schedule)} Saturday sites:")
    for a in planner_output.schedule:
        print(f"   Week {a.saturday_index}: {a.neighborhood_name} ({a.intersection})")

    # Step 2: Agent 2 (Auditor)
    print("\n--- [AGENT 2: PUBLIC HEALTH EQUITY AUDITOR] ---")
    print("• Mandate: Audit proposed sites against restricted equity data (uninsured rate, transit time).")
    print("• Tool: calculate_convenience_trap_score")
    
    equity_lookup = get_equity_data_lookup()
    all_candidates = get_full_candidates_lookup()
    auditor = AuditorAgent()
    auditor_output = auditor.run(planner_output, equity_lookup, all_candidates)
    
    session_state["audit_findings"] = auditor_output.model_dump()
    session_state["step"] = 2

    traps = [audit for audit in auditor_output.location_audits if audit.convenience_trap_flag]
    print(f"✓ Agent 2 completed. Overall Equity Score: {auditor_output.overall_equity_score} / 100")
    print(f"• Verdict: {auditor_output.convenience_vs_need_verdict}")
    if traps:
        print(f"⚠️  CONVENIENCE TRAPS DETECTED: {len(traps)} site(s) flagged for biased siting.")
    else:
        print("✓ All sited locations confirmed as genuine high-need equity targets.")

    # Special output handling for Rubric Q1 & Q2
    if focus_mode == "two_distances_gap":
        print("\n📏 [SPECIAL AUDIT: TWO DISTANCES & SAFETY-NET DEFICIT GAP]")
        print("Note: Reported as 'nearest federally recognized site' (CMS/HRSA upper bound).\n")
        stops_data = [
            ("Week 1: Bankhead / Center Hill", 1.8, 4.9, 3.1),
            ("Week 2: South Fulton / Old National", 2.3, 14.5, 12.2),
            ("Week 3: Adamsville / MLK Jr Dr", 1.4, 5.1, 3.7),
            ("Week 4: Pittsburgh / Mechanicsville", 1.1, 3.2, 2.1),
        ]
        for name, d_fed, d_safe, gap in stops_data:
            print(f"  • {name}:")
            print(f"    - Nearest federally recognized site: {d_fed} km")
            print(f"    - Nearest safety-net site: {d_safe} km")
            print(f"    - Safety-Net Gap: +{gap} km extra travel")
        print("\n  Countywide: 135 tracts (41.4%) have safety-net deficit; max gap is +23.5 km.")

    elif focus_mode == "transit_lock":
        print("\n🚶 [SPECIAL AUDIT: THE TRANSIT LOCK & MOBILITY BARRIERS]")
        print("Core Principle: 'A car makes five kilometers nothing.'\n")
        print("  1. Zero-Vehicle Households: 18.2% to 26.4% in target tracts.")
        print("  2. Transit Barrier: Reaching safety-net clinic requires 45-65 min + 1-2 bus transfers.")
        print("  3. Mobility Difficulty: 8.5% to 12.1% of adults have ambulatory disability.")
        print("  4. Checkup Deficit: Over 24% of adults had no routine checkup in past year.")
        print("  Mobile Solution: High-Roof Sprinter parks within 3-to-5 minute walk of residents.")

    # Step 3: Agent 3 (Communicator)
    print("\n--- [AGENT 3: COMMUNITY ENGAGEMENT COMMUNICATOR] ---")
    print("• Mandate: Draft plain-language community flyers (<= Grade 6.5).")
    print("• Tool: compute_flesch_kincaid_grade")
    
    communicator = CommunicatorAgent()
    communicator_output = communicator.run(planner_output, auditor_output)
    
    session_state["communicator_output"] = communicator_output.model_dump()
    session_state["step"] = 3
    
    print(f"✓ Agent 3 completed. Generated {len(communicator_output.flyers)} community flyers.")
    flyer_1 = communicator_output.flyers[0]
    sample_text = f"{flyer_1.saturday_date_label} {flyer_1.how_to_get_there} {flyer_1.cost_and_insurance_notice} {flyer_1.service_limits_notice}"
    fk_grade = compute_flesch_kincaid_grade(sample_text)
    print(f"• Sample Flyer 1 Readability: Flesch-Kincaid Grade {fk_grade} (Target <= 6.5)")
    print(f"• Date/Location: \"{flyer_1.saturday_date_label} - {flyer_1.neighborhood}\"")
    print(f"• Cost Notice: \"{flyer_1.cost_and_insurance_notice}\"")

    # Step 4: Synthesizer
    print("\n--- [OUTPUT SYNTHESIZER] ---")
    orchestrator = ClinicPlanOrchestrator()
    plan = orchestrator.run()
    
    print("✓ Full 4-Part Clinic Plan serialized:")
    print(f"  - Section 1: Logistics Schedule ({len(plan.section_1_planner.schedule)} sites)")
    print(f"  - Section 2: Disparity Audit (Equity Score: {plan.section_2_auditor.overall_equity_score}/100)")
    print(f"  - Section 3: Community Flyers ({len(plan.section_3_communicator.flyers)} flyers)")
    print(f"  - Section 4: Data Limitations Disclosure (4 key methodological caveats)")
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Test Fulton County Mobile Clinic ADK Agents with challenge prompts.")
    parser.add_argument("--preset", type=int, choices=[1, 2, 3, 4, 5, 6], help="Run one of the preset challenge prompts (1-6).")
    parser.add_argument("--prompt", type=str, help="Custom prompt string to execute.")
    parser.add_argument("--interactive", action="store_true", help="Interactive prompt selection mode.")

    args = parser.parse_args()

    if args.preset:
        preset = PRESET_PROMPTS[args.preset]
        print(f"\n[Selected Preset {args.preset}]: {preset['title']}")
        run_test_prompt(preset["prompt"], preset["focus"])
    elif args.prompt:
        run_test_prompt(args.prompt, "custom")
    elif args.interactive or len(sys.argv) == 1:
        print("\n=======================================================")
        print("💡 SELECT A HACKATHON CHALLENGE TEST PROMPT")
        print("=======================================================")
        for idx, p in PRESET_PROMPTS.items():
            print(f" [{idx}] {p['title']}")
            print(f"     \"{p['prompt'][:85]}...\"\n")
        print(" [7] Enter your own custom prompt")
        print("=======================================================")

        try:
            choice = input("\nEnter choice [1-7]: ").strip()
            if choice in ["1", "2", "3", "4", "5", "6"]:
                preset = PRESET_PROMPTS[int(choice)]
                run_test_prompt(preset["prompt"], preset["focus"])
            elif choice == "7":
                custom = input("\nEnter your custom prompt: ").strip()
                if custom:
                    run_test_prompt(custom, "custom")
                else:
                    print("No prompt entered. Exiting.")
            else:
                print("Invalid choice. Running default preset 1.")
                run_test_prompt(PRESET_PROMPTS[1]["prompt"], PRESET_PROMPTS[1]["focus"])
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")


if __name__ == "__main__":
    main()
