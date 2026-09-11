"""
tests/test_knowledge_retriever.py
Unit tests for TF-IDF historical resolution retrieval engine.
"""

import pytest
from src.knowledge_retriever import KnowledgeRetriever, get_default_retriever

@pytest.fixture(scope="module")
def retriever():
    return get_default_retriever(save=False)

def test_retriever_initialization(retriever):
    assert retriever.vectorizer is not None
    assert retriever.doc_vectors is not None
    assert len(retriever.corpus_records) > 0

def test_retrieve_returns_top_k(retriever):
    query = "My battery dies very quickly after iOS 11 update"
    results = retriever.retrieve(query, top_k=3)
    assert len(results) == 3
    for r in results:
        assert "similarity_score" in r
        assert "historical_customer_query" in r
        assert "historical_agent_reply" in r
        assert "links" in r
        assert r["similarity_score"] >= 0.0

def test_retrieve_extracts_links(retriever):
    # Retrieve across corpus to verify link extraction works when links exist
    results = retriever.retrieve("direct message DM support link", top_k=5)
    has_any_link = any(len(r["links"]) > 0 for r in results)
    assert has_any_link

def test_retrieve_empty_query_returns_empty(retriever):
    results = retriever.retrieve("")
    assert results == []
