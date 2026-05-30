import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.utils import format_cpf, generate_hash, generate_uuid, validate_cpf


class TestPasswordHashing:
    def test_hash_password(self):
        hashed = hash_password("senha123")
        assert hashed != "senha123"
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        hashed = hash_password("senha123")
        assert verify_password("senha123", hashed) is True

    def test_verify_password_wrong(self):
        hashed = hash_password("senha123")
        assert verify_password("senha_errada", hashed) is False


class TestJWT:
    def test_create_access_token(self):
        token = create_access_token({"sub": "user-uuid"})
        assert token is not None
        assert isinstance(token, str)

    def test_decode_access_token(self):
        token = create_access_token({"sub": "user-uuid"})
        payload = decode_token(token)
        assert payload["sub"] == "user-uuid"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        token = create_refresh_token({"sub": "user-uuid"})
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_decode_invalid_token(self):
        with pytest.raises(Exception):
            decode_token("token_invalido")


class TestUtils:
    def test_validate_cpf_valid(self):
        assert validate_cpf("52998224725") is True

    def test_validate_cpf_invalid(self):
        assert validate_cpf("00000000000") is False

    def test_validate_cpf_formatted(self):
        assert validate_cpf("529.982.247-25") is True

    def test_validate_cpf_wrong_digits(self):
        assert validate_cpf("12345678901") is False

    def test_generate_uuid(self):
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2
        assert len(uuid1) == 36

    def test_generate_hash(self):
        h1 = generate_hash(b"teste")
        h2 = generate_hash(b"teste")
        h3 = generate_hash(b"diferente")
        assert h1 == h2
        assert h1 != h3
        assert len(h1) == 64

    def test_format_cpf(self):
        assert format_cpf("52998224725") == "529.982.247-25"
        assert format_cpf("529.982.247-25") == "529.982.247-25"
