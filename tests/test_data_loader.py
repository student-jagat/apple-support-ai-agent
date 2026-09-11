"""
tests/test_data_loader.py
Unit tests for data loading, text cleaning, and normalization utilities.
"""

import os
import pytest
from src.data_loader import (
    clean_tweet_text,
    load_corpus,
    load_golden_set,
    get_training_corpus,
    DEFAULT_CORPUS_PATH,
    DEFAULT_GOLDEN_PATH
)

def test_clean_tweet_text_removes_handles():
    raw = "@AppleSupport @115854 My iPhone won't turn on after update!"
    cleaned = clean_tweet_text(raw, keep_mentions=False)
    assert "@AppleSupport" not in cleaned
    assert "@115854" not in cleaned
    assert "My iPhone won't turn on after update!" in cleaned

def test_clean_tweet_text_keeps_mentions_when_flagged():
    raw = "@AppleSupport help please!"
    cleaned = clean_tweet_text(raw, keep_mentions=True)
    assert "@AppleSupport" in cleaned

def test_clean_tweet_text_removes_urls():
    raw = "Check this screenshot https://t.co/abc123XYZ and this link http://example.com"
    cleaned = clean_tweet_text(raw)
    assert "https://" not in cleaned
    assert "http://" not in cleaned

def test_clean_tweet_text_collapses_punctuation_and_whitespace():
    raw = "My phone is frozen!!!!!!!    What should I do????"
    cleaned = clean_tweet_text(raw)
    assert "!" in cleaned
    assert "!!!!!!" not in cleaned
    assert "????" not in cleaned
    assert "    " not in cleaned

def test_clean_tweet_text_handles_empty_and_none():
    assert clean_tweet_text("") == ""
    assert clean_tweet_text(None) == ""
    assert clean_tweet_text("   ") == ""

def test_clean_tweet_text_normalizes_html_entities():
    raw = "iPhone 8 &gt; iPhone 7 &amp; battery &lt; 10%"
    cleaned = clean_tweet_text(raw)
    assert ">" in cleaned
    assert "<" in cleaned
    assert "&" in cleaned
    assert "&gt;" not in cleaned

def test_load_golden_set_structure():
    assert os.path.exists(DEFAULT_GOLDEN_PATH)
    golden = load_golden_set()
    assert len(golden) == 180
    
    first = golden[0]
    required_keys = ["id", "text", "true_intent", "true_escalate", "human_gold_reply", "stratum"]
    for k in required_keys:
        assert k in first, f"Missing key '{k}' in golden sample"

def test_load_corpus_structure():
    assert os.path.exists(DEFAULT_CORPUS_PATH)
    corpus = load_corpus()
    assert len(corpus) > 500
    first = corpus[0]
    assert "customer_text" in first
    assert "agent_text" in first
