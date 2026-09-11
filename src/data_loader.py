"""
src/data_loader.py
Data loading, cleaning, handle stripping, text normalization,
and thread reconstruction utilities for the Apple Support AI agent.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
import pandas as pd

DEFAULT_CORPUS_PATH = os.path.join("data", "apple_support_corpus.json")
DEFAULT_GOLDEN_PATH = os.path.join("data", "golden_eval_set.json")

def clean_tweet_text(text: str, keep_mentions: bool = False) -> str:
    """
    Cleans raw customer tweet text:
    - Normalizes unicode spaces and variation selectors
    - Optionally removes Twitter user handles (@username, @115854)
    - Normalizes URLs
    - Normalizes repeated punctuation and whitespace
    """
    if not isinstance(text, str):
        return ""

    # Remove unicode variation selectors (e.g. \ufe0f)
    text = text.replace("\ufe0f", "")
    text = text.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")

    if not keep_mentions:
        # Strip all @mentions (e.g., @AppleSupport, @115854)
        text = re.sub(r"@\w+", "", text)

    # Normalize t.co links to a generic token or strip if just sharing an image/attachment
    text = re.sub(r"https?://t\.co/\S+", "", text)
    text = re.sub(r"https?://\S+", "", text)

    # Remove excessive punctuation repetitions (e.g., !!!!!!!! -> !)
    text = re.sub(r"([!?.]){2,}", r"\1", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_corpus(path: str = DEFAULT_CORPUS_PATH) -> List[Dict]:
    """Loads the curated AppleSupport corpus of paired customer inquiries and agent replies."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Corpus file not found at {path}. Run 'python scripts/download_corpus.py' first."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_golden_set(path: str = DEFAULT_GOLDEN_PATH) -> List[Dict]:
    """Loads the 180-example golden evaluation benchmark."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Golden set file not found at {path}. Run 'python scripts/build_golden_set.py' first."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_training_corpus(corpus_path: str = DEFAULT_CORPUS_PATH) -> pd.DataFrame:
    """
    Returns a DataFrame containing cleaned customer texts and agent replies,
    ready for model training and retrieval indexing.
    """
    raw_data = load_corpus(corpus_path)
    records = []
    for item in raw_data:
        cust_clean = clean_tweet_text(item["customer_text"])
        agent_clean = clean_tweet_text(item["agent_text"], keep_mentions=False)
        if cust_clean and agent_clean:
            records.append({
                "pair_id": item["pair_id"],
                "customer_tweet_id": item["customer_tweet_id"],
                "agent_tweet_id": item["agent_tweet_id"],
                "customer_raw": item["customer_text"],
                "customer_clean": cust_clean,
                "agent_raw": item["agent_text"],
                "agent_clean": agent_clean,
                "is_initial": item.get("is_initial_query", True)
            })
    return pd.DataFrame(records)
