"""
src/knowledge_retriever.py
Historical resolution retrieval engine for @AppleSupport inquiries.
Uses TF-IDF Vector Space search and BM25-style lexical scoring
to surface relevant historical resolutions, official links, and diagnostic patterns.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.data_loader import clean_tweet_text, load_corpus

INDEX_DIR = "models"
INDEX_PATH = os.path.join(INDEX_DIR, "retriever_index.joblib")

class KnowledgeRetriever:
    """
    Retrieves historical @AppleSupport resolutions and troubleshooting actions
    grounded directly in how Apple Support historically solved similar customer queries.
    """

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.doc_vectors: Optional[np.ndarray] = None
        self.corpus_records: List[Dict] = []

    def build_index(self, corpus_records: List[Dict]):
        """
        Builds the TF-IDF vector index over historical customer queries and resolutions.
        """
        self.corpus_records = corpus_records
        # Index on customer query text combined with agent resolution
        indexed_texts = []
        for r in corpus_records:
            cust = clean_tweet_text(r["customer_text"])
            agent = clean_tweet_text(r["agent_text"])
            indexed_texts.append(f"{cust} {agent}")

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.90,
            sublinear_tf=True,
            strip_accents="unicode"
        )
        self.doc_vectors = self.vectorizer.fit_transform(indexed_texts)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieves the top_k most similar historical resolutions for a customer query.
        """
        if self.vectorizer is None or self.doc_vectors is None:
            raise ValueError("Retriever index is not built. Call build_index() or load() first.")

        cleaned_query = clean_tweet_text(query)
        if not cleaned_query:
            return []

        q_vec = self.vectorizer.transform([cleaned_query])
        scores = cosine_similarity(q_vec, self.doc_vectors)[0]
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            rec = self.corpus_records[idx]
            
            # Extract official links if present
            links = re.findall(r"https?://\S+|apple\.co/\S+", rec["agent_text"])
            
            results.append({
                "similarity_score": round(score, 4),
                "historical_customer_query": rec["customer_text"],
                "historical_agent_reply": rec["agent_text"],
                "pair_id": rec.get("pair_id", ""),
                "links": links
            })
        return results

    def save(self, filepath: str = INDEX_PATH):
        """Saves retriever index to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "vectorizer": self.vectorizer,
            "doc_vectors": self.doc_vectors,
            "corpus_records": self.corpus_records
        }, filepath)

    def load(self, filepath: str = INDEX_PATH):
        """Loads retriever index from disk."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Retriever index not found at {filepath}")
        data = joblib.load(filepath)
        self.vectorizer = data["vectorizer"]
        self.doc_vectors = data["doc_vectors"]
        self.corpus_records = data["corpus_records"]


def get_default_retriever(save: bool = True) -> KnowledgeRetriever:
    """Initializes and builds the default retriever from the AppleSupport corpus."""
    if os.path.exists(INDEX_PATH):
        retriever = KnowledgeRetriever()
        retriever.load(INDEX_PATH)
        return retriever

    corpus = load_corpus()
    retriever = KnowledgeRetriever()
    retriever.build_index(corpus)
    if save:
        retriever.save()
    return retriever
