"""
scripts/download_corpus.py
Streams a slice of the TWCS dataset directly from Hugging Face using HTTP Range requests,
extracts real @AppleSupport customer conversations, links replies to inbound tweets,
and saves the curated corpus for training and retrieval.
"""

import io
import json
import os
import sys
import pandas as pd
import requests

DATASET_URL = "https://huggingface.co/datasets/SunidhiSriram/twcs/resolve/main/twcs.csv"
OUTPUT_JSON = os.path.join("data", "apple_support_corpus.json")
OUTPUT_CSV = os.path.join("data", "raw_sample.csv")

def get_final_url(url: str) -> str:
    """Resolve potential redirects to ensure Range headers are respected by CloudFront/S3."""
    resp = requests.head(url, allow_redirects=True, timeout=30)
    return resp.url

def download_and_extract_apple_support(byte_range: int = 25_000_000):
    """
    Downloads byte_range bytes from TWCS and filters for AppleSupport interactions.
    25MB provides ~4,000+ AppleSupport replies and 3,900+ matched customer-support pairs.
    """
    os.makedirs("data", exist_ok=True)
    
    if os.path.exists(OUTPUT_JSON) and os.path.exists(OUTPUT_CSV):
        print(f"[Info] Corpus already exists at {OUTPUT_JSON}. Skipping download.")
        return

    print(f"[1/4] Resolving dataset download endpoint...")
    final_url = get_final_url(DATASET_URL)
    
    print(f"[2/4] Fetching first {byte_range // (1024*1024)}MB of TWCS via HTTP Range...")
    headers = {"Range": f"bytes=0-{byte_range}"}
    resp = requests.get(final_url, headers=headers, timeout=120)
    resp.raise_for_status()

    # Truncate to the last complete newline to avoid partial CSV record errors
    content = resp.content[:resp.content.rfind(b"\n")]
    print(f"[3/4] Parsing CSV chunk ({len(content):,} bytes)...")
    
    df = pd.read_csv(
        io.BytesIO(content),
        on_bad_lines="skip",
        dtype={
            "tweet_id": "Int64",
            "author_id": "string",
            "inbound": "boolean",
            "created_at": "string",
            "text": "string",
            "response_tweet_id": "string",
            "in_response_to_tweet_id": "Int64"
        }
    )
    print(f"      Total rows parsed in chunk: {len(df):,}")

    # Extract AppleSupport agent responses
    apple_replies = df[df["author_id"] == "AppleSupport"].copy()
    print(f"      Found {len(apple_replies):,} @AppleSupport agent replies.")

    # Match each agent reply with its triggering customer tweet
    merged = pd.merge(
        apple_replies,
        df,
        left_on="in_response_to_tweet_id",
        right_on="tweet_id",
        suffixes=("_agent", "_cust")
    )
    print(f"      Successfully linked {len(merged):,} customer -> @AppleSupport pairs.")

    # Clean and structure records
    records = []
    for _, row in merged.iterrows():
        cust_text = str(row["text_cust"]).strip() if pd.notna(row["text_cust"]) else ""
        agent_text = str(row["text_agent"]).strip() if pd.notna(row["text_agent"]) else ""
        
        if not cust_text or not agent_text:
            continue
        if len(cust_text) < 5 or len(agent_text) < 5:
            continue

        records.append({
            "pair_id": f"tw_{int(row['tweet_id_cust'])}_{int(row['tweet_id_agent'])}",
            "customer_tweet_id": int(row["tweet_id_cust"]),
            "agent_tweet_id": int(row["tweet_id_agent"]),
            "customer_text": cust_text,
            "agent_text": agent_text,
            "is_initial_query": pd.isna(row["in_response_to_tweet_id_cust"]),
            "created_at_cust": str(row["created_at_cust"]),
            "created_at_agent": str(row["created_at_agent"])
        })

    print(f"[4/4] Saving {len(records):,} curated pairs to disk...")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    df_out = pd.DataFrame(records)
    df_out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"      [Done] Saved {OUTPUT_JSON} and {OUTPUT_CSV} successfully.")

if __name__ == "__main__":
    download_and_extract_apple_support()
