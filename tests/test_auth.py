from io import BytesIO

from PIL import Image

from app.models import User


def test_registration_hashes_password_and_logs_user_in(client, app):
    response = client.post(
        "/auth/register",
        data={
            "username": "reader_one",
            "email": "Reader@Example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome to BlogSphere" in response.data
    with app.app_context():
        user = User.query.one()
        assert user.email == "reader@example.com"
        assert user.password_hash != "LongEnoughPassword!23"
        assert user.check_password("LongEnoughPassword!23")


def test_duplicate_registration_is_rejected(client, author):
    client.post("/auth/logout")
    response = client.post(
        "/auth/register",
        data={
            "username": "writer_one",
            "email": "writer@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
    )
    assert response.status_code == 200
    assert b"already taken" in response.data


def test_username_uniqueness_is_case_insensitive(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "WriterTwo",
            "email": "writertwo@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    client.post("/auth/logout")
    second_response = client.post(
        "/auth/register",
        data={
            "username": "writertwo",
            "email": "different@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
        follow_redirects=True,
    )
    assert second_response.status_code == 200
    assert b"already taken" in second_response.data


def test_login_logout_and_protected_dashboard(client, author):
    client.post("/auth/logout")
    assert client.get("/dashboard/").status_code == 302
    response = client.post(
        "/auth/login",
        data={"email": "writer@example.com", "password": "LongEnoughPassword!23"},
        follow_redirects=True,
    )
    assert b"Welcome back, writer_one" in response.data
    assert client.post("/auth/logout", follow_redirects=True).status_code == 200


def test_login_rejects_external_next_url(client, author):
    client.post("/auth/logout")
    response = client.post(
        "/auth/login?next=https://example.com",
        data={"email": "writer@example.com", "password": "LongEnoughPassword!23"},
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard/")


def test_profile_is_public_and_owner_can_edit(client, author):
    response = client.get("/auth/profile/writer_one")
    assert response.status_code == 200
    response = client.post(
        "/auth/profile/writer_one",
        data={"username": "writer_renamed", "bio": "A reader and writer."},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"writer_renamed" in response.data
    assert b"A reader and writer." in response.data


def test_profile_supports_avatar_upload(author, app):
    image_data = BytesIO()
    Image.new("RGB", (24, 24), color="blue").save(image_data, format="PNG")
    image_data.seek(0)

    response = author.post(
        "/auth/profile/writer_one",
        data={
            "username": "writer_one",
            "bio": "A reader and writer.",
            "profile_image": (image_data, "avatar.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username="writer_one").one()
        assert user.profile_image is not None
        assert user.profile_image.endswith(".png")
        assert b"/static/uploads/" in response.data
