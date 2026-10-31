from app.extensions import db
from app.models import Notification


def create_notification(recipient_id, kind, message, *, actor_id=None, post_id=None, comment_id=None):
    if recipient_id == actor_id:
        return
    db.session.add(
        Notification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            post_id=post_id,
            comment_id=comment_id,
            kind=kind,
            message=message,
        )
    )
