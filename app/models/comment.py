from datetime import datetime, timezone

from app.extensions import db


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("comment.id", ondelete="CASCADE"), index=True)
    author = db.relationship("User", back_populates="comments")
    post = db.relationship("Post", back_populates="comments")
    parent = db.relationship("Comment", remote_side="Comment.id", back_populates="replies")
    replies = db.relationship("Comment", back_populates="parent", cascade="all, delete-orphan", order_by="Comment.created_at")
    reports = db.relationship("CommentReport", back_populates="comment", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="comment")

    def __repr__(self) -> str:
        return f"<Comment {self.id}>"
