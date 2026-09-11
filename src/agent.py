"""
src/agent.py
Unified AppleSupportAgent orchestrating intent classification,
grounded historical retrieval, reasoned escalation policy, and draft response synthesis.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.data_loader import clean_tweet_text
from src.intent_classifier import IntentClassifier
from src.knowledge_retriever import KnowledgeRetriever, get_default_retriever
from src.escalation_engine import EscalationEngine, EscalationDecision
from src.response_generator import ResponseGenerator

@dataclass
class AgentResponse:
    customer_text: str
    cleaned_text: str
    predicted_intent: str
    intent_confidence: float
    intent_probabilities: Dict[str, float]
    should_escalate: bool
    escalation_reason: str
    escalation_trigger: str
    draft_reply: str
    retrieved_resolutions: List[Dict] = field(default_factory=list)
    latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "customer_text": self.customer_text,
            "cleaned_text": self.cleaned_text,
            "predicted_intent": self.predicted_intent,
            "intent_confidence": round(self.intent_confidence, 4),
            "should_escalate": self.should_escalate,
            "escalation_reason": self.escalation_reason,
            "escalation_trigger": self.escalation_trigger,
            "draft_reply": self.draft_reply,
            "retrieved_resolutions": self.retrieved_resolutions,
            "latency_ms": round(self.latency_ms, 2)
        }


class AppleSupportAgent:
    """
    End-to-end AI Support Agent for @AppleSupport.
    """

    def __init__(
        self,
        classifier: Optional[IntentClassifier] = None,
        retriever: Optional[KnowledgeRetriever] = None,
        escalation_engine: Optional[EscalationEngine] = None,
        generator: Optional[ResponseGenerator] = None
    ):
        # Lazy initialization of models
        if classifier is None:
            from src.intent_classifier import MODEL_PATH
            import os
            classifier = IntentClassifier()
            if os.path.exists(MODEL_PATH):
                classifier.load(MODEL_PATH)
            else:
                from src.intent_classifier import train_default_classifier
                classifier = train_default_classifier()
        self.classifier = classifier

        if retriever is None:
            self.retriever = get_default_retriever()
        else:
            self.retriever = retriever

        self.escalation_engine = escalation_engine or EscalationEngine()
        self.generator = generator or ResponseGenerator()

    def process(
        self,
        customer_text: str,
        thread_context: Optional[List[str]] = None
    ) -> AgentResponse:
        """
        Executes end-to-end agent workflow for an incoming customer message.
        """
        t0 = time.time()
        cleaned = clean_tweet_text(customer_text)

        # 1. Calibrated Intent Classification
        intent, conf, prob_dict = self.classifier.predict(cleaned)

        # 2. Historical Resolution Retrieval
        retrieved = self.retriever.retrieve(cleaned, top_k=2)

        # 3. Reasoned Escalation Policy Evaluation
        escalation = self.escalation_engine.evaluate(
            text=customer_text,
            predicted_intent=intent,
            confidence=conf,
            thread_context=thread_context
        )

        # 4. Grounded Response Draft Synthesis
        reply = self.generator.generate_reply(
            customer_text=customer_text,
            predicted_intent=intent,
            escalation=escalation,
            retrieved_resolutions=retrieved
        )

        latency_ms = (time.time() - t0) * 1000.0

        return AgentResponse(
            customer_text=customer_text,
            cleaned_text=cleaned,
            predicted_intent=str(intent),
            intent_confidence=float(conf),
            intent_probabilities=prob_dict,
            should_escalate=escalation.should_escalate,
            escalation_reason=escalation.stated_reason,
            escalation_trigger=escalation.trigger_category,
            draft_reply=reply,
            retrieved_resolutions=retrieved,
            latency_ms=latency_ms
        )
