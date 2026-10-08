def record_audit(user_id=None, action=None, entity_name=None, record_id=None, old_value=None, new_value=None, ip_address=None):
    from extensions import db
    from models.user import AuditLog

    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_name=entity_name,
        record_id=record_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
    )
    db.session.add(log)
    db.session.commit()
