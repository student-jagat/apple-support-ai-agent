"""
tests/test_intent_classifier.py
Unit tests for calibrated multi-class intent classification and confidence estimation.
"""

import pytest
from src.intent_classifier import (
    IntentClassifier,
    INTENT_TAXONOMY,
    INTENT_LEXICON,
    train_default_classifier
)

@pytest.fixture(scope="module")
def classifier():
    return train_default_classifier(save=False)

def test_intent_taxonomy_has_six_classes():
    assert len(INTENT_TAXONOMY) == 6
    assert "software_os_update" in INTENT_TAXONOMY
    assert "battery_power_charging" in INTENT_TAXONOMY
    assert "hardware_physical_defect" in INTENT_TAXONOMY
    assert "account_icloud_billing" in INTENT_TAXONOMY
    assert "connectivity_pairing" in INTENT_TAXONOMY
    assert "order_delivery_tradein" in INTENT_TAXONOMY

def test_predict_battery_intent(classifier):
    text = "My battery is draining completely within 2 hours after updating to iOS 11."
    intent, conf, probs = classifier.predict(text)
    assert intent == "battery_power_charging"
    assert conf > 0.40
    assert sum(probs.values()) == pytest.approx(1.0, abs=1e-4)

def test_predict_screen_damage_intent(classifier):
    text = "I dropped my iPhone on concrete and the front screen glass is cracked."
    intent, conf, probs = classifier.predict(text)
    assert intent == "hardware_physical_defect"
    assert conf > 0.40

def test_predict_billing_intent(classifier):
    text = "I was charged twice on my credit card for an App Store subscription. I need a refund."
    intent, conf, probs = classifier.predict(text)
    assert intent == "account_icloud_billing"
    assert conf > 0.40

def test_predict_connectivity_intent(classifier):
    text = "My AirPods keep disconnecting during phone calls and won't pair via Bluetooth."
    intent, conf, probs = classifier.predict(text)
    assert intent == "connectivity_pairing"
    assert conf > 0.40

def test_predict_tradein_intent(classifier):
    text = "Where do I return my trade-in kit and how long do I have to ship it back?"
    intent, conf, probs = classifier.predict(text)
    assert intent == "order_delivery_tradein"
    assert conf > 0.40

def test_predict_empty_text_returns_default_safely(classifier):
    intent, conf, probs = classifier.predict("")
    assert intent == "software_os_update"
    assert conf == 0.0
    assert len(probs) == 6

def test_probability_distribution_sums_to_one(classifier):
    queries = [
        "iPhone won't charge with my lightning cable",
        "How do I reset my Apple ID password",
        "iOS 11 calculator typing bug"
    ]
    for q in queries:
        _, conf, probs = classifier.predict(q)
        assert sum(probs.values()) == pytest.approx(1.0, abs=1e-3)
        assert all(0.0 <= p <= 1.0 for p in probs.values())
