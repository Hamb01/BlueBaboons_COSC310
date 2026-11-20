"""#69: typed menu update bodies and documented error responses in OpenAPI."""
import pytest

from app.main import app


@pytest.fixture(scope="module")
def spec():
    return app.openapi()


@pytest.mark.parametrize("method", ["put", "patch"])
def test_menu_update_body_is_typed(spec, method):
    body = spec["paths"]["/restaurant/{restaurant_id}/menu/{item_id}"][method]["requestBody"]
    assert body["content"]["application/json"]["schema"]["$ref"].endswith("/MenuItemUpdate")


@pytest.mark.parametrize("path, method", [
    ("/restaurants/{restaurant_id}", "get"),
    ("/restaurants/{restaurant_id}", "put"),
    ("/restaurants/{restaurant_id}/menu", "get"),
    ("/restaurants/{restaurant_id}/menu/{item_id}", "get"),
    ("/restaurant/{restaurant_id}/menu/{item_id}", "put"),
    ("/restaurant/{restaurant_id}/menu/{item_id}", "patch"),
    ("/restaurant/{restaurant_id}/menu", "post"),
    ("/restaurants/{restaurant_id}/menu/{menu_item_id}", "delete"),
])
def test_detail_and_update_routes_document_404(spec, path, method):
    assert "404" in spec["paths"][path][method]["responses"]


@pytest.mark.parametrize("path, method", [
    ("/restaurants", "post"),
    ("/restaurants/{restaurant_id}", "put"),
    ("/restaurant/{restaurant_id}/menu/{item_id}", "put"),
    ("/restaurant/{restaurant_id}/menu/{item_id}", "patch"),
    ("/restaurant/{restaurant_id}/menu", "post"),
])
def test_write_routes_have_a_response_model_and_document_auth_errors(spec, path, method):
    operation = spec["paths"][path][method]
    success = next(code for code in operation["responses"] if code.startswith("2"))
    assert "schema" in operation["responses"][success]["content"]["application/json"]
    assert {"401", "403"} <= set(operation["responses"])


@pytest.mark.parametrize("body", [{"price": -1}, {"colour": "red"}, {"availability": "maybe"}])
def test_menu_update_rejects_invalid_bodies_with_422(client, isolated_restaurant_repo, body):
    before = isolated_restaurant_repo.master_file.read_bytes()

    response = client.patch("/restaurant/r01/menu/m01", json=body)

    assert response.status_code == 422
    assert isolated_restaurant_repo.master_file.read_bytes() == before
