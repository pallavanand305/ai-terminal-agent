# Tests

Functional test suite in pytest format. Verifies that the inventory service is correctly fixed and running.

## Files

- `test_outputs.py` — all test logic (18 tests across 6 classes)
- `test.sh` — test runner invoked by Harbor; **do not modify**

## Test Classes

| Class | What It Checks |
|-------|---------------|
| `TestHealthEndpoint` | `/health` returns 200 and `{"status": "ok"}` |
| `TestItemsListEndpoint` | GET `/items` returns 200 and a JSON list |
| `TestItemsCreateEndpoint` | POST `/items` creates items, returns 201, validates required fields |
| `TestItemsGetEndpoint` | GET `/items/{id}` returns correct item, 404 for missing |
| `TestDatabasePersistence` | Multiple created items persist and appear in list |
| `TestMigrations` | Alembic ran, `items` table exists with correct columns and revision |
| `TestServicePort` | Service is on port 8080, not the broken default 9090 |

## Important

- Tests are **not** copied into the Docker image — the agent cannot see this directory
- Tests connect to `http://localhost:8080` and `/app/inventory.db` inside the container
- A 30-second readiness poll waits for the service before any test runs
