import pytest
from fastapi import status
from httpx import AsyncClient, Response

from src.features.posts.schemas import PostListResponse, PostResponse


async def get_posts_page_request(client: AsyncClient, params) -> Response:
    response = await client.get(
        "/api/posts/page",
        params=params,
    )

    return response


import pytest


#fmt: off
@pytest.mark.parametrize(
    "query_params, is_last_page, expected_post_list",
    [   
        # ============================ Успешный ответ со стандартными данными ===============================
        pytest.param(
            {"page": 1, "per_page": 3, "sort_by": "id", "order_by": "desc"},
            False,
            ['post19', 'post17', 'post16'],
            id='успешный ответ 1 страница id desc 200'
        ),
        pytest.param(
            {"page": 2, "per_page": 3, "sort_by": "id", "order_by": "desc"},
            False,
            ['post15', 'post14', 'post13'],
            id='успешный ответ 2 страница id desc 200'
        ),
        pytest.param(
            {"page": 5, "per_page": 3, "sort_by": "id", "order_by": "desc"},
            True,
            ['post3', 'post1'],
            id='успешный ответ последняя страница id desc 200'
        ),
        pytest.param(
            {"page": 1, "per_page": 3, "sort_by": "id", "order_by": "asc"},
            False,
            ['post1', 'post3', 'post4'],
            id='успешный ответ 1 страница id asc 200'
        ),
        pytest.param(
            {"page": 5, "per_page": 3, "sort_by": "id", "order_by": "asc"},
            True,
            ['post17', 'post19'],
            id='успешный ответ последняя страница id asc 200'
        ),
        pytest.param(
            {},
            False,
            ['post19', 'post17', 'post16', 'post15', 'post14', 'post13', 'post11', 'post10', 'post9', 'post7'],
            id='успешный ответ без введенных параметров 200'
        ),
        # ============================ Успешный ответ с недопустимыми целыми числами в page, per_page ===============================
        pytest.param(
            {"page": -1, "per_page": 3},
            False,
            ['post19', 'post17', 'post16'],
            id='успешный ответ с отрицательной страницей(меняется на 1) 200'
        ),
        pytest.param(
            {"page": 0, "per_page": 3},
            False,
            ['post19', 'post17', 'post16'],
            id='успешный ответ с нулевой страницей(меняется на 1) 200'
        ),
        pytest.param(
            {"per_page": -1},
            False,
            ['post19'],
            id='успешный ответ с отрицательным числом записей на странице(меняется на 1) 200'
        ),
        pytest.param(
            {"per_page": 0},
            False,
            ['post19'],
            id='успешный ответ с нулевым числом записей на странице(меняется на 1) 200'
        ),
        pytest.param(
            {"per_page": 41},
            True,
            ['post19', 'post17', 'post16', 'post15', 'post14', 'post13', 'post11', 'post10', 'post9', 'post7', 'post6', 'post4', 'post3', 'post1'],
            id='успешный ответ с числом записей на странице >40(меняется на 40) 200'
        ),
    ]
)
async def test_get_posts_page(
    query_params,
    is_last_page, expected_post_list,
    client: AsyncClient, base_data: dict, session,
):
#fmt: on
    response = await get_posts_page_request(client, params=query_params)

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()

    assert PostListResponse.model_validate(response_json)

    assert [post["title"] for post in response_json["data"]] == expected_post_list

    assert response_json["is_last_page"] == is_last_page



#fmt: off
@pytest.mark.parametrize(
    "params, expected_status_code",
    [
        pytest.param(
            {'page': 1.2}, status.HTTP_422_UNPROCESSABLE_CONTENT,
            id='ошибка: страница написана float вместо int 422'
        ),
        pytest.param(
            {'page': 'fdasf'}, status.HTTP_422_UNPROCESSABLE_CONTENT,
            id='ошибка: страница написана str вместо int 422'
        ),
        pytest.param(
            {'page': 1.2}, status.HTTP_422_UNPROCESSABLE_CONTENT,
            id='ошибка: количество записей на странице написано float вместо int 422'
        ),
        pytest.param(
            {'page': 'fdasf'}, status.HTTP_422_UNPROCESSABLE_CONTENT,
            id='ошибка: количество записей на странице написано str вместо int 422'
        ),
        pytest.param(
            {'sort_by': 'fdasf'}, status.HTTP_422_UNPROCESSABLE_CONTENT,
            id='ошибка: sort_by написано некорректно 422'
        ),
        pytest.param(
            {'order_by': 'fdasf'}, status.HTTP_422_UNPROCESSABLE_CONTENT,
            id='ошибка: order_by написано некорректно 422'
        ),
    ]
)
async def test_get_posts_page_exceptions(
    params,
    expected_status_code,
    client: AsyncClient, base_data: dict
):
#fmt: on
    response = await get_posts_page_request(client, params=params)

    assert response.status_code == expected_status_code


# async def test_get_posts_page_invalid_sort_by(client: AsyncClient, base_data: dict):
#     response = await get_posts_page_request(client, sort_by='jfkdlasj')

#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# async def test_get_posts_page_invalid_order_by(client: AsyncClient, base_data: dict):
#     response = await get_posts_page_request(client, order_by='jfkdlasj')

#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
