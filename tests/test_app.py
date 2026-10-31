import pytest

from app import create_app


def test_homepage_and_health_endpoint(client):
    assert client.get("/").status_code == 200
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_custom_not_found_page(client):
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404
    assert b"wandered off" in response.data


def test_production_requires_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY must be configured"):
        create_app("production")
    monkeypatch.setenv("SECRET_KEY", "a-test-production-secret")
    production_app = create_app("production")
    assert production_app.config["DEBUG"] is False
    assert production_app.config["SESSION_COOKIE_SECURE"] is True
