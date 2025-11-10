def test_token_refresh_success(client, monkeypatch):
    from app.services.token_service import TokenService
    from app.utils import jwt_utils

    async def mock_validate_refresh_token(self, rt: str):
        return {"user_id": "u1", "metadata": {"email": "e@example.com"}}

    async def mock_rotate_refresh_token(self, rt: str, user_id: str, metadata=None):
        return "newRefresh"

    def mock_create_access_token(data: dict, expires_delta=None):
        return "newAccess"

    monkeypatch.setattr(TokenService, "validate_refresh_token", mock_validate_refresh_token, raising=True)
    monkeypatch.setattr(TokenService, "rotate_refresh_token", mock_rotate_refresh_token, raising=True)
    monkeypatch.setattr(jwt_utils, "create_access_token", mock_create_access_token, raising=True)

    resp = client.post("/v1/auth/token/refresh", json={"refresh_token": "old"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    data = body["data"]
    assert data["access_token"] == "newAccess"
    assert data["refresh_token"] == "newRefresh"


def test_token_refresh_invalid(client, monkeypatch):
    from app.services.token_service import TokenService

    async def mock_validate_refresh_token(self, rt: str):
        raise ValueError("invalid")

    monkeypatch.setattr(TokenService, "validate_refresh_token", mock_validate_refresh_token, raising=True)

    resp = client.post("/v1/auth/token/refresh", json={"refresh_token": "bad"})
    # Controller maps generic exception to 500
    assert resp.status_code == 500
    body = resp.json()
    assert body["status"] == "error"

