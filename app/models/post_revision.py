from datetime import datetime, timezone

from app.extensions import db


class PostRevision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    excerpt = db.Column(db.String(320), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), nullable=False, index=True)
    editor_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    post = db.relationship("Post", back_populates="revisions")
    editor = db.relationship("User")
