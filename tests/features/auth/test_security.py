from src.features.auth.security import (
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    validate_password,
)


def test_password_validation():
    password = "Qwerty123456@"

    hashed_password = hash_password(password)

    assert validate_password(password, hashed_password)
    assert not validate_password("abcdefg", hashed_password)


def test_refresh_token_hashing():
    refresh_token = generate_refresh_token()

    assert isinstance(refresh_token, str)

    refresh_token_hash = hash_refresh_token(refresh_token)

    assert refresh_token_hash == hash_refresh_token(refresh_token)
    assert refresh_token_hash != hash_refresh_token("abc")
