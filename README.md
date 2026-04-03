# AI Terminal Agent

A "Hard" DevOps/SWE task built for the [Terminal Bench 2.0](https://harborframework.com/docs/) framework.

## Task Summary

An AI agent is dropped into a Linux container with a broken FastAPI inventory microservice. The service fails to start due to three independent, cascading bugs. The agent must diagnose each failure from logs and code, apply fixes, and get the service running correctly on port **8080**.

## Bugs Hidden in the Environment

| # | Location | Bug |
|---|----------|-----|
| 1 | `environment/app/requirements.txt` | `pydantic==1.10.13` — incompatible with `fastapi==0.103.2` which requires pydantic v2 |
| 2 | `environment/app/service.conf` | `SERVICE_PORT=9090` — service binds to wrong port; must be 8080 |
| 3 | `environment/app/main.py` | `os.environ.get("DB_URL", ...)` — wrong env var name; `start.sh` exports `DATABASE_URL` |

All three must be fixed for the test suite to pass.

## Structure

```
.
├── task.toml               # Harbor task configuration
├── instruction.md          # Prompt shown to the AI agent
├── environment/            # Docker environment the agent works inside
│   ├── Dockerfile
│   └── app/
│       ├── main.py         # FastAPI application (contains bug 3)
│       ├── requirements.txt# Pinned deps (contains bug 1)
│       ├── start.sh        # Service launcher (reads service.conf)
│       ├── service.conf    # Runtime config (contains bug 2)
│       ├── alembic.ini     # Alembic configuration
│       └── migrations/     # Alembic migration scripts
├── solution/
│   └── solve.sh            # Golden solution script
└── tests/
    ├── test_outputs.py     # Pytest functional test suite
    └── test.sh             # Test runner (do not modify)
```

## Running Locally

### Prerequisites

- Docker running
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed
- Harbor CLI: `uv tool install harbor`
- Groq API key (set `GROQ_API_KEY` in your environment)

### Step 1 — Run the Oracle (verifies your golden solution)

```bash
harbor run -p "." -a oracle
```

This should pass all tests before you run the agent.

### Step 2 — Run the AI Agent

```bash
harbor run -p "." -a terminus-2 --model groq/moonshotai/kimi-k2-instruct-0905 -k 10 -n 10
```

## Difficulty

Target success rate: **> 0% and < 70%** across 10 agent runs.

The agent must:
- Diagnose a pydantic v1/v2 version conflict from pip/uvicorn error output
- Trace port configuration through an indirection (`start.sh` → `service.conf`)
- Spot an env var name mismatch between `main.py` and `start.sh`

Simple `cat`-ing files is not enough — the agent needs to reason across multiple files and understand Python packaging semantics.

## Test Coverage

18 functional tests across 6 classes:

- `TestHealthEndpoint` — `/health` returns `{"status": "ok"}`
- `TestItemsListEndpoint` — GET `/items` returns a list
- `TestItemsCreateEndpoint` — POST `/items` creates items, validates input
- `TestItemsGetEndpoint` — GET `/items/{id}` fetches by ID, 404 on missing
- `TestDatabasePersistence` — multiple items persist and appear in list
- `TestMigrations` — alembic ran, `items` table exists with correct schema
- `TestServicePort` — service is on 8080, not 9090
