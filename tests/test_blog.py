from io import BytesIO

from app.extensions import db
from app.models import Category, Post, Tag, User
from PIL import Image


def _create_post(client, title="A thoughtful article", content="<p>This is a sufficiently long article body.</p>", **extra):
    data = {
        "title": title,
        "excerpt": "A useful summary.",
        "content": content,
        "category_id": "0",
        "tag_ids": [],
        "status": "published",
    }
    data.update(extra)
    return client.post("/article/new", data=data, follow_redirects=True)


def test_author_can_create_and_view_published_article(author, app):
    response = _create_post(author)
    assert response.status_code == 200
    assert b"A thoughtful article" in response.data
    with app.app_context():
        post = Post.query.one()
        assert post.slug == "a-thoughtful-article"
        assert post.status == "published"


def test_article_editor_keeps_content_field_available_without_javascript(author):
    response = author.get("/article/new")
    assert response.status_code == 200
    assert b'<textarea class="form-control" id="content-source"' in response.data
    assert b'<div id="rich-editor" hidden></div>' in response.data


def test_author_can_edit_and_delete_own_article(author, app):
    _create_post(author)
    with app.app_context():
        slug = Post.query.one().slug
    response = author.post(
        f"/article/{slug}/edit",
        data={
            "title": "An edited thoughtful article",
            "excerpt": "Updated.",
            "content": "<p>This updated article has more than twenty characters.</p>",
            "category_id": "0",
            "tag_ids": [],
            "status": "draft",
        },
        follow_redirects=True,
    )
    assert b"Your article has been updated" in response.data
    with app.app_context():
        post = Post.query.one()
        assert post.slug == "an-edited-thoughtful-article"
        assert post.status == "draft"
        slug = post.slug
    response = author.post(f"/article/{slug}/delete", follow_redirects=True)
    assert b"article has been deleted" in response.data
    with app.app_context():
        assert Post.query.count() == 0


def test_author_cannot_modify_another_authors_post(client, author, app):
    _create_post(author)
    with app.app_context():
        post = Post.query.one()
        slug = post.slug
    client.post("/auth/logout")
    client.post(
        "/auth/register",
        data={
            "username": "writer_two",
            "email": "writer2@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
    )
    assert client.get(f"/article/{slug}/edit").status_code == 403
    assert client.post(f"/article/{slug}/delete").status_code == 403


def test_rich_text_is_sanitized(author, app):
    _create_post(
        author,
        content='<p>Hello <script>alert("bad")</script><img src=x onerror="alert(1)">world safely.</p>',
    )
    with app.app_context():
        post = Post.query.one()
        assert "<script" not in post.content
        assert "onerror" not in post.content
        assert "<p>" in post.content


def test_rich_text_keeps_only_local_uploaded_images(author, app):
    _create_post(
        author,
        content=(
            '<p>A safe image description for this article.</p>'
            '<img src="/static/uploads/photo.png" alt="A local photo">'
            '<img src="https://tracker.example/pixel.png" onerror="alert(1)">'
        ),
    )
    with app.app_context():
        content = Post.query.one().content
        assert '/static/uploads/photo.png' in content
        assert 'alt="A local photo"' in content
        assert "tracker.example" not in content
        assert "onerror" not in content


def test_inline_image_upload_validates_image_and_returns_local_url(author, app):
    image_data = BytesIO()
    Image.new("RGB", (4, 4), color="green").save(image_data, format="PNG")
    image_data.seek(0)
    response = author.post(
        "/article/images",
        data={"image": (image_data, "inline.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    assert response.json["url"].startswith("/static/uploads/inline-")
    assert response.json["url"].endswith(".png")

    invalid_response = author.post(
        "/article/images",
        data={"image": (BytesIO(b"not an image"), "fake.png")},
        content_type="multipart/form-data",
    )
    assert invalid_response.status_code == 400
    assert "valid supported image" in invalid_response.json["error"]


def test_search_category_tag_combination_and_pagination(author, app):
    with app.app_context():
        category = Category(name="Design", slug="design")
        tag = Tag(name="Craft", slug="craft")
        db.session.add_all([category, tag])
        db.session.commit()
        user = User.query.filter_by(username="writer_one").one()
        for index in range(3):
            db.session.add(
                Post(
                    title=f"Design notes {index}",
                    slug=f"design-notes-{index}",
                    content="Writing about visual design and careful craft.",
                    status="published",
                    author=user,
                    category=category,
                    tags=[tag],
                )
            )
        db.session.add(
            Post(
                title="Unrelated story",
                slug="unrelated-story",
                content="This one is not categorized.",
                status="published",
                author=user,
            )
        )
        db.session.commit()
    response = author.get("/articles?q=design&category=1&tag=1")
    assert response.status_code == 200
    assert b"3 stories" in response.data
    assert b"Unrelated story" not in response.data
    assert b"Next" in response.data
    response = author.get("/articles?q=CRAFT")
    assert response.status_code == 200
    assert b"Design notes" in response.data


def test_draft_is_hidden_from_public(author, app):
    _create_post(author, title="A private article", status="draft")
    assert b"A private article" not in author.get("/").data
    with app.app_context():
        post = Post.query.one()
        slug = post.slug
    assert author.get(f"/article/{slug}").status_code == 200
