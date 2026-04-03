# Environment

This directory is the Docker environment the AI agent operates inside.

## What the Agent Sees

Everything under `environment/app/` is copied into `/app/` inside the container.

```
/app/
├── main.py         # FastAPI application
├── requirements.txt
├── start.sh        # Entry point — agent must use this to start the service
├── service.conf    # Runtime configuration sourced by start.sh
├── alembic.ini
└── migrations/
    ├── env.py
    ├── script.py.mako
    └── versions/
        └── 0001_create_items_table.py
```

## Dockerfile

- Base: `python:3.12-slim`
- Installs all dependencies from `requirements.txt` at build time
- Does **not** include `tests/` or `solution/` — the agent cannot see those

## Notes

- The service is expected to run on port **8080**
- The agent must start the service via `/app/start.sh`
- All fixes must be made inside `/app/`
