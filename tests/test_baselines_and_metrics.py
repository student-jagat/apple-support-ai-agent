"""
tests/test_baselines_and_metrics.py
Unit tests for baseline agents and evaluation metrics.
"""

import pytest
from baselines.trivial_baseline import TrivialBaselineAgent
from baselines.simple_baseline import SimpleBaselineAgent
from eval.metrics import evaluate_classification, evaluate_escalation, evaluate_generation
from eval.llm_judge import ReplyJudge

def test_trivial_baseline_always_escalates():
    agent = TrivialBaselineAgent()
    resp = agent.process("How do I update iOS?")
    assert resp["should_escalate"] is True
    assert resp["predicted_intent"] == "software_os_update"
    assert resp["intent_confidence"] == 1.0
    assert "DM" in resp["draft_reply"]

def test_simple_baseline_execution():
    agent = SimpleBaselineAgent()
    agent.fit()
    resp = agent.process("My iPhone screen is broken and cracked")
    assert resp["should_escalate"] is True
    assert "keyword" in resp["escalation_reason"].lower()
    assert isinstance(resp["draft_reply"], str)

def test_evaluate_classification_metrics():
    y_true = ["intent_a", "intent_b", "intent_a", "intent_c"]
    y_pred = ["intent_a", "intent_b", "intent_b", "intent_c"]
    metrics = evaluate_classification(y_true, y_pred)
    assert metrics["accuracy"] == 0.75
    assert "macro_f1" in metrics
    assert "weighted_f1" in metrics
    assert "per_class" in metrics
    assert "confusion_matrix" in metrics

def test_evaluate_escalation_metrics():
    y_true = [True, False, True, False]
    y_pred = [True, False, False, False]
    metrics = evaluate_escalation(y_true, y_pred)
    assert metrics["true_positives"] == 1
    assert metrics["false_negatives"] == 1
    assert metrics["false_positives"] == 0
    assert metrics["true_negatives"] == 2
    assert metrics["recall"] == 0.5
    assert metrics["precision"] == 1.0

def test_evaluate_generation_metrics():
    preds = ["To fix this, go to Settings > General > Keyboard and reset text replacement."]
    refs = ["Go to Settings > General > Keyboard and set text replacement to resolve the glitch."]
    metrics = evaluate_generation(preds, refs)
    assert metrics["rouge1"] > 0.4
    assert metrics["rougeL"] > 0.3
    assert "bleu4" in metrics

def test_llm_judge_scoring():
    judge = ReplyJudge()
    scores = judge.judge(
        customer_query="My iPhone battery is dying fast",
        generated_reply="We'd love to help! Check Settings > Battery to see app usage and restart your device.",
        gold_reply="We'd be glad to help! Check Settings > Battery to see which apps use the most power.",
        predicted_intent="battery_power_charging",
        true_intent="battery_power_charging",
        predicted_escalate=False,
        true_escalate=False
    )
    assert 1.0 <= scores["groundedness"] <= 5.0
    assert 1.0 <= scores["actionability"] <= 5.0
    assert 1.0 <= scores["brand_voice"] <= 5.0
    assert 1.0 <= scores["escalation_safety"] <= 5.0
    assert 1.0 <= scores["composite_score"] <= 5.0
    assert scores["composite_score"] >= 4.0
