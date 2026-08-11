"""Unit tests for app.auth.security — no DB, no HTTP."""
import pytest
from jose import jwt

from app.auth.security import (
    ALGORITHM,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.config.settings import get_settings

settings = get_settings()


# ── Password hashing ──────────────────────────────────────────────────────────

def test_hash_differs_from_plaintext():
    assert hash_password("secret") != "secret"


def test_verify_correct_password():
    h = hash_password("mypassword")
    assert verify_password("mypassword", h) is True


def test_verify_wrong_password():
    h = hash_password("mypassword")
    assert verify_password("wrongpassword", h) is False


def test_hash_is_idempotent_but_salted():
    # Two hashes of same input should differ (bcrypt salts each hash)
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2
    # But both must verify correctly
    assert verify_password("same", h1)
    assert verify_password("same", h2)


# ── Token creation ────────────────────────────────────────────────────────────

def test_access_token_has_correct_claims():
    token = create_access_token("user-42", "admin")
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    assert payload["sub"] == "user-42"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_refresh_token_has_correct_claims():
    token = create_refresh_token("user-42", "auditor")
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    assert payload["sub"] == "user-42"
    assert payload["role"] == "auditor"
    assert payload["type"] == "refresh"


def test_refresh_token_expires_later_than_access_token():
    access = create_access_token("u", "admin")
    refresh = create_refresh_token("u", "admin")
    access_exp = jwt.decode(access, settings.secret_key, algorithms=[ALGORITHM])["exp"]
    refresh_exp = jwt.decode(refresh, settings.secret_key, algorithms=[ALGORITHM])["exp"]
    assert refresh_exp > access_exp


# ── Token decoding ────────────────────────────────────────────────────────────

def test_decode_valid_token():
    token = create_access_token("abc", "finance_manager")
    result = decode_token(token)
    assert result["sub"] == "abc"
    assert result["role"] == "finance_manager"


def test_decode_garbage_token_raises():
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_token("not-a-real-token")


def test_decode_tampered_signature_raises():
    token = create_access_token("abc", "admin")
    # Corrupt the signature (last segment)
    header, payload, sig = token.rsplit(".", 2)
    tampered = f"{header}.{payload}.invalidsig"
    with pytest.raises(ValueError):
        decode_token(tampered)


def test_decode_wrong_secret_raises():
    from jose import jwt as jose_jwt
    token = jose_jwt.encode({"sub": "x", "exp": 9999999999}, "other-secret", algorithm=ALGORITHM)
    with pytest.raises(ValueError):
        decode_token(token)
