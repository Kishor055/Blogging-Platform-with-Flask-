from datetime import datetime, timezone

from app.blog.scheduling import publish_due_posts
from app.extensions import db
from app.models import ArticleView, Bookmark, Comment, CommentReport, Notification, Post, PostLike, PostRevision, User
from tests.test_blog import _create_post


def test_post_revisions_can_be_restored(author, app):
    _create_post(author)
    with app.app_context():
        post = Post.query.one()
        original_slug = post.slug

    author.post(
        f"/article/{original_slug}/edit",
        data={
            "title": "A revised thoughtful article",
            "excerpt": "A newer summary.",
            "content": "<p>This revised article has more than twenty characters.</p>",
            "category_id": "0",
            "tag_ids": [],
            "status": "published",
        },
        follow_redirects=True,
    )
    with app.app_context():
        post = Post.query.one()
        revision = PostRevision.query.one()
        assert revision.title == "A thoughtful article"
        assert revision.content == "<p>This is a sufficiently long article body.</p>"
        revision_id = revision.id
        revised_slug = post.slug

    response = author.post(
        f"/article/{revised_slug}/revisions/{revision_id}/restore",
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        post = Post.query.one()
        assert post.title == "A thoughtful article"
        assert post.content == "<p>This is a sufficiently long article body.</p>"
        assert PostRevision.query.count() == 2
        assert PostRevision.query.order_by(PostRevision.id.desc()).first().title == "A revised thoughtful article"


def test_scheduled_posts_publish_idempotently_and_notify_author(author, app):
    author.post(
        "/article/new",
        data={
            "title": "A scheduled thoughtful article",
            "excerpt": "Coming later.",
            "content": "<p>This article will be published at its scheduled time.</p>",
            "category_id": "0",
            "tag_ids": [],
            "status": "scheduled",
            "scheduled_local": "2027-01-01T09:00",
            "schedule_timezone": "Europe/Paris",
        },
        follow_redirects=True,
    )
    with app.app_context():
        post = Post.query.one()
        assert post.status == "scheduled"
        scheduled_at = post.scheduled_at
        if scheduled_at.tzinfo is None:
            scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
        assert scheduled_at == datetime(2027, 1, 1, 8, tzinfo=timezone.utc)
        slug = post.slug

    assert app.test_client().get(f"/article/{slug}").status_code == 404
    with app.app_context():
        assert publish_due_posts(datetime(2027, 1, 1, 9, tzinfo=timezone.utc)) == 1
        assert publish_due_posts(datetime(2027, 1, 1, 9, tzinfo=timezone.utc)) == 0
        assert Post.query.one().status == "published"
        assert Notification.query.filter_by(kind="published").count() == 1


def test_invalid_schedule_timezone_is_rejected(author, app):
    response = author.post(
        "/article/new",
        data={
            "title": "A scheduled thoughtful article",
            "excerpt": "Coming later.",
            "content": "<p>This article will be published at its scheduled time.</p>",
            "category_id": "0",
            "tag_ids": [],
            "status": "scheduled",
            "scheduled_local": "2027-01-01T09:00",
            "schedule_timezone": "Not/A_Timezone",
        },
        follow_redirects=True,
    )
    assert b"Enter a valid timezone" in response.data
    with app.app_context():
        assert Post.query.count() == 0


def test_likes_bookmarks_and_daily_unique_analytics(author, app):
    _create_post(author)
    with app.app_context():
        slug = Post.query.one().slug

    author.get(f"/article/{slug}")
    author.get(f"/article/{slug}")
    app.test_client().get(f"/article/{slug}")
    with app.app_context():
        assert ArticleView.query.count() == 2

    author.post(f"/article/{slug}/like")
    author.post(f"/article/{slug}/bookmark")
    with app.app_context():
        assert PostLike.query.count() == 1
        assert Bookmark.query.count() == 1
    assert b"A thoughtful article" in author.get("/bookmarks").data

    author.post(f"/article/{slug}/like")
    author.post(f"/article/{slug}/bookmark")
    with app.app_context():
        assert PostLike.query.count() == 0
        assert Bookmark.query.count() == 0


def test_comment_replies_reports_and_notifications(author, app):
    _create_post(author)
    with app.app_context():
        post = Post.query.one()
        slug = post.slug

    reader = app.test_client()
    reader.post(
        "/auth/register",
        data={
            "username": "reader_one",
            "email": "reader@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
    )
    reader.post(
        f"/article/{slug}",
        data={"content": "A reader has shared a thoughtful comment."},
    )
    with app.app_context():
        comment = Comment.query.one()
        comment_id = comment.id
        author_id = Post.query.one().author_id
        assert Notification.query.filter_by(recipient_id=author_id, kind="comment").count() == 1

    author.post(
        f"/comments/{comment_id}/reply",
        data={"content": "Here is a helpful reply from the author."},
    )
    author.post(
        f"/comments/{comment_id}/report",
        data={"reason": "This comment appears to be spam."},
    )
    with app.app_context():
        assert Comment.query.count() == 2
        assert CommentReport.query.one().status == "pending"
        assert Notification.query.filter_by(kind="reply").count() == 1
        author_user = User.query.filter_by(username="writer_one").one()
        author_user.role = "admin"
        db.session.commit()
    response = author.get("/admin/")
    assert response.status_code == 200
    assert b"Comment reports" in response.data


def test_revision_history_is_owner_only(author, app):
    _create_post(author)
    with app.app_context():
        slug = Post.query.one().slug

    reader = app.test_client()
    reader.post(
        "/auth/register",
        data={
            "username": "reader_two",
            "email": "reader2@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
    )
    assert reader.get(f"/article/{slug}/revisions").status_code == 403


def test_seo_endpoints_only_include_published_posts(author, app):
    _create_post(author)
    _create_post(author, title="A private draft", status="draft")
    sitemap = author.get("/sitemap.xml")
    feed = author.get("/feed.xml")
    robots = author.get("/robots.txt")
    assert sitemap.status_code == 200
    assert b"a-thoughtful-article" in sitemap.data
    assert b"a-private-draft" not in sitemap.data
    assert b"A thoughtful article" in feed.data
    assert b"A private draft" not in feed.data
    assert b"Sitemap:" in robots.data
