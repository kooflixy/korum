import pytest
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.posts.repository import PostRepository
from src.features.posts.schemas import PostResponse
from src.features.users.schemas import UserResponse


async def make_create_post_request(
    post_data: dict, access_token: str, client: AsyncClient
) -> Response:
    response = await client.post(
        "/api/posts/create",
        json=post_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response


@pytest.mark.parametrize(
    "post_data, expected_status_code",
    [
        # ============================ Успешное создание ===============================
        pytest.param(
            {
                "title": "title",
                "content": "content",
            },
            status.HTTP_201_CREATED,
            id="успешное создание(стандартные данные) 201",
        ),
        pytest.param(
            {
                "title": "title",
            },
            status.HTTP_201_CREATED,
            id="успешное создание при отсутствии content 201",
        ),
        # ============================ Валидация title ===============================
        pytest.param(
            {},
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: отсутствие title 422",
        ),
        pytest.param(
            {
                "title": "",
            },
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: title ниже минимальной границы(0 символов) 422",
        ),
        pytest.param(
            {
                "title": "1",
            },
            status.HTTP_201_CREATED,
            id="валидация: title на минимальной границе(1 символ) 201",
        ),
        pytest.param(
            {
                "title": "length256" + "." * 247,
            },
            status.HTTP_201_CREATED,
            id="валидация: title на максимальной границе(256 символов) 201",
        ),
        pytest.param(
            {
                "title": "length256" + "." * 248,
            },
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: title выше максимальной границы(257 символов) 422",
        ),
        # ============================ Валидация content ===============================
        pytest.param(
            {
                "title": "title",
                "content": "",
            },
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: content ниже минимальной границы(0 символов) 422",
        ),
        pytest.param(
            {
                "title": "title",
                "content": "1",
            },
            status.HTTP_201_CREATED,
            id="валидация: content на минимальной границе(1 символ) 201",
        ),
        pytest.param(
            {
                "title": "title",
                "content": "length4096" + "." * 4086,
            },
            status.HTTP_201_CREATED,
            id="валидация: content на максимальной границе(4096 символов) 201",
        ),
        pytest.param(
            {
                "title": "title",
                "content": "length4097" + "." * 4087,
            },
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: content выше максимальной границы(4097 символов) 422",
        ),
    ],
)
# fmt: off
async def test_create_post(
    post_data: dict, expected_status_code,
    client: AsyncClient, base_data: dict, access_tokens: dict, session: AsyncSession,
):
# fmt: on
    username = "user1"
    access_token = access_tokens[username]

    response = await make_create_post_request(
        post_data=post_data, access_token=access_token, client=client
    )

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_201_CREATED:
        response_json = response.json()
        assert PostResponse.model_validate(response_json)

        assert response_json['title'] == post_data['title']
        assert response_json['content'] == post_data.get('content')

        assert UserResponse.model_validate(response_json['author'])

        assert response_json['author']['id'] == base_data[username].id
        assert response_json['author']['username'] == username

        assert 'password' not in response_json['author']
        assert 'hashed_password' not in response_json['author']

        post_record = await PostRepository.get(session, response_json['id'])

        assert post_record is not None

        assert post_record.title == post_data['title']
        assert post_record.content == post_data.get('content')

        assert post_record.author_id == base_data[username].id
        assert post_record.is_deleted is False


async def test_create_post_non_existent_token(client: AsyncClient):
    post_data = {"title": "title", "content": "content"}
    response = await make_create_post_request(
        post_data=post_data, access_token="non_existent_token", client=client
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_create_post_expired_token(
    client: AsyncClient, expired_access_token: str
):
    post_data = {"title": "title", "content": "content"}
    response = await make_create_post_request(
        post_data=post_data, access_token=expired_access_token, client=client
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
