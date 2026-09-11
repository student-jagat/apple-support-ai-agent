"""
tests/test_escalation_engine.py
Unit tests for reasoned multi-factor escalation engine and safety boundaries.
"""

import pytest
from src.escalation_engine import EscalationEngine, EscalationDecision

@pytest.fixture
def engine():
    return EscalationEngine(confidence_threshold=0.38)

def test_safety_hazard_swollen_battery(engine):
    text = "My iPhone battery is swollen and pushing the screen out. Is this dangerous?"
    decision = engine.evaluate(text, predicted_intent="battery_power_charging", confidence=0.85)
    assert decision.should_escalate is True
    assert decision.trigger_category == "safety_hazard"
    assert "safety" in decision.stated_reason.lower()
    assert decision.suggested_routing == "urgent_safety_team"

def test_safety_hazard_sparks_fire(engine):
    text = "Smoke and sparks came out of my charger port while plugged in!"
    decision = engine.evaluate(text, predicted_intent="battery_power_charging", confidence=0.90)
    assert decision.should_escalate is True
    assert decision.trigger_category == "safety_hazard"

def test_security_account_lockout(engine):
    text = "My Apple ID is locked for security reasons and I cannot get 2FA verification code."
    decision = engine.evaluate(text, predicted_intent="account_icloud_billing", confidence=0.92)
    assert decision.should_escalate is True
    assert decision.trigger_category == "account_security_pii"

def test_billing_dispute_double_charge(engine):
    text = "I was charged twice on my credit card without permission for an in-app subscription."
    decision = engine.evaluate(text, predicted_intent="account_icloud_billing", confidence=0.88)
    assert decision.should_escalate is True
    assert decision.trigger_category == "billing_dispute"

def test_hardware_repair_shattered_screen(engine):
    text = "My front screen is shattered and cracked into pieces after I dropped it."
    decision = engine.evaluate(text, predicted_intent="hardware_physical_defect", confidence=0.89)
    assert decision.should_escalate is True
    assert decision.trigger_category == "hardware_repair"

def test_logistics_missing_package(engine):
    text = "UPS tracking says delivered but there is no package at my door. Order is missing!"
    decision = engine.evaluate(text, predicted_intent="order_delivery_tradein", confidence=0.82)
    assert decision.should_escalate is True
    assert decision.trigger_category == "logistics_patterns" or decision.trigger_category == "order_logistics"

def test_churn_risk_manager_demand(engine):
    text = "Your support is useless. Let me speak to a human manager immediately or I am switching to Samsung!"
    decision = engine.evaluate(text, predicted_intent="software_os_update", confidence=0.75)
    assert decision.should_escalate is True
    assert decision.trigger_category == "sentiment_churn_risk"

def test_uncertainty_gating_low_confidence(engine):
    text = "something weird blorp random widget"
    decision = engine.evaluate(text, predicted_intent="software_os_update", confidence=0.25)
    assert decision.should_escalate is True
    assert decision.trigger_category == "model_uncertainty"

def test_routine_auto_handle_software_query(engine):
    text = "How do I clear my Safari cache and website history in Settings?"
    decision = engine.evaluate(text, predicted_intent="software_os_update", confidence=0.85)
    assert decision.should_escalate is False
    assert decision.trigger_category == "auto_handle_eligible"
