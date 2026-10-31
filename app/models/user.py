from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.String(500), nullable=False, default="")
    role = db.Column(db.String(20), nullable=False, default="author")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    posts = db.relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    post_likes = db.relationship("PostLike", back_populates="user", cascade="all, delete-orphan")
    bookmarks = db.relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    notifications = db.relationship(
        "Notification", back_populates="recipient", cascade="all, delete-orphan",
        foreign_keys="Notification.recipient_id",
    )
    acted_notifications = db.relationship(
        "Notification", back_populates="actor", foreign_keys="Notification.actor_id"
    )
    reported_comments = db.relationship("CommentReport", back_populates="reporter", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self) -> str:
        return f"<User {self.username}>"
