from datetime import datetime
from flask import request, session
from utils.db import get_connection


def log_action(actor_type: str, actor_id, action: str, entity_type: str = "", entity_id=None, details: str = ""):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    ua = request.headers.get("User-Agent", "")[:500]
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO audit_logs (actor_type, actor_id, action, entity_type, entity_id, details, ip_address, user_agent, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (actor_type, str(actor_id or ""), action, entity_type, str(entity_id or ""), details, ip, ua, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
