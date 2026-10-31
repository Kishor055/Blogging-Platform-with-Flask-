from datetime import datetime, timezone

from sqlalchemy import update

from app.extensions import db
from app.models import Post
from app.utils.notifications import create_notification


def publish_due_posts(now=None):
    current_time = now or datetime.now(timezone.utc)
    due_post_ids = [
        post_id
        for (post_id,) in db.session.query(Post.id)
        .filter(Post.status == "scheduled", Post.scheduled_at <= current_time)
        .order_by(Post.scheduled_at, Post.id)
        .all()
    ]
    published_count = 0
    for post_id in due_post_ids:
        post = db.session.get(Post, post_id)
        if post is None:
            continue
        result = db.session.execute(
            update(Post)
            .where(
                Post.id == post_id,
                Post.status == "scheduled",
                Post.scheduled_at <= current_time,
            )
            .values(status="published", scheduled_at=None)
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            continue
        published_count += 1
        create_notification(
            post.author_id,
            "published",
            f'Your scheduled article "{post.title}" is now published.',
            post_id=post.id,
        )
    db.session.commit()
    return published_count
