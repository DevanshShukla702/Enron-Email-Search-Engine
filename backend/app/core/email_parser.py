"""
backend/app/core/email_parser.py

Robust enterprise email parser using Python's standard email library.
Extracts metadata, cleans MIME headers, decodes text payloads, and handles malformed messages.
"""

import email
import email.policy
from email.header import decode_header, make_header
from email.utils import parseaddr, parsedate_to_datetime
import html
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("email_parser")

HTML_TAG_CLEANER = re.compile(r"<[^>]+>")


def safe_decode_header(header_value: Optional[str]) -> str:
    """Safely decode RFC-2047 MIME encoded headers."""
    if not header_value:
        return ""
    try:
        decoded_chunks = decode_header(header_value)
        return str(make_header(decoded_chunks)).strip()
    except Exception:
        return str(header_value).strip()


def extract_body_from_message(msg: email.message.EmailMessage) -> str:
    """Extract plain text or HTML body from message, handling multipart payloads."""
    body_parts = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Skip attachments
            if "attachment" in content_disposition.lower():
                continue

            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        body_parts.append(payload.decode(charset, errors="replace"))
                except Exception as e:
                    logger.debug(f"Failed decoding text/plain part: {e}")
            elif content_type == "text/html" and not body_parts:
                # Fallback to HTML if plain text not yet found
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        raw_html = payload.decode(charset, errors="replace")
                        text_only = HTML_TAG_CLEANER.sub(" ", raw_html)
                        body_parts.append(html.unescape(text_only))
                except Exception as e:
                    logger.debug(f"Failed decoding text/html part: {e}")
    else:
        content_type = msg.get_content_type()
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                decoded = payload.decode(charset, errors="replace")
                if content_type == "text/html":
                    decoded = html.unescape(HTML_TAG_CLEANER.sub(" ", decoded))
                body_parts.append(decoded)
            else:
                raw_payload = msg.get_payload()
                if isinstance(raw_payload, str):
                    body_parts.append(raw_payload)
        except Exception as e:
            logger.debug(f"Failed decoding payload: {e}")
            raw = msg.get_payload()
            if isinstance(raw, str):
                body_parts.append(raw)

    full_body = "\n".join(body_parts).strip()
    return full_body


def parse_email_file(file_path: Path, doc_id_prefix: str = "") -> Optional[Dict[str, Any]]:
    """
    Parse a single raw email file from the Enron corpus.
    Returns a normalized dictionary of email attributes or None on fatal failure.
    """
    try:
        with open(file_path, "rb") as f:
            raw_bytes = f.read()

        msg = email.message_from_bytes(raw_bytes, policy=email.policy.compat32)

        # Derive mailbox and folder from file path
        # Typical Enron path: maildir/<user>/<folder>/<filename>
        parts = file_path.parts
        mailbox = ""
        folder = ""
        if "maildir" in parts:
            idx = parts.index("maildir")
            if len(parts) > idx + 1:
                mailbox = parts[idx + 1]
            if len(parts) > idx + 2:
                folder = "/".join(parts[idx + 2:-1])

        # Extract headers
        message_id = safe_decode_header(msg.get("Message-ID", ""))
        sender_raw = safe_decode_header(msg.get("From", ""))
        sender_name, sender_email = parseaddr(sender_raw)
        if not sender_email and sender_raw:
            sender_email = sender_raw

        recipients = safe_decode_header(msg.get("To", ""))
        cc = safe_decode_header(msg.get("Cc", ""))
        bcc = safe_decode_header(msg.get("Bcc", ""))
        subject = safe_decode_header(msg.get("Subject", "")).strip()

        # Parse date to ISO format if possible
        date_raw = msg.get("Date", "")
        date_iso = None
        if date_raw:
            try:
                dt = parsedate_to_datetime(date_raw)
                date_iso = dt.isoformat()
            except Exception:
                date_iso = str(date_raw)

        # Extract body
        body = extract_body_from_message(msg)

        # Unique document ID: mailbox + relative path or message-id
        doc_id = f"{mailbox}_{folder}_{file_path.name}".replace("/", "_").replace("\\", "_")
        if not doc_id or doc_id == "__":
            doc_id = f"doc_{abs(hash(str(file_path)))}"

        return {
            "document_id": doc_id,
            "message_id": message_id,
            "sender": sender_email.strip().lower(),
            "sender_name": sender_name.strip() if sender_name else sender_email.split("@")[0],
            "recipients": recipients.strip(),
            "cc": cc.strip(),
            "bcc": bcc.strip(),
            "subject": subject,
            "date": date_iso,
            "mailbox": mailbox,
            "folder": folder,
            "body": body,
            "thread_id": None,
            "file_path": str(file_path),
            "in_reply_to": safe_decode_header(msg.get("In-Reply-To", "")),
            "references": safe_decode_header(msg.get("References", ""))
        }
    except Exception as e:
        logger.warning(f"Error parsing email file {file_path}: {e}")
        return None
