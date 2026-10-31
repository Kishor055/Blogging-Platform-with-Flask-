from datetime import datetime, timezone

from app.extensions import db


class CommentReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comment.id", ondelete="CASCADE"), nullable=False, index=True)
    reporter = db.relationship("User", back_populates="reported_comments")
    comment = db.relationship("Comment", back_populates="reports")
    __table_args__ = (db.UniqueConstraint("reporter_id", "comment_id", name="uq_comment_reporter_comment"),)
