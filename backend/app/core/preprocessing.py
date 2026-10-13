"""
backend/app/core/preprocessing.py

Comprehensive text preprocessing pipeline for enterprise email IR:
- Unicode normalization (NFKD)
- HTML stripping & entity decoding
- Email header noise & boilerplate stripping
- Lowercasing
- Regex tokenization
- Stop-word removal
- Porter Stemming
- Whitespace normalization
"""

import re
import html
import unicodedata
from typing import List, Optional
import nltk
from nltk.stem import PorterStemmer

# Ensure nltk stopwords are downloaded or provide fallback
try:
    from nltk.corpus import stopwords
    STOPWORDS = set(stopwords.words("english"))
except Exception:
    # Comprehensive standard English stop-words fallback
    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
        "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
        "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
        "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
        "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
        "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
        "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
        "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that",
        "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
        "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
        "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
        "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who",
        "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
        "you're", "you've", "your", "yours", "yourself", "yourselves"
    }

# Also add frequent email boilerplate terms to stop-list
EMAIL_BOILERPLATE_WORDS = {
    "subject", "from", "to", "cc", "bcc", "sent", "date", "forwarded", "original", "message",
    "pm", "am", "font", "td", "tr", "table", "http", "https", "www", "com", "ect", "enron", "hou"
}

HTML_TAG_REGEX = re.compile(r"<[^>]+>", re.IGNORECASE)
EMAIL_FORWARD_DIVIDER = re.compile(r"-{4,}\s*(Original Message|Forwarded by).*?-{4,}", re.IGNORECASE | re.DOTALL)
EMAIL_HEADER_LINE = re.compile(r"^(From|To|Cc|Bcc|Sent|Date|Subject):\s*.*$", re.IGNORECASE | re.MULTILINE)
URL_REGEX = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
TOKEN_REGEX = re.compile(r"\b[a-zA-Z]{2,}\b")
WHITESPACE_REGEX = re.compile(r"\s+")

stemmer = PorterStemmer()


class Preprocessor:
    def __init__(self, use_stemming: bool = True, remove_stopwords: bool = True):
        self.use_stemming = use_stemming
        self.remove_stopwords = remove_stopwords
        self.stemmer = stemmer

    def clean_text(self, text: Optional[str]) -> str:
        """
        Clean text: normalize unicode, unescape html, strip tags, remove email headers and URLs.
        """
        if not text:
            return ""

        # Step 1: Unicode normalization (NFKD)
        text = unicodedata.normalize("NFKD", text)

        # Step 2: Unescape HTML entities & strip HTML tags
        text = html.unescape(text)
        text = HTML_TAG_REGEX.sub(" ", text)

        # Step 3: Remove URLs
        text = URL_REGEX.sub(" ", text)

        # Step 4: Remove forwarded message markers and inline header noise
        text = EMAIL_FORWARD_DIVIDER.sub(" ", text)
        text = EMAIL_HEADER_LINE.sub(" ", text)

        # Step 5: Whitespace normalization
        text = WHITESPACE_REGEX.sub(" ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """
        Lowercase and extract alpha tokens of length >= 2.
        """
        text = text.lower()
        return TOKEN_REGEX.findall(text)

    def filter_and_stem(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords and apply Porter Stemming.
        """
        results = []
        for t in tokens:
            if self.remove_stopwords:
                if t in STOPWORDS or t in EMAIL_BOILERPLATE_WORDS:
                    continue
            if self.use_stemming:
                t = self.stemmer.stem(t)
            results.append(t)
        return results

    def preprocess(self, text: Optional[str]) -> str:
        """
        End-to-end preprocessing pipeline returning normalized, stemmed tokens as a space-separated string.
        """
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        processed_tokens = self.filter_and_stem(tokens)
        return " ".join(processed_tokens)

    def preprocess_tokens(self, text: Optional[str]) -> List[str]:
        """
        End-to-end preprocessing pipeline returning a list of processed tokens.
        """
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        return self.filter_and_stem(tokens)


# Global singleton preprocessor instance
default_preprocessor = Preprocessor()
