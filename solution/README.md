# Solution

`solve.sh` is the golden solution — the ideal human-written fix for all three bugs.

## What It Does

1. Upgrades `pydantic` from `1.10.13` to `2.5.3` in `requirements.txt` and reinstalls deps
2. Corrects `SERVICE_PORT` from `9090` to `8080` in `service.conf`
3. Fixes the env var name from `DB_URL` to `DATABASE_URL` in `main.py`
4. Starts the service via `/app/start.sh` and waits for it to be healthy

## Usage

This is run automatically by the Harbor oracle:

```bash
harbor run -p "." -a oracle
```

Do not run `solve.sh` manually against a live agent session.
