from datetime import datetime, timezone

from app.extensions import db


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(30), nullable=False)
    message = db.Column(db.String(240), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    read_at = db.Column(db.DateTime(timezone=True))
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id", ondelete="SET NULL"))
    comment_id = db.Column(db.Integer, db.ForeignKey("comment.id", ondelete="SET NULL"))
    recipient = db.relationship("User", back_populates="notifications", foreign_keys=[recipient_id])
    actor = db.relationship("User", back_populates="acted_notifications", foreign_keys=[actor_id])
    post = db.relationship("Post", back_populates="notifications")
    comment = db.relationship("Comment", back_populates="notifications")

    @property
    def is_read(self) -> bool:
        return self.read_at is not None
