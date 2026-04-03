"""
Functional tests for the inventory microservice.
These tests verify that the agent (or oracle) correctly fixed all issues.
"""
import time
import sqlite3
import pytest
import requests

BASE_URL = "http://localhost:8080"
DB_PATH = "/app/inventory.db"


def wait_for_service(timeout: int = 30) -> bool:
    """Poll /health until the service responds or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False


@pytest.fixture(scope="module", autouse=True)
def service_ready():
    """Ensure the service is reachable before running any test."""
    if not wait_for_service(30):
        pytest.fail(
            "Service did not become reachable on port 8080 within 30 seconds. "
            "Make sure /app/start.sh was executed and the service is running."
        )


class TestHealthEndpoint:
    def test_health_returns_200(self):
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code == 200

    def test_health_returns_ok_status(self):
        r = requests.get(f"{BASE_URL}/health")
        data = r.json()
        assert data.get("status") == "ok"


class TestItemsListEndpoint:
    def test_list_items_returns_200(self):
        r = requests.get(f"{BASE_URL}/items")
        assert r.status_code == 200

    def test_list_items_returns_list(self):
        r = requests.get(f"{BASE_URL}/items")
        data = r.json()
        assert isinstance(data, list)


class TestItemsCreateEndpoint:
    def test_create_item_returns_201(self):
        payload = {"name": "widget", "quantity": 10}
        r = requests.post(f"{BASE_URL}/items", json=payload)
        assert r.status_code == 201

    def test_create_item_returns_correct_fields(self):
        payload = {"name": "gadget", "quantity": 5}
        r = requests.post(f"{BASE_URL}/items", json=payload)
        data = r.json()
        assert "id" in data
        assert data["name"] == "gadget"
        assert data["quantity"] == 5

    def test_create_item_assigns_integer_id(self):
        payload = {"name": "doohickey", "quantity": 3}
        r = requests.post(f"{BASE_URL}/items", json=payload)
        data = r.json()
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    def test_create_item_missing_name_returns_422(self):
        r = requests.post(f"{BASE_URL}/items", json={"quantity": 1})
        assert r.status_code == 422

    def test_create_item_missing_quantity_returns_422(self):
        r = requests.post(f"{BASE_URL}/items", json={"name": "thing"})
        assert r.status_code == 422


class TestItemsGetEndpoint:
    def test_get_existing_item(self):
        # Create an item first
        payload = {"name": "sprocket", "quantity": 7}
        create_r = requests.post(f"{BASE_URL}/items", json=payload)
        assert create_r.status_code == 201
        item_id = create_r.json()["id"]

        # Fetch it back
        get_r = requests.get(f"{BASE_URL}/items/{item_id}")
        assert get_r.status_code == 200
        data = get_r.json()
        assert data["id"] == item_id
        assert data["name"] == "sprocket"
        assert data["quantity"] == 7

    def test_get_nonexistent_item_returns_404(self):
        r = requests.get(f"{BASE_URL}/items/999999")
        assert r.status_code == 404

    def test_created_item_appears_in_list(self):
        payload = {"name": "cog", "quantity": 2}
        create_r = requests.post(f"{BASE_URL}/items", json=payload)
        item_id = create_r.json()["id"]

        list_r = requests.get(f"{BASE_URL}/items")
        ids = [item["id"] for item in list_r.json()]
        assert item_id in ids


class TestDatabasePersistence:
    def test_multiple_items_persist(self):
        names = ["alpha", "beta", "gamma"]
        created_ids = []
        for name in names:
            r = requests.post(f"{BASE_URL}/items", json={"name": name, "quantity": 1})
            assert r.status_code == 201
            created_ids.append(r.json()["id"])

        list_r = requests.get(f"{BASE_URL}/items")
        existing_ids = [item["id"] for item in list_r.json()]
        for cid in created_ids:
            assert cid in existing_ids


class TestMigrations:
    def test_items_table_exists_in_db(self):
        """Verify alembic migrations actually ran and created the items table."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='items'"
        )
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "items table not found — migrations did not run"

    def test_items_table_has_correct_columns(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(items)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "id" in columns
        assert "name" in columns
        assert "quantity" in columns

    def test_alembic_version_table_exists(self):
        """Confirm alembic_version table is present, meaning migrations were tracked."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
        )
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "alembic_version table missing — alembic never ran"

    def test_alembic_version_is_correct_revision(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT version_num FROM alembic_version")
        row = cursor.fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "0001"


class TestServicePort:
    def test_service_not_on_wrong_port(self):
        """Service must NOT be reachable on the old broken port 9090."""
        try:
            r = requests.get("http://localhost:9090/health", timeout=2)
            try:
                body = r.json()
                assert not (r.status_code == 200 and body.get("status") == "ok"), (
                    "Service is still running on port 9090 instead of 8080"
                )
            except Exception:
                pass  # Non-JSON response on 9090 is fine
        except requests.exceptions.ConnectionError:
            pass  # Nothing on 9090 — correct

    def test_service_is_on_correct_port(self):
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        assert r.status_code == 200
