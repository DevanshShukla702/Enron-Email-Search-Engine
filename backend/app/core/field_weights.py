"""
backend/app/core/field_weights.py

Field weights configuration and text combination utility.
"""

from typing import Optional
from backend.app.config import settings


class FieldWeights:
    def __init__(
        self,
        subject_weight: float = settings.WEIGHT_SUBJECT,
        body_weight: float = settings.WEIGHT_BODY,
        sender_weight: float = settings.WEIGHT_SENDER,
        recipients_weight: float = settings.WEIGHT_RECIPIENTS
    ):
        self.subject = subject_weight
        self.body = body_weight
        self.sender = sender_weight
        self.recipients = recipients_weight

    def build_weighted_text(
        self,
        subject: Optional[str] = "",
        body: Optional[str] = "",
        sender: Optional[str] = "",
        recipients: Optional[str] = ""
    ) -> str:
        """
        Construct a combined weighted representation of an email document.
        Higher-weight fields (like Subject) are repeated or emphasized.
        """
        parts = []
        
        # Emphasize subject based on weight (e.g., weight 2.0 repeats subject twice)
        subj = (subject or "").strip()
        if subj:
            repeat_count = max(1, int(round(self.subject)))
            for _ in range(repeat_count):
                parts.append(subj)
                
        # Emphasize sender/recipients if weight >= 1.0
        sndr = (sender or "").strip()
        if sndr and self.sender >= 1.0:
            parts.append(sndr)
            
        recips = (recipients or "").strip()
        if recips and self.recipients >= 1.0:
            parts.append(recips)
            
        bdy = (body or "").strip()
        if bdy:
            parts.append(bdy)
            
        return " ".join(parts)


default_field_weights = FieldWeights()
