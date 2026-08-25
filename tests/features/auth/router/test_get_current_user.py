from fastapi import status
from httpx import AsyncClient

from src.features.users.schemas import UserResponse


async def test_get_current_user_success(
    client: AsyncClient, base_data: dict, access_tokens: dict
):
    username = "user1"

    response = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {access_tokens[username]}"}
    )

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()

    assert UserResponse.model_validate(response_json)

    assert response_json["id"] == base_data[username].id
    assert response_json["username"] == username

    assert "password" not in response_json
    assert "hashed_password" not in response_json


async def test_get_current_user_non_existent_token(client: AsyncClient):
    response = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer non_existent_token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_current_user_expired_token(
    client: AsyncClient, expired_access_token: str
):
    response = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {expired_access_token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
