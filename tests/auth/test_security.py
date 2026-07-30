from src.features.auth.security import hash_password, validate_password


def test_password_validation():
    password = "Qwerty123456@"

    hashed_password = hash_password(password)

    assert validate_password(password, hashed_password)
    assert not validate_password("abcdefg", hashed_password)
