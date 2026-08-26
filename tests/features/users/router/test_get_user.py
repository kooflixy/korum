from fastapi import status
from httpx import AsyncClient

from src.features.users.schemas import UserResponse


async def test_get_user_success(client: AsyncClient, base_data: dict):
    username = "user1"
    user = base_data[username]

    response = await client.get(f"api/users/{user.id}")

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()

    assert UserResponse.model_validate(response_json)

    assert response_json["id"] == user.id
    assert response_json["username"] == username

    assert "password" not in response_json
    assert "hashed_password" not in response_json


async def test_get_user_non_existent(client: AsyncClient):
    user_id = "99999999"

    response = await client.get(f"api/users/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_user_success_invalid_user_id(client: AsyncClient):
    user_id = "invalid"

    response = await client.get(f"api/users/{user_id}")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
