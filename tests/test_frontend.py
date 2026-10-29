from fastapi.testclient import TestClient
from app.repositories.restaurant_repository import RestaurantRepository


def test_frontend_and_assets_are_served(client: TestClient):
    """The frontend loads alongside the API without a separate build server."""
    response = client.get('/ui/')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert '<form id="filters"' in response.text
    assert '<form id="restaurant-form"' in response.text
    assert '<form id="menu-item-form"' in response.text
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
    assert client.get(f'/restaurants/{restaurant_id}/menu').json() == []
    reloaded = RestaurantRepository(isolated_data_dir)
    assert reloaded.get_restaurant_data(restaurant_id)['name'] == payload['name']


def test_frontend_add_menu_item_flow(client: TestClient, isolated_data_dir):
    """The add-item form's exact payload creates an item that the menu panel then lists."""
    form_payload = {'restaurant_id': 0, 'name': 'Fish Taco', 'description': 'Battered fish with slaw',
                    'price': 8.25, 'availability': False}
    response = client.post('/restaurant/r01/menu', json=form_payload)
    assert response.status_code == 201
    item = response.json()['item']

    menu = client.get('/restaurants/r01/menu').json()
    assert item in menu
    assert item['availability'] is False
    reloaded = RestaurantRepository(isolated_data_dir)
    assert item in reloaded.get_restaurant_data('r01')['menu']
