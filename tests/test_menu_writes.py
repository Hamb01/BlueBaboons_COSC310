import pytest

from app.repositories.restaurant_repository import RestaurantRepository
from app.core.exceptions import DataPersistenceError


ITEM = dict(name="Soup", description="Vegetable soup", price=5.25, availability=True)


def test_create_persists_and_generates_unique_ids(client, isolated_data_dir):
    first = client.post("/restaurants/r01/menu", json=ITEM)
    second = client.post("/restaurants/r01/menu", json=ITEM)
    assert first.status_code == second.status_code == 201
    item = first.json()
    assert item["id"] != second.json()["id"]
    assert item["restaurant_id"] == "r01"
    assert client.get(f"/restaurants/r01/menu/{item['id']}").json() == item
    reloaded = RestaurantRepository(isolated_data_dir)
    assert item in reloaded.get_menu_data("r01")


def test_patch_preserves_fields_and_does_not_duplicate(client, isolated_data_dir):
    before = client.get("/restaurants/r01/menu").json()
    original = before[0]
    response = client.patch(f"/restaurants/r01/menu/{original['id']}",
                            json={"price": 0, "availability": False})
    assert response.status_code == 200
    expected = {**original, "price": 0, "availability": False}
    assert response.json() == expected
    menu = RestaurantRepository(isolated_data_dir).get_menu_data("r01")
    assert len(menu) == len(before)
    assert menu[0] == expected


def test_put_replaces_fields(client, isolated_data_dir):
    response = client.put("/restaurants/r01/menu/m01", json=ITEM)
    assert response.status_code == 200
    assert response.json() == {**ITEM, "id": "m01", "restaurant_id": "r01"}
    assert RestaurantRepository(isolated_data_dir).get_menu_data("r01")[0] == response.json()


@pytest.mark.parametrize("method,path,payload", [
    ("post", "/restaurants/missing/menu", ITEM),
    ("patch", "/restaurants/missing/menu/m01", {"price": 2}),
    ("put", "/restaurants/r01/menu/missing", ITEM),
    ("patch", "/restaurants/r01/menu/m03", {"price": 2}),
])
def test_unknown_or_wrong_owner_does_not_write(client, isolated_restaurant_repo, method, path, payload):
    before = isolated_restaurant_repo.master_file.read_bytes()
    assert getattr(client, method)(path, json=payload).status_code == 404
    assert isolated_restaurant_repo.master_file.read_bytes() == before


@pytest.mark.parametrize("method,path,payload", [
    ("post", "/restaurants/r01/menu", {**ITEM, "price": -1}),
    ("post", "/restaurants/r01/menu", {**ITEM, "name": ""}),
    ("post", "/restaurants/r01/menu", {**ITEM, "restaurant_id": "r02"}),
    ("patch", "/restaurants/r01/menu/m01", {"price": None}),
    ("patch", "/restaurants/r01/menu/m01", {"price": -1}),
    ("patch", "/restaurants/r01/menu/m01", {"id": "other"}),
    ("put", "/restaurants/r01/menu/m01", {"price": 1}),
])
def test_invalid_writes_leave_storage_unchanged(client, isolated_restaurant_repo, method, path, payload):
    before = isolated_restaurant_repo.master_file.read_bytes()
    assert getattr(client, method)(path, json=payload).status_code == 422
    assert isolated_restaurant_repo.master_file.read_bytes() == before


@pytest.mark.parametrize("method,path,payload", [
    ("post", "/restaurants/r01/menu", ITEM),
    ("patch", "/restaurants/r01/menu/m01", {"price": 1}),
])
def test_save_failure_returns_500_and_restores_memory(client, isolated_restaurant_repo, monkeypatch, method, path, payload):
    before = client.get("/restaurants/r01/menu").json()
    def fail():
        raise DataPersistenceError("private storage details")
    monkeypatch.setattr(isolated_restaurant_repo, "save_to_file", fail)
    response = getattr(client, method)(path, json=payload)
    assert response.status_code == 500
    assert "private storage details" not in response.text
    assert client.get("/restaurants/r01/menu").json() == before
