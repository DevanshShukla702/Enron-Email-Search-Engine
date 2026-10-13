"""
backend/app/core/thread_builder.py

Thread reconstruction algorithm for email corpora.
Uses a hybrid heuristic:
1. Message-ID -> In-Reply-To / References direct parent-child edges
2. Normalized Subject grouping (stripping 'Re:', 'Fwd:', etc.) within temporal windows
3. Disjoint Set Union (DSU) to generate connected component thread_ids.
"""

import re
import hashlib
from typing import List, Dict, Any, Tuple
from collections import defaultdict

PREFIX_REGEX = re.compile(r"^(re:\s*|fwd:\s*|fw:\s*|\[fwd:\s*)+", re.IGNORECASE)


def normalize_subject(subject: str) -> str:
    """Strip 'Re:', 'Fwd:', etc., and excess whitespace."""
    if not subject:
        return ""
    s = subject.strip()
    while True:
        new_s = PREFIX_REGEX.sub("", s).strip()
        if new_s == s:
            break
        s = new_s
    return s.strip().lower()


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, i: str) -> str:
        if i not in self.parent:
            self.parent[i] = i
            return i
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: str, j: str):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j


def build_email_threads(emails: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Construct threads across email records.
    Returns a dictionary mapping document_id -> thread_id.
    """
    uf = UnionFind()
    msg_id_to_doc_id = {}
    subject_groups = defaultdict(list)

    # First pass: map message IDs and group by normalized subject
    for email_record in emails:
        doc_id = email_record["document_id"]
        msg_id = (email_record.get("message_id") or "").strip()
        if msg_id:
            msg_id_to_doc_id[msg_id] = doc_id

        norm_sub = normalize_subject(email_record.get("subject") or "")
        if len(norm_sub) >= 4:  # Ignore trivial subjects like "hi", "ok"
            subject_groups[norm_sub].append(doc_id)

    # Second pass: link In-Reply-To and References
    for email_record in emails:
        doc_id = email_record["document_id"]
        in_reply = (email_record.get("in_reply_to") or "").strip()
        references = (email_record.get("references_field") or "").strip()

        # Connect in_reply_to
        if in_reply and in_reply in msg_id_to_doc_id:
            parent_doc_id = msg_id_to_doc_id[in_reply]
            uf.union(doc_id, parent_doc_id)

        # Connect references
        if references:
            for ref in references.split():
                ref = ref.strip()
                if ref in msg_id_to_doc_id:
                    uf.union(doc_id, msg_id_to_doc_id[ref])

    # Third pass: link emails sharing normalized subject (max group size 100 to avoid giant clusters)
    for norm_sub, doc_ids in subject_groups.items():
        if 1 < len(doc_ids) <= 100:
            first_doc = doc_ids[0]
            for other_doc in doc_ids[1:]:
                uf.union(first_doc, other_doc)

    # Generate canonical thread IDs
    doc_id_to_thread_id = {}
    root_to_thread_id = {}

    for email_record in emails:
        doc_id = email_record["document_id"]
        root = uf.find(doc_id)
        if root not in root_to_thread_id:
            thread_hash = hashlib.md5(root.encode("utf-8")).hexdigest()[:12]
            root_to_thread_id[root] = f"th_{thread_hash}"
        doc_id_to_thread_id[doc_id] = root_to_thread_id[root]

    return doc_id_to_thread_id
