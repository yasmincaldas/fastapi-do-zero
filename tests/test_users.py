from http import HTTPStatus

import pytest

from fast_zero.schemas import UserPublic


@pytest.mark.asyncio()
async def test_create_user_endpoint(async_client):
    response = await async_client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


@pytest.mark.asyncio()
async def test_read_users(async_client):
    response = await async_client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


@pytest.mark.asyncio()
async def test_read_users_with_users(async_client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = await async_client.get('/users/')
    assert response.json() == {'users': [user_schema]}


@pytest.mark.asyncio()
async def test_update_user(async_client, user, token):
    response = await async_client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': user.id,
    }


@pytest.mark.asyncio()
async def test_update_integrity_error(async_client, user, other_user, token):
    response_update = await async_client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


@pytest.mark.asyncio()
async def test_delete_user(async_client, user, token):
    response = await async_client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


@pytest.mark.asyncio()
async def test_update_user_with_wrong_user(async_client, other_user, token):
    response = await async_client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


@pytest.mark.asyncio()
async def test_delete_user_wrong_user(async_client, other_user, token):
    response = await async_client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
