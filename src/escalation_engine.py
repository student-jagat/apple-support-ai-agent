"""
src/escalation_engine.py
Reasoned escalation decision engine for @AppleSupport.
Determines whether an inquiry can be safely auto-handled or must be escalated to a human agent,
enforcing security boundaries, hardware policies, customer churn protection, and uncertainty gating.
"""

import re
from typing import Dict, List, Optional, Tuple

class EscalationDecision:
    def __init__(
        self,
        should_escalate: bool,
        stated_reason: str,
        trigger_category: str,
        suggested_routing: str = "auto_handle"
    ):
        self.should_escalate = should_escalate
        self.stated_reason = stated_reason
        self.trigger_category = trigger_category
        self.suggested_routing = suggested_routing

    def to_dict(self) -> Dict:
        return {
            "should_escalate": self.should_escalate,
            "stated_reason": self.stated_reason,
            "trigger_category": self.trigger_category,
            "suggested_routing": self.suggested_routing
        }


class EscalationEngine:
    """
    Multi-factor deterministic and probabilistic escalation policy engine.
    Ensures safety, confidentiality, brand protection, and support efficiency.
    """

    def __init__(self, confidence_threshold: float = 0.38):
        self.confidence_threshold = confidence_threshold

        # Safety hazard patterns (highest priority)
        self.safety_patterns = [
            r"\b(swollen|swelling|bulging|bulge|expand|expanding)\b.*\bbattery\b",
            r"\bbattery\b.*\b(swollen|swelling|bulging|bulge|expand|expanding)\b",
            r"\b(spark|sparked|sparking|fire|smoke|exploded|exploding|scorched|scorching)\b",
            r"\bburning\s+(hot|up)\b",
            r"\blifting\s+(screen|display)\b",
            r"\bscreen\b.*\b(popped|lifted)\s+off\b",
            r"\b(popped|lifted)\s+off\b"
        ]

        # Security & Authentication (PII) patterns
        self.security_patterns = [
            r"\bapple\s*id\b.*\b(locked|disabled|hacked|compromised|stolen|suspended)\b",
            r"\b(locked|disabled|suspend|suspended)\b.*\bapple\s*id\b",
            r"\b(2fa|two-factor|two\s*factor|verification\s*code|recovery\s*key)\b",
            r"\bforgot\b.*\b(password|passcode|apple\s*id)\b.*\b(recovery|phone|email)\b",
            r"\baccount\s+recovery\b"
        ]

        # Financial & Billing dispute patterns
        self.billing_patterns = [
            r"\b(charged|billed|charging|billing)\b.*\b(twice|double|fraud|unauthorized|without\s+permission)\b",
            r"\b(refund|money\s+back)\b.*\b(charge|charged|spent|purchase|subscription|dollar|\$)\b",
            r"\bunauthorized\s+(charge|purchase|transaction)\b",
            r"\b(card|payment\s+method)\b.*\bdeclined\b",
            r"\bdeclined\b.*\b(card|payment|funds)\b",
            r"\bpayment\s+failed\b",
            r"\bdispute\b.*\b(charge|bank|apple)\b"
        ]

        # Hardware repair patterns
        self.hardware_repair_patterns = [
            r"\b(cracked|shattered|broken|smashed)\b.*\b(screen|glass|display)\b",
            r"\bscreen\b.*\b(cracked|shattered|broken|smashed|green\s+line)\b",
            r"\b(home\s*button|volume\s*button|power\s*button|button)\b.*\b(broken|jammed|stuck|dead|not\s+working|doesn't\s+work|doesnt\s+work|depressed|no\s+haptic)\b",
            r"\b(keyboard|spacebar|key)\b.*\b(stuck|repeating|double\s+space|not\s+working)\b",
            r"\b(bluetooth|wi-?fi)\b.*\b(greyed|grayed)\s+out\b",
            r"\b(shutting|shuts?|dying|dies?)\s+(off\s+|down\s+)?at\s+\d{1,2}%",
            r"\b(dropped|fell)\b.*\b(sink|water|pool|toilet|bath|ocean)\b",
            r"\bwater\s+damage\b",
            r"\bcamera\b.*\b(buzzing|vibrating|shaking|clicking)\b",
            r"\bface\s*id\s+is\s+not\s+available\b",
            r"\bcellular\s+update\s+failed\b",
            r"\bservice\s+battery\b",
            r"\brepair\s+(quote|id|status)\b"
        ]

        # Logistics / Order failure patterns
        self.logistics_patterns = [
            r"\b(tracking|package|delivery|shipment)\b.*\b(missing|stolen|empty\s+box|not\s+delivered|nowhere)\b",
            r"\bdelivered\b.*\b(nothing|no\s+package|not\s+here)\b",
            r"\border\b.*\b(cancelled|canceled|wrong\s+address|preparing\s+for\s+shipment)\b",
            r"\border\s+status\b",
            r"\bwrong\s+(delivery\s+|shipping\s+)?address\b",
            r"\b(never\s+received|missing)\b.*\b(return\s+box|trade-?in\s+kit|box|package)\b",
            r"\btrade-?in\b.*\b(valuation|quote|dropped|lower)\b",
            r"\b(reserved|reservation|order|delivery)\b.*\b(delayed|discrepancy|wrong\s+date|different\s+date|what\s+happened)\b"
        ]

        # Churn risk & extreme agitation patterns
        self.sentiment_churn_patterns = [
            r"\bswitching\s+to\s+(samsung|android|google|pixel)\b",
            r"\bbuying\s+(a\s+)?(samsung|android|google|pixel)\b",
            r"\b(worst|disgusted|trash|incompetence|scam|thieves|criminal)\b",
            r"\b(speak|talk)\s+to\s+(a\s+)?(human|person|agent|manager|supervisor)\b",
            r"\b(stop|hate)\s+(sending\s+)?(bots?|robots?|automated)\b",
            r"\b(lawyer|attorney|lawsuit|small\s+claims|better\s+business\s+bureau|bbb|court)\b",
            r"\btweeted\s+(you\s+)?(several|multiple|[3-9]|\d{2})\s+times\b"
        ]

    def evaluate(
        self,
        text: str,
        predicted_intent: str,
        confidence: float,
        thread_context: Optional[List[str]] = None
    ) -> EscalationDecision:
        """
        Evaluates incoming customer tweet and returns reasoned escalation decision.
        """
        lower = text.lower()

        # 1. Critical Physical Safety Hazards
        for pattern in self.safety_patterns:
            if re.search(pattern, lower):
                return EscalationDecision(
                    should_escalate=True,
                    stated_reason="Critical physical safety hazard detected (battery swelling / thermal / fire risk). Immediate human intervention required.",
                    trigger_category="safety_hazard",
                    suggested_routing="urgent_safety_team"
                )

        # 2. Account Security & Confidential Authentication (PII)
        for pattern in self.security_patterns:
            if re.search(pattern, lower):
                return EscalationDecision(
                    should_escalate=True,
                    stated_reason="Involves confidential account credentials, Apple ID recovery, or 2FA authentication that cannot be conducted in a public forum.",
                    trigger_category="account_security_pii",
                    suggested_routing="dm_security_support"
                )

        # 3. Financial & Billing Disputes
        for pattern in self.billing_patterns:
            if re.search(pattern, lower):
                return EscalationDecision(
                    should_escalate=True,
                    stated_reason="Financial billing dispute, unauthorized charges, or refund audit requiring private order/credit lookup.",
                    trigger_category="billing_dispute",
                    suggested_routing="dm_billing_specialist"
                )

        # 4. Irreversible Physical Hardware Defect
        for pattern in self.hardware_repair_patterns:
            if re.search(pattern, lower):
                return EscalationDecision(
                    should_escalate=True,
                    stated_reason="Physical hardware damage or component malfunction requiring hands-on Genius Bar inspection or mail-in repair.",
                    trigger_category="hardware_repair",
                    suggested_routing="dm_genius_bar_scheduling"
                )

        # 5. Order Logistics & Missing Deliveries
        for pattern in self.logistics_patterns:
            if re.search(pattern, lower):
                return EscalationDecision(
                    should_escalate=True,
                    stated_reason="Order shipping discrepancy, carrier investigation, or transit theft requiring private order tracking.",
                    trigger_category="order_logistics",
                    suggested_routing="dm_logistics_specialist"
                )

        # 6. Customer Sentiment Volatility / High Churn Risk
        for pattern in self.sentiment_churn_patterns:
            if re.search(pattern, lower):
                return EscalationDecision(
                    should_escalate=True,
                    stated_reason="Severe customer dissatisfaction, churn risk (competitor defection), or explicit demand for human manager intervention.",
                    trigger_category="sentiment_churn_risk",
                    suggested_routing="dm_priority_customer_care"
                )

        # 7. Intent-Level Policy Rules
        # Certain intents are escalated by default unless clearly a general FAQ
        if predicted_intent == "hardware_physical_defect":
            # If explicit physical damage terms
            if any(w in lower for w in ["cracked", "shattered", "water", "dropped", "broken", "bent", "button", "screen", "keyboard", "spacebar", "buzzing", "camera", "popped", "depressed", "haptic", "taptic"]):
                return EscalationDecision(
                    should_escalate=True,
                    stated_reason="Physical hardware failure classified under hardware_physical_defect requiring authorized hardware inspection.",
                    trigger_category="hardware_policy",
                    suggested_routing="dm_genius_bar_scheduling"
                )

        if predicted_intent == "account_icloud_billing":
            if any(w in lower for w in ["locked", "refund", "charged", "stolen", "dispute", "password"]):
                return EscalationDecision(
                    should_escalate=True,
                    stated_reason="Account security or transaction dispute requiring authenticated lookup.",
                    trigger_category="account_billing_policy",
                    suggested_routing="dm_security_support"
                )

        # 8. Model Uncertainty Gating
        if confidence < self.confidence_threshold:
            return EscalationDecision(
                should_escalate=True,
                stated_reason=f"Classifier confidence ({confidence:.2f}) is below safe auto-handling threshold ({self.confidence_threshold:.2f}). Escalating to human triage to avoid misrouting.",
                trigger_category="model_uncertainty",
                suggested_routing="human_triage_queue"
            )

        # Default: Safe for Auto-Handling with Knowledge Base & Diagnostic Guidance
        return EscalationDecision(
            should_escalate=False,
            stated_reason="Routine technical inquiry suitable for automated knowledge base resolution and self-service diagnostics.",
            trigger_category="auto_handle_eligible",
            suggested_routing="automated_response"
        )
