from datetime import datetime, timezone

from app.extensions import db


class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), nullable=False, index=True)
    user = db.relationship("User", back_populates="post_likes")
    post = db.relationship("Post", back_populates="likes")
    __table_args__ = (db.UniqueConstraint("user_id", "post_id", name="uq_post_like_user_post"),)
