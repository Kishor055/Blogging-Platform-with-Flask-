import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app(tmp_path):
    application = create_app("testing")
    upload_folder = tmp_path / "uploads"
    upload_folder.mkdir()
    application.config.update(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'test.db'}",
        UPLOAD_FOLDER=str(upload_folder),
        POSTS_PER_PAGE=2,
    )
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def author(client):
    client.post(
        "/auth/register",
        data={
            "username": "writer_one",
            "email": "writer@example.com",
            "password": "LongEnoughPassword!23",
            "confirm_password": "LongEnoughPassword!23",
        },
        follow_redirects=True,
    )
    return client
