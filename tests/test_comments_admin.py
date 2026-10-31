from app.extensions import db
from app.models import Category, Comment, Post, Tag, User
from tests.test_blog import _create_post


def test_authenticated_comment_and_owner_deletion(author, app):
    _create_post(author)
    with app.app_context():
        post = Post.query.one()
        slug = post.slug
    response = author.post(
        f"/article/{slug}",
        data={"content": "A thoughtful response from a reader."},
        follow_redirects=True,
    )
    assert b"A thoughtful response from a reader." in response.data
    with app.app_context():
        comment_id = Comment.query.one().id
    response = author.post(f"/comments/{comment_id}/delete", follow_redirects=True)
    assert b"comment has been removed" in response.data


def test_comment_authorization(client, author, app):
    _create_post(author)
    with app.app_context():
        post = Post.query.one()
        slug = post.slug
    author.post(f"/article/{slug}", data={"content": "A comment that belongs to another reader."})
    with app.app_context():
        comment_id = Comment.query.one().id
    author.post("/auth/logout")
    client.post(
        "/auth/register",
        data={
            "username": "other_reader",
            "email": "other@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
    )
    assert client.post(f"/comments/{comment_id}/delete").status_code == 403


def test_admin_can_moderate_and_manage_categories(client, app):
    client.post(
        "/auth/register",
        data={
            "username": "site_admin",
            "email": "admin@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
    )
    with app.app_context():
        user = User.query.filter_by(username="site_admin").one()
        user.role = "admin"
        db.session.commit()
    assert client.get("/admin/").status_code == 200
    response = client.post("/admin/taxonomy/category", data={"name": "Technology"})
    assert response.status_code == 302
    response = client.get(response.headers["Location"], follow_redirects=True)
    assert b"Category created" in response.data
    assert client.get("/admin/").status_code == 200
    assert client.get("/admin/").data.count(b"Technology") >= 1


def test_non_admin_cannot_access_administration(author):
    assert author.get("/admin/").status_code == 403


def test_admin_can_remove_taxonomy_without_removing_articles(client, app):
    client.post(
        "/auth/register",
        data={
            "username": "site_admin",
            "email": "admin@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
    )
    with app.app_context():
        admin = User.query.filter_by(username="site_admin").one()
        admin.role = "admin"
        category = Category(name="Design", slug="design")
        tag = Tag(name="Thoughtful", slug="thoughtful")
        post = Post(
            title="A thoughtful article",
            slug="a-thoughtful-article",
            content="<p>Article content remains after taxonomy changes.</p>",
            status="published",
            author=admin,
            category=category,
            tags=[tag],
        )
        db.session.add(post)
        db.session.commit()
        category_id = category.id
        tag_id = tag.id
        post_id = post.id
    assert client.post(f"/admin/taxonomy/category/{category_id}/delete").status_code == 302
    assert client.post(f"/admin/taxonomy/tag/{tag_id}/delete").status_code == 302
    with app.app_context():
        post = db.session.get(Post, post_id)
        assert post is not None
        assert post.category is None
        assert post.tags == []


def test_admin_cannot_delete_self_but_can_remove_member(client, app):
    client.post(
        "/auth/register",
        data={
            "username": "site_admin",
            "email": "admin@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
    )
    with app.app_context():
        admin = User.query.filter_by(username="site_admin").one()
        admin.role = "admin"
        admin_id = admin.id
        member = User(username="member", email="member@example.com")
        member.set_password("LongEnoughPassword!23")
        db.session.add(member)
        db.session.commit()
        member_id = member.id
    response = client.post(f"/admin/users/{admin_id}/delete", follow_redirects=True)
    assert b"cannot delete your own account" in response.data
    assert client.post(f"/admin/users/{member_id}/delete").status_code == 302
    with app.app_context():
        assert db.session.get(User, admin_id) is not None
        assert db.session.get(User, member_id) is None
