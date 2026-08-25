import pytest
from fastapi import status
from httpx import AsyncClient

from src.features.posts.schemas import PostResponse


def get_post_id_by_title(title: str, base_data: dict):
    return base_data[title].id


async def test_get_post_success(client: AsyncClient, base_data: dict):
    post_title = "post1"
    post_id = get_post_id_by_title(post_title, base_data)
    response = await client.get(f"/api/posts/{post_id}")

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()

    assert response_json["id"] == post_id
    assert response_json["title"] == post_title

    assert "password" not in response_json["author"]
    assert "hashed_password" not in response_json["author"]

    assert PostResponse.model_validate(response_json)


async def test_get_post_deleted(client: AsyncClient, base_data: dict):
    post_title = "post2"
    post_id = get_post_id_by_title(post_title, base_data)
    response = await client.get(f"/api/posts/{post_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_post_non_existent(client: AsyncClient, base_data: dict):
    post_id = "999999"
    response = await client.get(f"/api/posts/{post_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_post_invalid_post_id(client: AsyncClient, base_data: dict):
    post_id = "invalid"
    response = await client.get(f"/api/posts/{post_id}")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
