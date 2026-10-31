from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.extensions import db
from app.models import ArticleView, Comment, Post

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.get("/")
@login_required
def index():
    posts = Post.query.filter_by(author_id=current_user.id).order_by(Post.updated_at.desc()).all()
    published_count = sum(post.is_published for post in posts)
    draft_count = len(posts) - published_count
    comment_count = Comment.query.join(Post).filter(Post.author_id == current_user.id).count()
    view_counts = dict(
        db.session.query(ArticleView.post_id, db.func.count(ArticleView.id))
        .join(Post, Post.id == ArticleView.post_id)
        .filter(Post.author_id == current_user.id)
        .group_by(ArticleView.post_id)
        .all()
    )
    total_views = sum(view_counts.values())
    recent_comments = (
        Comment.query.join(Post)
        .filter(Post.author_id == current_user.id)
        .order_by(Comment.created_at.desc())
        .limit(6)
        .all()
    )
    return render_template(
        "dashboard/index.html", posts=posts, published_count=published_count, draft_count=draft_count,
        comment_count=comment_count, recent_comments=recent_comments,
        view_counts=view_counts,
        total_views=total_views,
    )
