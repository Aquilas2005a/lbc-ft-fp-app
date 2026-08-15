from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def record_audit(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    details: Optional[str] = None,
    user_id: Optional[str] = "system",
) -> AuditLog:
    """Attach an audit event to the caller's database transaction."""
    event = AuditLog(
        user_id=user_id or "system",
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(event)
    return event
