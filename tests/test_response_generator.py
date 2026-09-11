"""
tests/test_response_generator.py
Unit tests for grounded response generator, safety prompts, and multilingual handling.
"""

import pytest
from src.response_generator import ResponseGenerator
from src.escalation_engine import EscalationDecision

@pytest.fixture
def generator():
    return ResponseGenerator(use_llm_if_available=False)

def test_safety_escalation_reply_contains_safety_warning(generator):
    escalation = EscalationDecision(
        should_escalate=True,
        stated_reason="Thermal safety hazard",
        trigger_category="safety_hazard"
    )
    reply = generator.generate_reply(
        customer_text="My battery is swelling and hot!",
        predicted_intent="battery_power_charging",
        escalation=escalation,
        retrieved_resolutions=[]
    )
    assert "immediately" in reply.lower() or "safety" in reply.lower()
    assert "apple.co/DM" in reply

def test_account_escalation_reply_protects_privacy(generator):
    escalation = EscalationDecision(
        should_escalate=True,
        stated_reason="PII account recovery",
        trigger_category="account_security_pii"
    )
    reply = generator.generate_reply(
        customer_text="My Apple ID is locked",
        predicted_intent="account_icloud_billing",
        escalation=escalation,
        retrieved_resolutions=[]
    )
    assert "DM" in reply
    assert "apple.co/DM" in reply

def test_spanish_query_generates_spanish_support(generator):
    escalation = EscalationDecision(
        should_escalate=False,
        stated_reason="Auto-handle Spanish",
        trigger_category="auto_handle_eligible"
    )
    reply = generator.generate_reply(
        customer_text="Hola, ¿cómo puedo calibrar la batería de mi iPhone?",
        predicted_intent="battery_power_charging",
        escalation=escalation,
        retrieved_resolutions=[]
    )
    assert "español" in reply.lower() or "apple.co/SoporteES" in reply

def test_french_query_generates_french_support(generator):
    escalation = EscalationDecision(
        should_escalate=False,
        stated_reason="Auto-handle French",
        trigger_category="auto_handle_eligible"
    )
    reply = generator.generate_reply(
        customer_text="Bonjour, mon écran a un problème de tactile",
        predicted_intent="hardware_physical_defect",
        escalation=escalation,
        retrieved_resolutions=[]
    )
    assert "French" in reply or "apple.co/AssistanceFR" in reply

def test_auto_handle_battery_reply_contains_settings_action(generator):
    escalation = EscalationDecision(
        should_escalate=False,
        stated_reason="Auto-handle routine query",
        trigger_category="auto_handle_eligible"
    )
    reply = generator.generate_reply(
        customer_text="My battery is draining quickly after the update",
        predicted_intent="battery_power_charging",
        escalation=escalation,
        retrieved_resolutions=[]
    )
    assert "Settings > Battery" in reply or "Settings" in reply

def test_known_ios11_autocorrect_issue_has_verified_solution(generator):
    escalation = EscalationDecision(
        should_escalate=False,
        stated_reason="Known issue",
        trigger_category="auto_handle_eligible"
    )
    reply = generator.generate_reply(
        customer_text="iOS 11 autocorrect bug types a symbol instead of capital letter I",
        predicted_intent="software_os_update",
        escalation=escalation,
        retrieved_resolutions=[]
    )
    assert "Text Replacement" in reply
    assert "apple.co/TextReplacement" in reply
