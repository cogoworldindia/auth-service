def test_email_send_success(client, monkeypatch):
    # Mock verification code generation and email send
    from app.utils import verification
    from app.utils import email_client

    async def mock_create_email_verification(email: str):
        return "123456"

    async def mock_send_verification_email(email: str, subject: str, body: str):
        return True

    monkeypatch.setattr(verification, "create_email_verification", mock_create_email_verification, raising=True)
    monkeypatch.setattr(email_client, "send_verification_email", mock_send_verification_email, raising=True)

    resp = client.post("/v1/auth/email/send", params={"email": "test@example.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "Verification email sent" in data["message"]


def test_email_verify_success(client, monkeypatch):
    # Mock provisioning to return an object having user_id
    class FakeAuth:
        def __init__(self, user_id: str):
            self.user_id = user_id

    from app.services.user_provisioning_service import UserProvisioningService
    from app.services.token_service import TokenService
    from app.utils import jwt_utils
    from app.utils import verification

    async def mock_verify_email_code(email: str, code: str):
        return True

    async def mock_ensure_user_and_auth(self, provider, identifier, default_auth_type_id, is_verified, user_status_payload=None):
        return FakeAuth(user_id="u1")

    async def mock_generate_refresh_token(self, user_id: str, metadata=None):
        return "refresh123"

    def mock_create_access_token(data: dict, expires_delta=None) -> str:
        return "access123"

    monkeypatch.setattr(verification, "verify_email_code", mock_verify_email_code, raising=True)
    monkeypatch.setattr(UserProvisioningService, "ensure_user_and_auth", mock_ensure_user_and_auth, raising=True)
    monkeypatch.setattr(TokenService, "generate_refresh_token", mock_generate_refresh_token, raising=True)
    monkeypatch.setattr(jwt_utils, "create_access_token", mock_create_access_token, raising=True)

    resp = client.post("/v1/auth/email/verify", params={"email": "test@example.com", "code": "123456"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    tokens = data["data"]
    assert tokens["access_token"] == "access123"
    assert tokens["refresh_token"] == "refresh123"

