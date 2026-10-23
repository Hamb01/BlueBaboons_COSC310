import json
from pathlib import Path

import pytest

# Checks that the proposed M2 routes are wired up. Below that is a checklist of tests the
# team still has to write: each one is skipped until someone replaces it with a real test.

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


@pytest.mark.parametrize("method, path", M2_ROUTES)
def test_m2_route_is_registered(client, method, path):
    paths = client.get("/openapi.json").json()["paths"]
    assert path in paths
    assert method in paths[path]


@pytest.mark.parametrize("file_name", ["Users.json", "Carts.json", "Orders.json"])
def test_seed_data_files_are_valid_json_objects(file_name):
    seed_file = Path(__file__).resolve().parents[1] / "data" / file_name
    assert isinstance(json.loads(seed_file.read_text(encoding="utf-8")), dict)


############################################################################################
### TODO checklist — replace each skip with a real test (move it into your own test file)
############################################################################################

TODO = "TODO: not written yet"


@pytest.mark.skip(reason=TODO)
def test_protected_routes_reject_requests_without_credentials():
    # What status code? What should the body contain?
    ...


@pytest.mark.skip(reason=TODO)
def test_customer_only_routes_reject_other_roles():
    ...


@pytest.mark.skip(reason=TODO)
def test_domain_errors_share_one_error_response_format():
    ...


@pytest.mark.skip(reason=TODO)
def test_json_file_store_handles_missing_and_corrupted_files():
    ...


@pytest.mark.skip(reason=TODO)
def test_json_file_store_ids_are_stable_and_never_reused():
    ...


@pytest.mark.skip(reason=TODO)
def test_tests_never_modify_committed_data_files():
    ...
