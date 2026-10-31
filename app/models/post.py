import re
from datetime import datetime, timezone

from app.extensions import db

post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(320), nullable=False, default="")
    featured_image = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="draft", index=True)
    scheduled_at = db.Column(db.DateTime(timezone=True), index=True)
    schedule_timezone = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id", ondelete="SET NULL"), index=True)
    author = db.relationship("User", back_populates="posts")
    category = db.relationship("Category", back_populates="posts")
    tags = db.relationship("Tag", secondary=post_tags, back_populates="posts")
    comments = db.relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan", order_by="Comment.created_at"
    )
    revisions = db.relationship("PostRevision", back_populates="post", cascade="all, delete-orphan", order_by="PostRevision.created_at.desc()")
    likes = db.relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    bookmarks = db.relationship("Bookmark", back_populates="post", cascade="all, delete-orphan")
    views = db.relationship("ArticleView", back_populates="post", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="post")

    @property
    def is_published(self) -> bool:
        return self.status == "published"

    @property
    def reading_time_minutes(self) -> int:
        plain_text = re.sub(r"<[^>]+>", " ", self.content)
        words = re.findall(r"\b\w+\b", plain_text)
        return max(1, round(len(words) / 200))

    def __repr__(self) -> str:
        return f"<Post {self.slug}>"
