from http import HTTPStatus

import pytest
from fastapi import HTTPException
from jwt import decode

from fast_zero.security import create_access_token, get_current_user, settings


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded['test'] == data['test']
    assert decoded['exp']


@pytest.mark.asyncio
async def test_jwt_invalid_token(async_client):
    response = await async_client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_get_current_user_none_username():
    access_token = create_access_token(data={'sub': ''})

    with pytest.raises(HTTPException) as exception:
        await get_current_user(token=access_token)

    assert exception.value.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token(async_client, user):
    access_token = create_access_token(data={'sub': 'invalid@email.com'})

    headers = {'Authorization': f'Bearer {access_token}'}
    response = await async_client.delete('/users/1', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
