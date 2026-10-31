from datetime import datetime, timezone

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Notification

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.get("/")
@login_required
def index():
    notifications = (
        Notification.query.filter_by(recipient_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(100)
        .all()
    )
    return render_template("notifications/index.html", notifications=notifications)


@notifications_bp.post("/<int:notification_id>/read")
@login_required
def mark_read(notification_id: int):
    notification = db.session.get(Notification, notification_id)
    if notification is None:
        abort(404)
    if notification.recipient_id != current_user.id:
        abort(403)
    notification.read_at = notification.read_at or datetime.now(timezone.utc)
    db.session.commit()
    return redirect(url_for("notifications.index"))


@notifications_bp.post("/read-all")
@login_required
def mark_all_read():
    Notification.query.filter_by(recipient_id=current_user.id, read_at=None).update(
        {"read_at": datetime.now(timezone.utc)}, synchronize_session=False
    )
    db.session.commit()
    flash("All notifications are marked as read.", "success")
    return redirect(url_for("notifications.index"))
