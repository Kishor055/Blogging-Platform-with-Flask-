from app.extensions import db, login_manager
from app.models.category import Category
from app.models.comment import Comment
from app.models.comment_report import CommentReport
from app.models.article_view import ArticleView
from app.models.bookmark import Bookmark
from app.models.notification import Notification
from app.models.post import Post, post_tags
from app.models.post_like import PostLike
from app.models.post_revision import PostRevision
from app.models.tag import Tag
from app.models.user import User


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


__all__ = [
    "ArticleView", "Bookmark", "Category", "Comment", "CommentReport", "Notification",
    "Post", "PostLike", "PostRevision", "Tag", "User", "post_tags",
]
