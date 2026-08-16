from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status
from freezegun import freeze_time
from httpx import AsyncClient

from src.core.config import settings
from src.features.auth.repository import RefreshTokenRepository
from src.features.auth.schemas import TokenInfo
from src.features.auth.security import decode_jwt, hash_refresh_token


@freeze_time("2026-01-01 12:00:00")
@pytest.mark.parametrize(
    "username, password, expected_status_code",
    [
        # ============================ Успешный вход ===============================
        pytest.param(
            "user1",
            "password1",
            status.HTTP_200_OK,
            id="успешный вход(стандартные данные) 200",
        ),
        # ============================ Валидация username ===============================
        pytest.param(
            "   user1     ",
            "password1",
            status.HTTP_200_OK,
            id="валидация: удаление пробелов в начале и конце юзернейма 200",
        ),
        pytest.param(
            "USER1",
            "password1",
            status.HTTP_401_UNAUTHORIZED,
            id="ошибка: поле юзернейма регистрозависимое 401",
        ),
        pytest.param(
            "",
            "password",
            status.HTTP_401_UNAUTHORIZED,
            id="валидация: работоспособность при пустом юзернейме 401",
        ),
        pytest.param(
            "        ",
            "password",
            status.HTTP_401_UNAUTHORIZED,
            id="валидация: работоспособность при юзернейме только из пробелов 401",
        ),
        # ============================ Иные ошибки при входе ===============================
        pytest.param(
            "non_existent_user",
            "password1",
            status.HTTP_401_UNAUTHORIZED,
            id="ошибка: несуществующий юзернейм 401",
        ),
        pytest.param(
            "user1",
            "incorrect_password",
            status.HTTP_401_UNAUTHORIZED,
            id="ошибка: неверный пароль 401",
        ),
        pytest.param(
            "user1",
            "",
            status.HTTP_401_UNAUTHORIZED,
            id="ошибка: работоспособность при отсутствии пароля 401",
        ),
    ],
)
async def test_login(
    username,
    password,
    expected_status_code,
    client: AsyncClient,
    base_data: dict,
    session,
):
    response = await client.post(
        "/api/auth/login",
        data=dict(username=username, password=password),
    )

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        response_json = response.json()

        assert TokenInfo.model_validate(response_json)
        assert response_json["token_type"] == "Bearer"

        jwt_payload = decode_jwt(response_json["access_token"])

        assert "username" in jwt_payload
        assert jwt_payload["username"] == username.strip()

        expected_datetime = int(datetime.now(tz=timezone.utc).timestamp())

        assert "sub" in jwt_payload
        assert isinstance(jwt_payload["sub"], str)

        assert "iat" in jwt_payload
        assert jwt_payload["iat"] == expected_datetime

        assert "exp" in jwt_payload
        assert (
            jwt_payload["exp"]
            == expected_datetime + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        assert "password" not in jwt_payload
        assert "hashed_password" not in jwt_payload

        assert "refresh_token" in response_json
        hashed_refresh_token = hash_refresh_token(response_json["refresh_token"])

        refresh_token = await RefreshTokenRepository.get_by_hash(
            session, hashed_refresh_token
        )

        assert refresh_token
        assert refresh_token.token_hash == hashed_refresh_token
        assert refresh_token.expires_at == refresh_token.created_at + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        assert refresh_token.is_used == False
        assert refresh_token.is_revoked == False
