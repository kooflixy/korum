import pytest
from fastapi import status
from httpx import AsyncClient

from src.features.users.schemas import UserResponse


@pytest.mark.parametrize(
    "username, password, expected_status_code",
    [
        # ============================ Успешное создание ===============================
        pytest.param(
            "unique_username",
            "password",
            status.HTTP_201_CREATED,
            id="успешная регистрация(стандартные данные) 201",
        ),
        # ============================ Валидация password ===============================
        pytest.param(
            "unique_username",
            "length7",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: пароль ниже минимальной границы(7 символов) 422",
        ),
        pytest.param(
            "unique_username",
            "length8.",
            status.HTTP_201_CREATED,
            id="валидация: пароль на минимальной границе(8 символов) 201",
        ),
        pytest.param(
            "unique_username",
            "length72" + "." * 64,
            status.HTTP_201_CREATED,
            id="валидация: пароль на максимальной границе(72 символа) 201",
        ),
        pytest.param(
            "unique_username",
            "length73" + "." * 65,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: пароль выше максимальной границы(73 символа) 422",
        ),
        # ============================ Валидация username ===============================
        pytest.param(
            "len4",
            "password",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: юзернейм ниже минимальной границы(4 символа) 422",
        ),
        pytest.param(
            "leng5",
            "password",
            status.HTTP_201_CREATED,
            id="валидация: юзернейм на минимальной границе(5 символов) 201",
        ),
        pytest.param(
            "length64" + "_" * 56,
            "password",
            status.HTTP_201_CREATED,
            id="валидация: юзернейм на максимальной границе(64 символа) 201",
        ),
        pytest.param(
            "length64" + "_" * 57,
            "password",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: юзернейм выше максимальной границы(65 символов) 422",
        ),
        pytest.param(
            "user_name",
            "password",
            status.HTTP_201_CREATED,
            id="валидация: нижнее подчеркивание в юзернейме 201",
        ),
        pytest.param(
            "USER_NAME",
            "password",
            status.HTTP_201_CREATED,
            id="валидация: нижнее подчеркивание и заглавные буквы в юзернейме 201",
        ),
        pytest.param(
            "username123",
            "password",
            status.HTTP_201_CREATED,
            id="валидация: цифры в юзернейме 201",
        ),
        pytest.param(
            "   User_name123      ",
            "password",
            status.HTTP_201_CREATED,
            id="валидация: только допустимые символы + пробелы в начале и в конце юзернейма 201",
        ),
        pytest.param(
            "username@",
            "password",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: один недопустимый символ в юзернейме 422",
        ),
        # ============================ Ошибки при создании ===============================
        pytest.param(
            "user1",
            "password",
            status.HTTP_409_CONFLICT,
            id="ошибка: уже занятый username 409",
        ),
    ],
)
async def test_register(
    username, password, expected_status_code, client: AsyncClient, base_data: dict
):
    response = await client.post(
        "/api/auth/register",
        json={"username": username, "password": password},
    )

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_201_CREATED:
        response_json = response.json()

        user = UserResponse.model_validate(response_json)
        assert username.strip() == user.username

        assert "password" not in response_json
        assert "hashed_password" not in response_json
