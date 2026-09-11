"""
scripts/interactive_demo.py
Interactive terminal demo for @AppleSupport AI Agent.
Allows testing queries in real time with side-by-side baseline comparisons,
or running pre-packaged representative queries across the 5 evaluation strata.
"""

import os
import sys
import time

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent import AppleSupportAgent
from baselines.trivial_baseline import TrivialBaselineAgent
from baselines.simple_baseline import SimpleBaselineAgent
from src.data_loader import load_golden_set

PRESET_QUERIES = [
    ("Battery Drainage", "My battery is draining completely within 3 hours after updating to iOS 11."),
    ("Critical Safety", "My iPhone battery is swollen and pushing the glass screen completely off!"),
    ("Account Lockout", "My Apple ID is locked for security reasons and I cannot get 2FA code."),
    ("Hardware Shattered", "I dropped my iPhone on concrete and the front glass is completely shattered."),
    ("Billing Dispute", "I was charged twice on my credit card for an App Store subscription. Refund please!"),
    ("Multilingual (Spanish)", "Hola, ¿cómo puedo calibrar la batería de mi iPhone 7?"),
    ("Churn Threat", "Your automated bots are useless. Let me speak to a human manager or I switch to Android!"),
    ("Known Autocorrect Glitch", "Why does typing the letter I change to a weird symbol on iOS 11.1?")
]

def format_color(text: str, color_code: str) -> str:
    return f"\033[{color_code}m{text}\033[0m"

def print_banner():
    print("\n" + "=" * 80)
    print(format_color("           @AppleSupport AI AGENT INTERACTIVE DEMO           ", "1;36"))
    print("=" * 80)
    print("Commands:")
    print("  Type any customer query to process")
    print("  'preset' : Pick from pre-loaded representative queries across 5 strata")
    print("  'compare': Toggle 3-way side-by-side baseline comparison (on by default)")
    print("  'exit'   : Quit demo\n")

def print_agent_result(query: str, resp, show_comparison: bool, triv_resp=None, simp_resp=None):
    print("\n" + "-" * 80)
    print(format_color("CUSTOMER QUERY: ", "1;33") + query)
    print("-" * 80)

    # Intent
    conf_pct = resp.intent_confidence * 100
    print(f"{format_color('Predicted Intent:', '1;34')} {resp.predicted_intent} "
          f"({conf_pct:.1f}% confidence)")

    # Escalation
    if resp.should_escalate:
        esc_badge = format_color("[ESCALATE TO HUMAN]", "1;31")
    else:
        esc_badge = format_color("[AUTO-HANDLE (SELF-SERVE)]", "1;32")

    print(f"{format_color('Escalation Decision:', '1;34')} {esc_badge}")
    print(f"{format_color('Policy Rationale:', '1;34')} {resp.escalation_reason}")
    print(f"{format_color('Trigger Category:', '1;34')} {resp.escalation_trigger}")

    # Draft Reply
    print(f"\n{format_color('DRAFT AGENT REPLY:', '1;32')}")
    print(f"  \"{resp.draft_reply}\"")

    # Retrieved resolutions
    if resp.retrieved_resolutions:
        print(f"\n{format_color('Grounded Historical Context (Top-1 Match):', '1;36')}")
        top = resp.retrieved_resolutions[0]
        print(f"  - Similarity Score: {top['similarity_score']}")
        print(f"  - Prior Query: {top['historical_customer_query']}")
        print(f"  - Official Links: {', '.join(top['links']) if top['links'] else 'None'}")

    print(f"\n{format_color('Latency:', '90')} {resp.latency_ms:.2f}ms")

    # Side-by-side comparison
    if show_comparison and triv_resp and simp_resp:
        print("\n" + "." * 80)
        print(format_color("SIDE-BY-SIDE BASELINE COMPARISON:", "1;35"))
        print(f"  [Trivial Baseline] -> Intent: {triv_resp['predicted_intent']} | "
              f"Escalate: {triv_resp['should_escalate']} | "
              f"Reply: \"{triv_resp['draft_reply'][:65]}...\"")
        print(f"  [Simple Baseline]  -> Intent: {simp_resp['predicted_intent']} | "
              f"Escalate: {simp_resp['should_escalate']} | "
              f"Reply: \"{simp_resp['draft_reply'][:65]}...\"")
    print("-" * 80 + "\n")

def main():
    print("Loading models and historical retriever index...")
    agent = AppleSupportAgent()
    trivial_agent = TrivialBaselineAgent()
    simple_agent = SimpleBaselineAgent()
    simple_agent.fit()

    show_comparison = True
    print_banner()

    while True:
        try:
            user_input = input(format_color("Enter query > ", "1;32")).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        if user_input.lower() == "compare":
            show_comparison = not show_comparison
            print(f"Side-by-side comparison: {'ENABLED' if show_comparison else 'DISABLED'}")
            continue
        if user_input.lower() == "preset":
            print("\nSelect a preset query:")
            for idx, (label, q) in enumerate(PRESET_QUERIES):
                print(f"  [{idx+1}] {label}: \"{q}\"")
            choice = input("Select number (1-8) or enter to cancel: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(PRESET_QUERIES):
                user_input = PRESET_QUERIES[int(choice)-1][1]
            else:
                continue

        resp = agent.process(user_input)
        triv_resp = trivial_agent.process(user_input) if show_comparison else None
        simp_resp = simple_agent.process(user_input) if show_comparison else None

        print_agent_result(user_input, resp, show_comparison, triv_resp, simp_resp)

if __name__ == "__main__":
    main()
