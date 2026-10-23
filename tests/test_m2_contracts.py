import json
from pathlib import Path

import pytest

from app.core.exceptions import DataPersistenceError, MixedRestaurantCartError
from app.main import app, handle_domain_error
from app.repositories.json_file_store import JsonFileStore
from app.schemas.user_schema import UserRole

# These tests pin down the M2 API contract. They stay true once the stubs are implemented,
# so nobody should need to delete them: if one breaks, the contract changed and the team should agree on it.

M2_ROUTES = [
    ("post", "/auth/register"),
    ("post", "/auth/login"),
    ("get", "/customers/me"),
    ("patch", "/customers/me"),
    ("put", "/customers/me/address"),
    ("post", "/customers/me/deactivate"),
    ("get", "/cart"),
    ("delete", "/cart"),
    ("post", "/cart/items"),
    ("patch", "/cart/items/{menu_item_id}"),
    ("delete", "/cart/items/{menu_item_id}"),
    ("post", "/orders/checkout"),
    ("get", "/orders"),
    ("get", "/orders/{order_id}"),
]

# (method, url, json body) for every route that requires a signed-in user
PROTECTED_REQUESTS = [
    ("get", "/customers/me", None),
    ("patch", "/customers/me", {"name": "New Name"}),
    ("put", "/customers/me/address", {"delivery_address": "1 Test St"}),
    ("post", "/customers/me/deactivate", None),
    ("get", "/cart", None),
    ("delete", "/cart", None),
    ("post", "/cart/items", {"restaurant_id": "r01", "menu_item_id": "m01", "quantity": 1}),
    ("patch", "/cart/items/m01", {"quantity": 2}),
    ("delete", "/cart/items/m01", None),
    ("post", "/orders/checkout", None),
    ("get", "/orders", None),
    ("get", "/orders/o01", None),
]

# Everything above except GET /orders/{id}, which admins may also use
CUSTOMER_ONLY_REQUESTS = [request for request in PROTECTED_REQUESTS if request[1] != "/orders/o01"]


@pytest.mark.parametrize("method, path", M2_ROUTES)
def test_m2_route_is_documented_in_openapi(client, method, path):
    paths = client.get("/openapi.json").json()["paths"]
    assert path in paths
    assert method in paths[path]


@pytest.mark.parametrize("method, url, body", PROTECTED_REQUESTS)
def test_protected_route_without_token_returns_401(client, method, url, body):
    response = client.request(method, url, json=body)
    assert response.status_code == 401
    assert response.json()["error"] == "AuthenticationError"
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize("method, url, body", CUSTOMER_ONLY_REQUESTS)
def test_customer_only_route_rejects_admin_with_403(client, login_as, method, url, body):
    login_as("u99", role=UserRole.ADMIN)
    response = client.request(method, url, json=body)
    assert response.status_code == 403
    assert response.json()["error"] == "PermissionDeniedError"


def test_domain_errors_use_the_shared_error_body():
    response = handle_domain_error(None, MixedRestaurantCartError("Cart already holds items from r01."))
    assert response.status_code == 409
    assert json.loads(response.body) == {
        "error": "MixedRestaurantCartError",
        "detail": "Cart already holds items from r01.",
    }


def test_cart_item_quantity_below_one_is_rejected(client, login_as):
    login_as()
    response = client.post("/cart/items", json={"restaurant_id": "r01", "menu_item_id": "m01", "quantity": 0})
    assert response.status_code == 422


############################################################################################
### JsonFileStore (shared persistence helper)
############################################################################################

def test_store_missing_file_loads_as_empty(empty_isolated_data_dir: Path):
    store = JsonFileStore(empty_isolated_data_dir / "Things.json")
    assert store.load() == {}


def test_store_save_then_load_round_trips_and_leaves_no_temp_file(empty_isolated_data_dir: Path):
    store = JsonFileStore(empty_isolated_data_dir / "Things.json")
    records = {"t01": {"id": "t01", "name": "first"}}
    store.save(records)
    assert JsonFileStore(empty_isolated_data_dir / "Things.json").load() == records
    assert not (empty_isolated_data_dir / "Things.json.tmp").exists()


def test_store_corrupted_file_raises_instead_of_returning_empty(empty_isolated_data_dir: Path):
    path = empty_isolated_data_dir / "Things.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(DataPersistenceError):
        JsonFileStore(path).load()


@pytest.mark.parametrize("existing, expected", [
    ({}, "u01"),
    ({"u01": {}, "u02": {}}, "u03"),
    ({"u01": {}, "u07": {}}, "u08"),           # gaps are never refilled
    ({"u01": {}, "x09": {}, "ubad": {}}, "u02"),  # other prefixes / malformed keys ignored
])
def test_store_next_id(existing, expected):
    assert JsonFileStore.next_id(existing, "u") == expected


@pytest.mark.parametrize("file_name", ["Users.json", "Carts.json", "Orders.json"])
def test_seed_data_files_are_valid_json_objects(file_name):
    seed_file = Path(__file__).resolve().parents[1] / "data" / file_name
    assert isinstance(json.loads(seed_file.read_text(encoding="utf-8")), dict)
