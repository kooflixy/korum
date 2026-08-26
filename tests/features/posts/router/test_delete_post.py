from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.posts.repository import PostRepository


async def make_delete_post_request(
    post_id, access_token: str, client: AsyncClient
) -> Response:
    response = await client.delete(
        f"/api/posts/{post_id}", headers={"Authorization": f"Bearer {access_token}"}
    )
    return response


async def test_delete_post_success(
    client: AsyncClient, session: AsyncSession, base_data: dict, access_tokens: dict
):
    title = "post1"
    author_username = "user1"
    post_id = base_data[title].id
    access_token = access_tokens[author_username]

    response = await make_delete_post_request(
        post_id=post_id, access_token=access_token, client=client
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    post_record = await PostRepository.get(session, post_id)

    assert post_record is not None
    assert post_record.is_deleted is True

    assert post_record.title == title
    assert post_record.content == base_data[title].content
    assert post_record.author_id == base_data[title].author_id


async def test_delete_post_already_deleted(
    client: AsyncClient, base_data: dict, access_tokens: dict
):
    title = "post2"
    author_username = "user2"
    post_id = base_data[title].id
    access_token = access_tokens[author_username]

    response = await make_delete_post_request(
        post_id=post_id, access_token=access_token, client=client
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_post_non_existent(client: AsyncClient, access_tokens: dict):
    author_username = "user1"
    post_id = "999999999"
    access_token = access_tokens[author_username]

    response = await make_delete_post_request(
        post_id=post_id, access_token=access_token, client=client
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_post_invalid_post_id(client: AsyncClient, access_tokens: dict):
    author_username = "user1"
    post_id = "invalid"
    access_token = access_tokens[author_username]

    response = await make_delete_post_request(
        post_id=post_id, access_token=access_token, client=client
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_delete_post_non_existent_token(client: AsyncClient, base_data: dict):
    title = "post1"
    post_id = base_data[title].id
    access_token = "non_existent_token"

    response = await make_delete_post_request(
        post_id=post_id, access_token=access_token, client=client
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_post_expired_token(
    client: AsyncClient, base_data: dict, expired_access_token: str
):
    title = "post1"
    post_id = base_data[title].id
    access_token = expired_access_token

    response = await make_delete_post_request(
        post_id=post_id, access_token=access_token, client=client
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_post_not_author(
    client: AsyncClient, base_data: dict, access_tokens: dict
):
    title = "post1"
    author_username = "user2"
    post_id = base_data[title].id
    access_token = access_tokens[author_username]

    response = await make_delete_post_request(
        post_id=post_id, access_token=access_token, client=client
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
