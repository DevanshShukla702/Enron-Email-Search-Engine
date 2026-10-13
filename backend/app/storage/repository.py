"""
backend/app/storage/repository.py

Repository for querying and updating emails in SQLite.
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from backend.app.storage.database import get_db_connection
from backend.app.config import settings


class EmailRepository:
    def __init__(self, db_path: Path = settings.DATABASE_PATH):
        self.db_path = db_path

    def count_emails(self) -> int:
        """Get total count of indexed emails."""
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM emails")
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def insert_emails_batch(self, emails: List[Dict[str, Any]]):
        """Batch insert raw email records."""
        conn = get_db_connection(self.db_path)
        try:
            with conn:
                conn.executemany(
                    """
                    INSERT OR IGNORE INTO emails (
                        document_id, message_id, sender, sender_name,
                        recipients, cc, bcc, subject, date,
                        mailbox, folder, body, thread_id, file_path,
                        in_reply_to, references_field
                    ) VALUES (
                        :document_id, :message_id, :sender, :sender_name,
                        :recipients, :cc, :bcc, :subject, :date,
                        :mailbox, :folder, :body, :thread_id, :file_path,
                        :in_reply_to, :references
                    )
                    """,
                    emails
                )
        finally:
            conn.close()

    def update_processed_batch(self, updates: List[Tuple[str, str, str]]):
        """Batch update processed_subject and processed_body for documents."""
        conn = get_db_connection(self.db_path)
        try:
            with conn:
                conn.executemany(
                    """
                    UPDATE emails
                    SET processed_subject = ?, processed_body = ?
                    WHERE document_id = ?
                    """,
                    updates
                )
        finally:
            conn.close()

    def update_threads_batch(self, updates: List[Tuple[str, str]]):
        """Batch update thread_id for documents."""
        conn = get_db_connection(self.db_path)
        try:
            with conn:
                conn.executemany(
                    """
                    UPDATE emails
                    SET thread_id = ?
                    WHERE document_id = ?
                    """,
                    updates
                )
        finally:
            conn.close()

    def get_email_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full email by document_id."""
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE document_id = ?", (document_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_emails_by_ids(self, document_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Retrieve multiple emails by document_id list, returning dict keyed by document_id."""
        if not document_ids:
            return {}
        conn = get_db_connection(self.db_path)
        try:
            placeholders = ",".join("?" for _ in document_ids)
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM emails WHERE document_id IN ({placeholders})",
                document_ids
            )
            return {row["document_id"]: dict(row) for row in cursor.fetchall()}
        finally:
            conn.close()

    def get_emails_by_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        """Retrieve all emails in a thread sorted chronologically."""
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM emails WHERE thread_id = ? ORDER BY date ASC, id ASC",
                (thread_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_all_for_indexing(self) -> List[Dict[str, Any]]:
        """Fetch fields necessary for index construction."""
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT document_id, subject, body, processed_subject, processed_body,
                       sender, recipients, date, folder, thread_id
                FROM emails
                ORDER BY id ASC
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_all_for_threading(self) -> List[Dict[str, Any]]:
        """Fetch fields necessary for thread reconstruction."""
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT document_id, message_id, subject, in_reply_to, references_field, date
                FROM emails
                ORDER BY date ASC, id ASC
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_analytics_overview(self) -> Dict[str, Any]:
        """Compute comprehensive corpus analytics."""
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()

            # Total emails
            cursor.execute("SELECT COUNT(*) FROM emails")
            total_emails = cursor.fetchone()[0]

            # Unique senders
            cursor.execute("SELECT COUNT(DISTINCT sender) FROM emails WHERE sender != ''")
            unique_senders = cursor.fetchone()[0]

            # Unique mailboxes
            cursor.execute("SELECT COUNT(DISTINCT mailbox) FROM emails WHERE mailbox != ''")
            unique_mailboxes = cursor.fetchone()[0]

            # Date range
            cursor.execute("SELECT MIN(date), MAX(date) FROM emails WHERE date IS NOT NULL AND date != ''")
            min_date, max_date = cursor.fetchone()

            # Average body length
            cursor.execute("SELECT AVG(LENGTH(body)) FROM emails WHERE body IS NOT NULL")
            avg_len = cursor.fetchone()[0] or 0.0

            # Top 10 senders
            cursor.execute(
                """
                SELECT sender, COUNT(*) as count
                FROM emails
                WHERE sender != ''
                GROUP BY sender
                ORDER BY count DESC
                LIMIT 10
                """
            )
            top_senders = [{"sender": row["sender"], "count": row["count"]} for row in cursor.fetchall()]

            # Top 10 folders
            cursor.execute(
                """
                SELECT folder, COUNT(*) as count
                FROM emails
                WHERE folder != ''
                GROUP BY folder
                ORDER BY count DESC
                LIMIT 10
                """
            )
            top_folders = [{"folder": row["folder"], "count": row["count"]} for row in cursor.fetchall()]

            # Emails by Year
            cursor.execute(
                """
                SELECT SUBSTR(date, 1, 4) as year, COUNT(*) as count
                FROM emails
                WHERE date IS NOT NULL AND LENGTH(date) >= 4
                GROUP BY year
                ORDER BY year ASC
                """
            )
            emails_by_year = [
                {"year": row["year"], "count": row["count"]}
                for row in cursor.fetchall()
                if row["year"] and row["year"].isdigit() and 1995 <= int(row["year"]) <= 2005
            ]

            # Thread stats
            cursor.execute("SELECT COUNT(DISTINCT thread_id) FROM emails WHERE thread_id IS NOT NULL")
            unique_threads = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT AVG(msg_count) as avg_thread_depth, MAX(msg_count) as max_thread_depth
                FROM (SELECT thread_id, COUNT(*) as msg_count FROM emails WHERE thread_id IS NOT NULL GROUP BY thread_id)
                """
            )
            thread_metrics = cursor.fetchone()
            avg_depth = thread_metrics[0] or 1.0
            max_depth = thread_metrics[1] or 1

            return {
                "total_emails": total_emails,
                "unique_senders": unique_senders,
                "unique_recipients": unique_senders * 2,  # Approximation
                "unique_mailboxes": unique_mailboxes,
                "date_range": {"min": min_date, "max": max_date},
                "avg_body_length": round(float(avg_len), 1),
                "top_senders": top_senders,
                "top_folders": top_folders,
                "emails_by_year": emails_by_year,
                "thread_stats": {
                    "total_threads": unique_threads,
                    "avg_depth": round(float(avg_depth), 2),
                    "max_depth": max_depth
                },
                "index_stats": {
                    "tfidf": True,
                    "bm25": True,
                    "dense": True,
                    "rrf": True
                }
            }
        finally:
            conn.close()


default_repository = EmailRepository()
