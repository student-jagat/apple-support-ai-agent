"""
tests/test_agent.py
Unit and integration tests for unified AppleSupportAgent.
"""

import pytest
from src.agent import AppleSupportAgent, AgentResponse

@pytest.fixture(scope="module")
def agent():
    return AppleSupportAgent()

def test_agent_process_routine_query(agent):
    query = "My battery is draining really fast after updating to iOS 11. What can I do?"
    resp = agent.process(query)

    assert isinstance(resp, AgentResponse)
    assert resp.customer_text == query
    assert resp.predicted_intent == "battery_power_charging"
    assert resp.intent_confidence > 0.40
    assert resp.should_escalate is False
    assert "Settings > Battery" in resp.draft_reply or "Settings" in resp.draft_reply
    assert resp.latency_ms > 0.0
    assert len(resp.retrieved_resolutions) > 0

def test_agent_process_safety_escalation(agent):
    query = "HELP! My iPhone battery is swollen, bulging out and smoking!"
    resp = agent.process(query)

    assert isinstance(resp, AgentResponse)
    assert resp.should_escalate is True
    assert resp.escalation_trigger == "safety_hazard"
    assert "DM" in resp.draft_reply
    assert "apple.co/DM" in resp.draft_reply

def test_agent_process_billing_escalation(agent):
    query = "Apple charged my credit card twice for an unauthorized subscription. I want a refund now."
    resp = agent.process(query)

    assert isinstance(resp, AgentResponse)
    assert resp.should_escalate is True
    assert resp.escalation_trigger in ("billing_dispute", "account_security_pii", "account_billing_policy")
    assert "DM" in resp.draft_reply

def test_agent_response_to_dict(agent):
    resp = agent.process("How do I update to iOS 11?")
    d = resp.to_dict()

    assert isinstance(d, dict)
    assert "customer_text" in d
    assert "cleaned_text" in d
    assert "predicted_intent" in d
    assert "intent_confidence" in d
    assert "should_escalate" in d
    assert "escalation_reason" in d
    assert "draft_reply" in d
    assert "latency_ms" in d
    assert isinstance(d["predicted_intent"], str)
