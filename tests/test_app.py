from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_root_deve_retornar_ok_e_ola_mundo(async_client):
    response = await async_client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}
