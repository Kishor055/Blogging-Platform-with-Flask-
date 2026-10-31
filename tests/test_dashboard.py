from app.extensions import db
from app.models import Comment, Post, User
from tests.test_blog import _create_post


def test_dashboard_shows_post_metrics_and_recent_comments(author, app):
    _create_post(author)
    with app.app_context():
        post = Post.query.one()
        reader = User(username="reader", email="reader@example.com")
        reader.set_password("LongEnoughPassword!23")
        db.session.add(reader)
        db.session.flush()
        db.session.add(Comment(content="A recent reader response.", author=reader, post=post))
        db.session.commit()

    response = author.get("/dashboard/")
    assert response.status_code == 200
    assert b"Published stories" in response.data
    assert b"Comments received" in response.data
    assert b"Recent conversations" in response.data
    assert b"A recent reader response." in response.data
    assert b"A thoughtful article" in response.data
