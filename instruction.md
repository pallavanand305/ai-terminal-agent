# Task: Fix the Broken Inventory Microservice

You are a backend engineer on-call. The inventory microservice at `/app` has just been deployed and is completely broken. The service is supposed to run on port **8080** and expose a REST API backed by a SQLite database.

## What You Know

- The service is a FastAPI application located at `/app`
- It uses Alembic for database migrations
- The database file should be at `/app/inventory.db`
- The service should be reachable at `http://localhost:8080`

## Your Goal

Get the service running correctly so that:

1. The service starts successfully and listens on port **8080**
2. The `/health` endpoint returns `{"status": "ok"}`
3. The `/items` endpoint (GET) returns a JSON list (may be empty)
4. The `/items` endpoint (POST) accepts a JSON body `{"name": "<string>", "quantity": <int>}` and creates a new item
5. The `/items/{id}` endpoint (GET) returns the item with the given ID
6. Database migrations run successfully before the service starts

## Constraints

- Do not change the port the service listens on (it must be 8080)
- The final running service process must be started via `/app/start.sh`
- All fixes must be applied inside `/app`
- You may install additional packages if needed

## Hints

- Check the application logs carefully — the errors are real, not simulated
- There may be more than one thing broken
- Read the code before making changes
