from datetime import datetime, timedelta, timezone

import time_machine
from fastapi import status
from httpx import AsyncClient, Response

from src.core.config import settings
from src.features.auth.repository import RefreshTokenRepository
from src.features.auth.schemas import TokenInfo
from src.features.auth.security import hash_refresh_token


async def make_refresh_request(client, refresh_token: str, user_agent: str) -> Response:
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
        headers={"user-agent": user_agent},
    )
    return response


async def test_refresh_success(client: AsyncClient, base_data: dict, session):
    old_refresh_token = base_data.get("user1_refresh_token")
    user_agent = "user1_user_agent"
    ip_address = "127.0.0.1"

    response = await make_refresh_request(
        client, refresh_token=old_refresh_token, user_agent=user_agent
    )

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()

    assert TokenInfo.model_validate(response_json)

    new_refresh_token = response_json["refresh_token"]

    assert new_refresh_token != old_refresh_token

    new_refresh_token_record = await RefreshTokenRepository.get_by_hash(
        session, token_hash=hash_refresh_token(new_refresh_token)
    )

    assert new_refresh_token_record.token_hash != new_refresh_token
    assert new_refresh_token_record.token_hash == hash_refresh_token(new_refresh_token)

    assert new_refresh_token_record.user_id == base_data["user1"].id
    assert new_refresh_token_record.device_info == user_agent
    assert new_refresh_token_record.ip_address == ip_address

    assert new_refresh_token_record.is_revoked == False
    assert new_refresh_token_record.is_used == False

    assert (
        new_refresh_token_record.created_at
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        == new_refresh_token_record.expires_at
    )

    old_refresh_token_record = await RefreshTokenRepository.get_by_hash(
        session, token_hash=hash_refresh_token(old_refresh_token)
    )

    assert old_refresh_token_record.is_used == True
    assert old_refresh_token_record.is_revoked == False


async def test_refresh_non_existent_token(client: AsyncClient, base_data: dict):
    old_refresh_token = "non_existent_refresh_token"
    user_agent = "user1_user_agent"
    expected_error_details = "Сессия не найдена"

    response = await make_refresh_request(
        client, refresh_token=old_refresh_token, user_agent=user_agent
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_json = response.json()

    assert response_json["detail"] == expected_error_details


async def test_refresh_revoked_token(client: AsyncClient, base_data: dict, session):
    old_refresh_token = base_data.get("user1_refresh_token")
    user_agent = "user1_user_agent"
    expected_error_details = "Сессия принудительно завершена"

    refresh_token_record = await RefreshTokenRepository.get_by_hash(
        session, hash_refresh_token(old_refresh_token)
    )
    refresh_token_record.is_revoked = True
    await session.flush()

    response = await make_refresh_request(
        client, refresh_token=old_refresh_token, user_agent=user_agent
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_json = response.json()

    assert response_json["detail"] == expected_error_details


async def test_refresh_expired_token(client: AsyncClient, base_data: dict, session):
    old_refresh_token = base_data.get("user1_refresh_token")
    user_agent = "user1_user_agent"
    expected_error_details = "Сессия истекла. Пожалуйста, войдите заново"

    future_time = datetime.now(tz=timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS + 1
    )
    with time_machine.travel(future_time):
        response = await make_refresh_request(
            client, refresh_token=old_refresh_token, user_agent=user_agent
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_json = response.json()

    assert response_json["detail"] == expected_error_details
    old_refresh_token_record = await RefreshTokenRepository.get_by_hash(
        session, token_hash=hash_refresh_token(old_refresh_token)
    )

    assert old_refresh_token_record.is_used == False
    assert old_refresh_token_record.is_revoked == False


async def test_refresh_already_used_token(
    client: AsyncClient, base_data: dict, session
):
    old_refresh_token = base_data.get("user1_refresh_token")
    user_agent = "user1_user_agent"
    expected_error_details = (
        "Данный токен уже использовался. В целях безопасности войдите заново"
    )

    # используем старый и создаем новый токен
    response = await make_refresh_request(
        client, refresh_token=old_refresh_token, user_agent=user_agent
    )

    new_refresh_token = response.json()["refresh_token"]

    response = await make_refresh_request(
        client, refresh_token=old_refresh_token, user_agent=user_agent
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_json = response.json()

    assert response_json["detail"] == expected_error_details

    old_refresh_token_record = await RefreshTokenRepository.get_by_hash(
        session, token_hash=hash_refresh_token(old_refresh_token)
    )

    new_refresh_token_record = await RefreshTokenRepository.get_by_hash(
        session, token_hash=hash_refresh_token(new_refresh_token)
    )

    assert old_refresh_token_record.is_revoked == True
    assert new_refresh_token_record.is_revoked == True


async def test_refresh_changed_user_agent(
    client: AsyncClient, base_data: dict, session
):
    old_refresh_token = base_data.get("user1_refresh_token")
    user_agent = "different_user_agent"
    expected_error_details = "Параметры среды изменились. Пожалуйста, войдите заново"

    response = await make_refresh_request(
        client, refresh_token=old_refresh_token, user_agent=user_agent
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_json = response.json()

    assert response_json["detail"] == expected_error_details

    old_refresh_token_record = await RefreshTokenRepository.get_by_hash(
        session, token_hash=hash_refresh_token(old_refresh_token)
    )

    assert old_refresh_token_record.is_revoked == True
