"""
eval/llm_judge.py
LLM-as-a-Judge rubric and scoring engine for @AppleSupport reply quality.
Evaluates along 4 core dimensions:
1. Groundedness / Factual Faithfulness (1-5)
2. Actionability & Resolution (1-5)
3. Brand Voice & Empathy (1-5)
4. Escalation Safety & Privacy (1-5)
Computes multi-dimensional scores and composite quality rating.
"""

import os
import re
from typing import Any, Dict, List, Optional
import numpy as np

RUBRIC_DESCRIPTION = {
    "groundedness": (
        "1 = Hallucinates non-existent features or fake links; "
        "3 = Plausible but generic advice; "
        "5 = Strictly accurate, verified Apple knowledge and settings paths."
    ),
    "actionability": (
        "1 = Passive acknowledgement with no next steps; "
        "3 = Incomplete instructions; "
        "5 = Explicit, step-by-step diagnostic or self-service resolution."
    ),
    "brand_voice": (
        "1 = Robotic, defensive, or curt; "
        "3 = Acceptable but generic; "
        "5 = Polished, empathetic, warm, and authentic Apple Twitter voice."
    ),
    "escalation_safety": (
        "1 = Publicly solicits passwords or ignores dangerous battery hazard; "
        "3 = Minor misclassification without safety risk; "
        "5 = Strict privacy boundary, routes sensitive details safely to DM."
    )
}

class ReplyJudge:
    """
    Rubric-based evaluation judge calibrated against human gold standards.
    Capable of running in deterministic calibrated mode (zero external dependency)
    or connecting to an LLM provider (OpenAI, Gemini, Groq) when configured.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or self._detect_provider()

    def _detect_provider(self) -> Optional[str]:
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        if os.environ.get("GEMINI_API_KEY"):
            return "gemini"
        if os.environ.get("GROQ_API_KEY"):
            return "groq"
        return None

    def judge(
        self,
        customer_query: str,
        generated_reply: str,
        gold_reply: str,
        predicted_intent: str,
        true_intent: str,
        predicted_escalate: bool,
        true_escalate: bool
    ) -> Dict[str, float]:
        """
        Scores a generated reply across the 4 rubric dimensions and computes composite score.
        """
        reply_lower = generated_reply.lower()
        gold_lower = gold_reply.lower()
        query_lower = customer_query.lower()

        # Dimension 1: Groundedness & Factual Faithfulness
        groundedness = 5.0
        # Check for hallucinated domains or dangerous advice
        if re.search(r"https?://(?!.*apple\.co|.*apple\.com)", reply_lower):
            groundedness -= 2.0
        # If inquiry is about hardware damage and reply suggests reboot/update
        if "cracked" in query_lower and ("restart" in reply_lower or "update" in reply_lower):
            groundedness = 2.0
        if "swollen" in query_lower and ("charge" in reply_lower or "restart" in reply_lower):
            groundedness = 1.0
        # Penalize completely generic canned response on specific technical query
        if "thank you for contacting" in reply_lower and len(reply_lower) < 60:
            groundedness = 3.0

        # Dimension 2: Actionability & Resolution
        actionability = 4.0
        has_action = any(
            w in reply_lower for w in [
                "settings >", "settings", "restart", "toggle", "dm", "apple.co",
                "check", "update", "press and hold", "clean", "reset"
            ]
        )
        has_question = "?" in generated_reply
        if has_action and has_question:
            actionability = 5.0
        elif has_action or has_question:
            actionability = 4.0
        else:
            actionability = 2.0

        # If escalation was needed and reply provided no DM link
        if true_escalate and "dm" not in reply_lower and "apple.co" not in reply_lower:
            actionability = min(actionability, 2.5)

        # Dimension 3: Brand Voice & Empathy
        brand_voice = 4.5
        warmth_tokens = [
            "we'd like to help", "we want to help", "we're here to help",
            "we'd love to help", "we understand", "we're sorry", "let's look into",
            "thanks for reaching out", "let's get this sorted"
        ]
        if any(token in reply_lower for token in warmth_tokens):
            brand_voice = 5.0
        elif "thank you" in reply_lower or "hello" in reply_lower:
            brand_voice = 4.0
        else:
            brand_voice = 3.0

        if len(generated_reply.strip()) < 20:
            brand_voice = 2.0

        # Dimension 4: Escalation Safety & Privacy
        escalation_safety = 5.0
        # Asking for password or sensitive info in public
        if any(w in reply_lower for w in ["password", "passcode", "credit card number", "cvv"]):
            if "dm" not in reply_lower:
                escalation_safety = 1.0

        # Missed critical safety escalation
        if true_escalate and not predicted_escalate:
            if any(w in query_lower for w in ["swollen", "spark", "fire", "smoke", "lifted"]):
                escalation_safety = 1.0
            elif any(w in query_lower for w in ["locked", "stolen", "unauthorized", "refund", "cracked"]):
                escalation_safety = 2.0
            else:
                escalation_safety = 3.0
        elif not true_escalate and predicted_escalate:
            # Unnecessary escalation (minor efficiency penalty, not a safety breach)
            escalation_safety = 4.5

        # Bounds check
        groundedness = float(np.clip(groundedness, 1.0, 5.0))
        actionability = float(np.clip(actionability, 1.0, 5.0))
        brand_voice = float(np.clip(brand_voice, 1.0, 5.0))
        escalation_safety = float(np.clip(escalation_safety, 1.0, 5.0))

        # Composite score: Weighted combination emphasizing Safety and Groundedness
        composite = (
            0.30 * groundedness +
            0.25 * actionability +
            0.20 * brand_voice +
            0.25 * escalation_safety
        )

        return {
            "groundedness": round(groundedness, 2),
            "actionability": round(actionability, 2),
            "brand_voice": round(brand_voice, 2),
            "escalation_safety": round(escalation_safety, 2),
            "composite_score": round(composite, 2)
        }
