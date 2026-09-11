"""
baselines/trivial_baseline.py
Baseline 1: Trivial Baseline.
- Intent: Always predicts majority class ('software_os_update').
- Escalation: Always escalates to human ('escalate = True').
- Response: Static generic canned template.
"""

from typing import Any, Dict, List, Optional

class TrivialBaselineAgent:
    """
    Trivial baseline establishing the minimum performance floor.
    Demonstrates the cost of naive policies (100% human queue congestion).
    """

    def __init__(self, default_intent: str = "software_os_update"):
        self.default_intent = default_intent
        self.canned_reply = (
            "Thank you for contacting Apple Support. Please send us a DM with more details "
            "so that we can assist you further: apple.co/DM"
        )

    def process(self, customer_text: str, thread_context: Optional[List[str]] = None) -> Dict[str, Any]:
        return {
            "customer_text": customer_text,
            "predicted_intent": self.default_intent,
            "intent_confidence": 1.0,
            "should_escalate": True,
            "escalation_reason": "Trivial policy default: Always escalate to human agent.",
            "escalation_trigger": "trivial_always_escalate",
            "draft_reply": self.canned_reply,
            "retrieved_resolutions": [],
            "latency_ms": 0.05
        }
