"""
baselines/simple_baseline.py
Baseline 2: Simple Baseline.
- Intent: Multinomial Naive Bayes trained on word-level TF-IDF.
- Escalation: Heuristic keyword-matching rules (trigger on words like 'broken', 'charge', 'locked').
- Response: 1-Nearest Neighbor cosine similarity retrieval from uncurated training replies.
"""

import re
import time
from typing import Any, Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics.pairwise import cosine_similarity

from src.data_loader import clean_tweet_text, load_corpus, load_golden_set

class SimpleBaselineAgent:
    """
    Simple baseline demonstrating typical standard ML approach without
    calibrated uncertainty, reasoned policy engine, or prompt-guided brand synthesis.
    """

    def __init__(self):
        self.pipeline: Optional[Pipeline] = None
        self.retrieval_vectorizer: Optional[TfidfVectorizer] = None
        self.retrieval_matrix = None
        self.corpus_replies: List[str] = []

        # Simple keyword list for escalation heuristic
        self.escalation_keywords = [
            "broken", "screen", "cracked", "stolen", "locked", "charge",
            "charged", "bill", "billing", "refund", "money", "fraud",
            "swollen", "fire", "spark", "manager", "human", "supervisor"
        ]

    def fit(self):
        """Fits Naive Bayes classifier on available golden training queries and corpus."""
        golden = load_golden_set()
        train_texts = [clean_tweet_text(g["text"]) for g in golden]
        train_labels = [g["true_intent"] for g in golden]

        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 1), min_df=1, stop_words="english")),
            ("nb", MultinomialNB(alpha=1.0))
        ])
        self.pipeline.fit(train_texts, train_labels)

        # Fit simple 1-NN retriever on uncurated corpus
        corpus = load_corpus()
        corpus_texts = [clean_tweet_text(c["customer_text"]) for c in corpus[:1000]]
        self.corpus_replies = [c["agent_text"] for c in corpus[:1000]]

        self.retrieval_vectorizer = TfidfVectorizer(max_features=2000)
        self.retrieval_matrix = self.retrieval_vectorizer.fit_transform(corpus_texts)

    def process(self, customer_text: str, thread_context: Optional[List[str]] = None) -> Dict[str, Any]:
        t0 = time.time()
        if self.pipeline is None:
            self.fit()

        cleaned = clean_tweet_text(customer_text)

        # 1. Naive Bayes intent prediction
        predicted_intent = self.pipeline.predict([cleaned])[0]
        probs = self.pipeline.predict_proba([cleaned])[0]
        conf = float(max(probs))

        # 2. Simple keyword matching escalation
        lower = cleaned.lower()
        matched_kw = [kw for kw in self.escalation_keywords if re.search(r"\b" + kw + r"\b", lower)]
        should_escalate = len(matched_kw) > 0
        if should_escalate:
            escalation_reason = f"Keyword matching heuristic triggered on terms: {matched_kw}"
        else:
            escalation_reason = "No escalation keyword detected; auto-handling."

        # 3. 1-NN reply retrieval
        q_vec = self.retrieval_vectorizer.transform([cleaned])
        sims = cosine_similarity(q_vec, self.retrieval_matrix)[0]
        best_idx = int(sims.argmax())
        raw_reply = self.corpus_replies[best_idx]
        draft_reply = re.sub(r"^@\w+\s*", "", raw_reply).strip()

        latency_ms = (time.time() - t0) * 1000.0

        return {
            "customer_text": customer_text,
            "predicted_intent": str(predicted_intent),
            "intent_confidence": round(conf, 4),
            "should_escalate": should_escalate,
            "escalation_reason": escalation_reason,
            "escalation_trigger": "simple_keyword_heuristic" if should_escalate else "none",
            "draft_reply": draft_reply,
            "latency_ms": round(latency_ms, 2)
        }
