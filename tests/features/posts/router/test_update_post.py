import pytest
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.posts.repository import PostRepository
from src.features.posts.schemas import PostResponse
from src.features.users.schemas import UserResponse


async def make_update_post_request(
    post_id: int, update_data: dict, access_token: str, client: AsyncClient
) -> Response:
    response = await client.patch(
        f"/api/posts/{post_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response


@pytest.mark.parametrize(
    "update_data, expected_status_code",
    [
        # ============================ Успешное создание ===============================
        pytest.param(
            {"title": "update_title", "content": "update_content"},
            status.HTTP_200_OK,
            id="успешное обновление(стандартные данные) 200",
        ),
        pytest.param(
            {},
            status.HTTP_200_OK,
            id="успешное обновление с пустыми введенными данными 200",
        ),
        # ============================ Валидация title ===============================
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
            status.HTTP_200_OK,
            id="валидация: title на минимальной границе(1 символ) 200",
        ),
        pytest.param(
            {
                "title": "length256" + "." * 247,
            },
            status.HTTP_200_OK,
            id="валидация: title на максимальной границе(256 символов) 200",
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
                "content": "",
            },
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: content ниже минимальной границы(0 символов) 422",
        ),
        pytest.param(
            {
                "content": "1",
            },
            status.HTTP_200_OK,
            id="валидация: content на минимальной границе(1 символ) 200",
        ),
        pytest.param(
            {
                "content": "length4096" + "." * 4086,
            },
            status.HTTP_200_OK,
            id="валидация: content на максимальной границе(4096 символов) 200",
        ),
        pytest.param(
            {
                "content": "length4097" + "." * 4087,
            },
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            id="валидация: content выше максимальной границы(4097 символов) 422",
        ),
    ],
)
#fmt: off
async def test_update_post(
    update_data: dict, expected_status_code: int,
    client: AsyncClient, base_data: dict, session: AsyncSession, access_tokens: dict
):
#fmt: on
    username = "user1"
    access_token = access_tokens[username]
    post_title = "post1"
    post = base_data[post_title]

    old_post = await PostRepository.get(session, post.id)

    response = await make_update_post_request(
        post_id=post.id,
        update_data=update_data,
        access_token=access_token,
        client=client,
    )

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        response_json = response.json()

        assert PostResponse.model_validate(response_json)

        assert response_json["title"] == update_data.get("title", old_post.title)
        assert response_json["content"] == update_data.get("content", old_post.content)

        assert "hashed_password" not in response_json
        assert "password" not in response_json

        assert UserResponse.model_validate(response_json["author"])

        assert response_json["author"]["id"] == old_post.author_id
        assert "hashed_password" not in response_json["author"]
        assert "password" not in response_json["author"]

        updated_post_record = await PostRepository.get(session, post.id)

        assert updated_post_record is not None

        assert updated_post_record.title == update_data.get("title", old_post.title)
        assert updated_post_record.content == update_data.get(
            "content", old_post.content
        )

        assert updated_post_record.author_id == old_post.author_id
        assert updated_post_record.is_deleted is False


async def test_update_post_non_existent(client: AsyncClient, access_tokens: dict):
    username = "user1"
    access_token = access_tokens[username]
    post_id = 99999999
    update_data = {"title": "update_title", "content": "update_content"}

    response = await make_update_post_request(
        post_id=post_id,
        update_data=update_data,
        access_token=access_token,
        client=client,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_post_deleted(
    client: AsyncClient, session: AsyncSession, base_data: dict, access_tokens: dict
):
    username = "user2"
    access_token = access_tokens[username]
    post_title = "post2"
    post = base_data[post_title]
    update_data = {"title": "update_title", "content": "update_content"}

    old_post = await PostRepository.get(session, post.id)

    response = await make_update_post_request(
        post_id=post.id,
        update_data=update_data,
        access_token=access_token,
        client=client,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    updated_post_record = await PostRepository.get(session, post.id)

    assert old_post == updated_post_record


async def test_update_post_non_author(
    client: AsyncClient, session: AsyncSession, base_data: dict, access_tokens: dict
):
    username = "user1"
    access_token = access_tokens[username]
    post_title = "post3"
    post = base_data[post_title]
    update_data = {"title": "update_title", "content": "update_content"}

    old_post = await PostRepository.get(session, post.id)

    response = await make_update_post_request(
        post_id=post.id,
        update_data=update_data,
        access_token=access_token,
        client=client,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    updated_post_record = await PostRepository.get(session, post.id)

    assert old_post == updated_post_record


async def test_update_post_deleted_and_non_author(
    client: AsyncClient, session: AsyncSession, base_data: dict, access_tokens: dict
):
    username = "user1"
    access_token = access_tokens[username]
    post_title = "post2"
    post = base_data[post_title]
    update_data = {"title": "update_title", "content": "update_content"}

    old_post = await PostRepository.get(session, post.id)

    response = await make_update_post_request(
        post_id=post.id,
        update_data=update_data,
        access_token=access_token,
        client=client,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    updated_post_record = await PostRepository.get(session, post.id)

    assert old_post == updated_post_record


async def test_update_post_non_existent_token(
    client: AsyncClient, session: AsyncSession, base_data: dict, access_tokens: dict
):
    access_token = "non_existent"
    post_title = "post2"
    post = base_data[post_title]
    update_data = {"title": "update_title", "content": "update_content"}

    old_post = await PostRepository.get(session, post.id)

    response = await make_update_post_request(
        post_id=post.id,
        update_data=update_data,
        access_token=access_token,
        client=client,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    updated_post_record = await PostRepository.get(session, post.id)

    assert old_post == updated_post_record


async def test_update_post_expired_token(
    client: AsyncClient,
    session: AsyncSession,
    base_data: dict,
    expired_access_token: str,
):
    access_token = expired_access_token
    post_title = "post2"
    post = base_data[post_title]
    update_data = {"title": "update_title", "content": "update_content"}

    old_post = await PostRepository.get(session, post.id)

    response = await make_update_post_request(
        post_id=post.id,
        update_data=update_data,
        access_token=access_token,
        client=client,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    updated_post_record = await PostRepository.get(session, post.id)

    assert old_post == updated_post_record
