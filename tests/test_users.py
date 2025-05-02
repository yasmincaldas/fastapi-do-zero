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
async def test_update_user_integrity_error_username(async_client, user, token):
    await async_client.post(
        '/users/',
        json={
            'username': 'existing_user',
            'email': 'existing@example.com',
            'password': 'secret',
        },
    )

    response = await async_client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'existing_user',
            'email': 'newemail@example.com',
            'password': 'newpassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == 'Username or Email already exists'


@pytest.mark.asyncio()
async def test_delete_user(async_client, user, token):
    response = await async_client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
