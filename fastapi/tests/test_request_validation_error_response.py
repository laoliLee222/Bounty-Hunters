from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel


class Credentials(BaseModel):
    username: str
    password: str
    profile: dict
    otp: int


def create_app(*, debug: bool) -> FastAPI:
    app = FastAPI(debug=debug)

    @app.post("/login")
    def login(credentials: Credentials) -> Credentials:
        return credentials  # pragma: no cover

    return app


def test_validation_error_response_includes_request_context_without_body():
    client = TestClient(create_app(debug=False))

    response = client.post(
        "/login?via=test",
        json={"username": "alice", "password": "secret"},
    )

    assert response.status_code == 422
    assert response.json()["path"] == "/login"
    assert response.json()["method"] == "POST"
    assert "body" not in response.json()


def test_validation_error_debug_response_includes_redacted_body():
    client = TestClient(create_app(debug=True))

    response = client.post(
        "/login",
        json={
            "username": "alice",
            "password": "root-password",
            "profile": {
                "name": "Alice",
                "secret": "nested-secret",
                "nested": {
                    "token": "nested-token",
                    "api_key": "nested-api-key",
                    "safe": "visible",
                },
                "sessions": [
                    {"token": "list-token", "label": "mobile"},
                    {"api_key": "list-api-key", "label": "desktop"},
                ],
            },
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["path"] == "/login"
    assert payload["method"] == "POST"
    assert payload["body"] == {
        "username": "alice",
        "password": "***REDACTED***",
        "profile": {
            "name": "Alice",
            "secret": "***REDACTED***",
            "nested": {
                "token": "***REDACTED***",
                "api_key": "***REDACTED***",
                "safe": "visible",
            },
            "sessions": [
                {"token": "***REDACTED***", "label": "mobile"},
                {"api_key": "***REDACTED***", "label": "desktop"},
            ],
        },
    }
