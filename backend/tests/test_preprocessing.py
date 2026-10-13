"""
Unit tests for text preprocessing and field-weighting pipelines.
"""

import pytest
from backend.app.core.preprocessing import Preprocessor, default_preprocessor
from backend.app.core.field_weights import FieldWeights


def test_unicode_normalization_and_html_cleaning():
    p = Preprocessor()
    raw = "<p>Hello&nbsp;World! <b>Enron</b> &amp; Energy</p>"
    cleaned = p.clean_text(raw)
    assert "Hello World!" in cleaned
    assert "Enron & Energy" in cleaned
    assert "<p>" not in cleaned
    assert "<b>" not in cleaned


def test_tokenization_and_lowercasing():
    p = Preprocessor()
    tokens = p.tokenize("Trading in California 2001 power markets!")
    assert "trading" in tokens
    assert "california" in tokens
    assert "power" in tokens
    assert "markets" in tokens
    # Numbers and punctuation should be excluded
    assert "2001" not in tokens


def test_stopword_removal_and_stemming():
    p = Preprocessor(use_stemming=True, remove_stopwords=True)
    # "regulatory" stems to "regulatori", "filings" stems to "file"
    tokens = p.preprocess_tokens("the regulatory filings about energy")
    assert "the" not in tokens
    assert "about" not in tokens
    assert len(tokens) >= 2


def test_header_and_forward_cleaning():
    p = Preprocessor()
    email_text = """
    From: john.doe@enron.com
    To: jane.doe@enron.com
    Subject: Urgent Review
    
    Here is the proposal.
    -----Original Message-----
    From: old.sender@enron.com
    Older message body.
    """
    cleaned = p.clean_text(email_text)
    assert "Here is the proposal." in cleaned


def test_field_weights_construction():
    fw = FieldWeights(subject_weight=2.0, body_weight=1.0)
    combined = fw.build_weighted_text(
        subject="FERC Investigation",
        body="California wholesale electricity price limits."
    )
    # Subject should be repeated twice for weight 2.0
    assert combined.count("FERC Investigation") == 2
    assert "California wholesale electricity price limits." in combined
