from fastapi.testclient import TestClient
from app.repositories.restaurant_repository import RestaurantRepository


def test_frontend_and_assets_are_served(client: TestClient):
    """The frontend loads alongside the API without a separate build server."""
    response = client.get('/ui/')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert '<form id="filters"' in response.text
    assert '<form id="restaurant-form"' in response.text
    assert client.get('/ui/app.js').status_code == 200
    assert client.get('/ui/styles.css').status_code == 200
    assert client.get('/health').status_code == 200


def test_frontend_management_api_flow(client: TestClient, isolated_data_dir):
    """The form's create/edit payloads persist and remain discoverable."""
    payload = {
        'name': 'Campus Cafe', 'cuisine': 'Cafe', 'location': 'Kelowna',
        'opening_hours': '08:00-17:00', 'isOpen': True,
    }
    response = client.post('/restaurants', json=payload)
    assert response.status_code == 201
    restaurant_id = response.json()['id']
    payload['name'] = 'Updated Campus Cafe'
    payload['isOpen'] = False
    response = client.put(f'/restaurants/{restaurant_id}', json=payload)
    assert response.status_code == 200
    assert response.json()['isOpen'] is False
    response = client.get('/restaurants', params={'search': 'Updated Campus', 'is_open': 'false'})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == restaurant_id
    assert client.get(f'/restaurants/{restaurant_id}').json()['name'] == payload['name']
    empty_menu_response = client.get(f'/restaurants/{restaurant_id}/menu')
    assert empty_menu_response.status_code == 404
    assert empty_menu_response.json()['detail'] == 'Restaurant has no Menu'
    reloaded = RestaurantRepository(isolated_data_dir)
    assert reloaded.get_restaurant_data(restaurant_id)['name'] == payload['name']
