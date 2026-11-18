from fastapi.testclient import TestClient
from app.api.deps import get_cart_repository
from app.main import app
from app.repositories.cart_repository import CartRepository
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
        'opening_hours': '08:00-17:00', 'isOpen': True, 'owner_id': 'u99',
        'address': '123 Main Street', 'postal_code': 'v1y 2b3',
        'opening_hours': '08:00-17:00', 'isOpen': True,
    }
    response = client.post('/restaurants', json=payload)
    assert response.status_code == 201
    assert response.json()['postal_code'] == 'V1Y 2B3'
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
    error = empty_menu_response.json()
    assert error['status_code'] == empty_menu_response.status_code
    assert error['message'] == f"Restaurant with id {restaurant_id} has no menu"
    assert error['details'] == 'Menu is empty'
    reloaded = RestaurantRepository(isolated_data_dir)
    assert reloaded.get_restaurant_data(restaurant_id)['name'] == payload['name']


def test_frontend_has_sign_in_and_cart(client: TestClient):
    page = client.get('/ui/').text
    assert '<form id="login-form"' in page
    assert '<dialog id="cart-dialog"' in page
    assert 'id="open-cart"' in page


def test_frontend_sign_in_and_cart_flow(client: TestClient, isolated_data_dir):
    """The same calls the page makes: log in, who am I, add to cart, open the cart."""
    app.dependency_overrides[get_cart_repository] = lambda: CartRepository(data_dir=isolated_data_dir)

    token = client.post('/auth/login', json={'username': 'UserName1', 'password': 'HardPassword1234'}).json()
    headers = {'Authorization': f'Bearer {token}'}

    me = client.get('/customers/me', headers=headers)
    assert me.status_code == 200
    assert me.json()['username'] == 'UserName1'

    added = client.post('/cart/items', headers=headers, json={'restaurant_id': 'r01', 'menu_item_id': 'm01', 'quantity': 1})
    assert added.status_code == 200

    cart = client.get('/cart', headers=headers).json()
    assert [(line['name'], line['quantity']) for line in cart['items']] == [('Beef Taco', 1)]
    assert cart['total'] == 7.99
