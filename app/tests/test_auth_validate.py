from fastapi import HTTPException


def test_validate_token_success(client, monkeypatch):
    # Mock AuthService.validate_token to return payload
    from app.services.auth_service import AuthService

    async def mock_validate_token(self, token: str):
        return {"user_id": "u123"}

    monkeypatch.setattr(AuthService, "validate_token", mock_validate_token, raising=True)

    resp = client.get("/v1/auth/validate", headers={"Authorization": "Bearer abc"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["user_id"] == "u123"


def test_validate_token_missing_header(client):
    resp = client.get("/v1/auth/validate")
    assert resp.status_code == 401
    body = resp.json()
    assert body["status"] == "error"
    assert body["code"] == 401


def test_validate_token_invalid(client, monkeypatch):
    from app.services.auth_service import AuthService

    async def mock_validate_token(self, token: str):
        raise HTTPException(status_code=401, detail="Invalid token")

    monkeypatch.setattr(AuthService, "validate_token", mock_validate_token, raising=True)
    resp = client.get("/v1/auth/validate", headers={"Authorization": "Bearer bad"})
    # Controller wraps in 500 error_response on HTTPException
    assert resp.status_code == 500
    body = resp.json()
    assert body["status"] == "error"

