import sqlite3
from datetime import datetime
from app.models import get_connection


def insert_message(msg) -> str:
    """
    Insert a webhook message into DB.

    Idempotency:
    - message_id is PRIMARY KEY
    - duplicate inserts are ignored gracefully

    Returns:
        "created"   -> new row inserted
        "duplicate" -> message already exists
    """
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO messages (
                message_id,
                from_msisdn,
                to_msisdn,
                ts,
                text,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                msg.message_id,
                msg.from_msisdn,
                msg.to_msisdn,
                msg.ts.isoformat(),
                msg.text,
                datetime.utcnow().isoformat()
            )
        )

        conn.commit()
        return "created"

    except sqlite3.IntegrityError:
        # message_id already exists → idempotent behavior
        return "duplicate"

    finally:
        conn.close()

def fetch_messages(
    limit: int,
    offset: int,
    from_msisdn: str | None,
    to_msisdn: str | None,
    start_ts: str | None,
    end_ts: str | None
):
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        query = "SELECT * FROM messages WHERE 1=1"
        params = []

        if from_msisdn:
            query += " AND from_msisdn = ?"
            params.append(from_msisdn)

        if to_msisdn:
            query += " AND to_msisdn = ?"
            params.append(to_msisdn)

        if start_ts:
            query += " AND ts >= ?"
            params.append(start_ts)

        if end_ts:
            query += " AND ts <= ?"
            params.append(end_ts)
            
    
        cursor.execute(f"SELECT COUNT(*) {query}", params)
        total = cursor.fetchone()[0]

        data_query = (
            f"{query} "
            "ORDER BY ts DESC LIMIT ? OFFSET ?"
        )
        

        query += " ORDER BY ts DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows],total

    finally:
        conn.close()


def fetch_stats():
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Total messages
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]

        # First and last timestamps
        cursor.execute("SELECT MIN(ts), MAX(ts) FROM messages")
        first_ts, last_ts = cursor.fetchone()

        # Messages per sender (top 10)
        cursor.execute(
            """
            SELECT from_msisdn, COUNT(*) as count
            FROM messages
            GROUP BY from_msisdn
            ORDER BY count DESC
            LIMIT 10
            """
        )
        rows = cursor.fetchall()

        messages_per_sender = [
            {"from": row[0], "count": row[1]} for row in rows
        ]

        return {
            "total_messages": total_messages,
            "senders_count": len(messages_per_sender),
            "messages_per_sender": messages_per_sender,
            "first_message_ts": first_ts,
            "last_message_ts": last_ts
        }

    finally:
        conn.close()
