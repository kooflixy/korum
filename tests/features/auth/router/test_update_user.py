import pytest
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.users.repository import UserRepository
from src.features.users.schemas import UserResponse


async def make_update_user_request(
    update_data: dict, access_token: str, client: AsyncClient
) -> Response:
    resopnse = await client.patch(
        "/api/auth/me",
        json=update_data,
        headers={"Authorization": "Bearer " + access_token},
    )
    return resopnse


@pytest.mark.parametrize(
    "update_data, expected_status_code",
    [
        pytest.param(
            {"username": "new_username"},
            status.HTTP_200_OK,
            id="успешное обновление(стандартные данные) 200",
        ),
        pytest.param(
            {"username": "len4"},
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: юзернейм ниже минимальной границы(4 символа) 422",
        ),
        pytest.param(
            {"username": "leng5"},
            status.HTTP_200_OK,
            id="валидация: юзернейм на минимальной границе(5 символов) 200",
        ),
        pytest.param(
            {"username": "length64" + "_" * 56},
            status.HTTP_200_OK,
            id="валидация: юзернейм на максимальной границе(64 символа) 200",
        ),
        pytest.param(
            {"username": "length64" + "_" * 57},
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: юзернейм выше максимальной границы(65 символов) 422",
        ),
        pytest.param(
            {"username": "user_name"},
            status.HTTP_200_OK,
            id="валидация: нижнее подчеркивание в юзернейме 200",
        ),
        pytest.param(
            {"username": "USER_NAME"},
            status.HTTP_200_OK,
            id="валидация: нижнее подчеркивание и заглавные буквы в юзернейме 200",
        ),
        pytest.param(
            {"username": "username123"},
            status.HTTP_200_OK,
            id="валидация: цифры в юзернейме 200",
        ),
        pytest.param(
            {"username": "   User_name123      "},
            status.HTTP_200_OK,
            id="валидация: только допустимые символы + пробелы в начале и в конце юзернейма 200",
        ),
        pytest.param(
            {"username": "username@"},
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: один недопустимый символ в юзернейме 422",
        ),
        pytest.param(
            {},
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: пустой юзернейм 422",
        ),
        pytest.param(
            {"username": "user2"},
            status.HTTP_409_CONFLICT,
            id="ошибка: уже занятый username 409",
        ),
    ],
)
#fmt: off
async def test_update_user(
    update_data, expected_status_code,
    access_tokens: dict, client: AsyncClient, session: AsyncSession
):
#fmt: on
    username = "user1"
    access_token = access_tokens[username]

    old_user = await UserRepository.get_by_username(session, username)

    response = await make_update_user_request(update_data, access_token, client)

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        response_json = response.json()

        assert UserResponse.model_validate(response_json)

        updated_user = await UserRepository.get_by_username(session, update_data.get('username', old_user.username).strip())

        assert updated_user.username == update_data.get('username', old_user.username).strip()

        assert 'hashed_password' not in response_json
        assert 'password' not in response_json


async def test_update_user_non_existent_token(client: AsyncClient):
    access_token = "non_existent"
    new_username = "new_username"

    response = await make_update_user_request(
        {"username": new_username}, access_token, client
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_update_user_non_existent_token(
    client: AsyncClient, expired_access_token: str
):
    access_token = expired_access_token
    new_username = "new_username"

    response = await make_update_user_request(
        {"username": new_username}, access_token, client
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
