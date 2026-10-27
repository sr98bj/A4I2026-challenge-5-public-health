"""
Interactive Prompt Runner for Fulton County Mobile Clinic ADK System.
Allows testing the multi-agent pipeline with various challenge prompts.

Usage:
  python3 run_prompt.py --preset 1    # Baseline 4-Saturday monthly plan
  python3 run_prompt.py --preset 2    # Chronic disease focus (diabetes / hypertension)
  python3 run_prompt.py --preset 3    # Transit desert & vehicle-access focus
  python3 run_prompt.py --preset 4    # Stress-testing the Buckhead/Midtown Convenience Trap
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
        print(f"⚠️ CONVENIENCE TRAPS DETECTED: {len(traps)} site(s) flagged!")
        for t in traps:
            print(f"   - {t.neighborhood_name}: Uninsured {t.uninsured_rate_pct}% (Travel time: {t.transit_travel_time_min} min)")
    else:
        print("✓ All sites confirmed as High/Critical Need.")

    # Step 3: Agent 3 (Communicator)
    print("\n--- [AGENT 3: COMMUNITY ENGAGEMENT COMMUNICATOR] ---")
    print("• Mandate: Translate schedule into plain language, 6th-grade reading level flyers.")
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
    parser.add_argument("--preset", type=int, choices=[1, 2, 3, 4], help="Run one of the preset challenge prompts (1-4).")
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
        print(" [5] Enter your own custom prompt")
        print("=======================================================")

        try:
            choice = input("\nEnter choice [1-5]: ").strip()
            if choice in ["1", "2", "3", "4"]:
                preset = PRESET_PROMPTS[int(choice)]
                run_test_prompt(preset["prompt"], preset["focus"])
            elif choice == "5":
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
