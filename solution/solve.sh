#!/usr/bin/env bash
# Golden solution: fix all three bugs in the inventory microservice
set -e

# Fix 1: Upgrade pydantic to v2 (compatible with fastapi==0.103.2)
sed -i 's/pydantic==1.10.13/pydantic==2.5.3/' /app/requirements.txt
pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Fix 2: Correct the port in service.conf (9090 -> 8080)
sed -i 's/SERVICE_PORT=9090/SERVICE_PORT=8080/' /app/service.conf

# Fix 3: Fix the env var name in main.py (DB_URL -> DATABASE_URL)
sed -i 's/os.environ.get("DB_URL"/os.environ.get("DATABASE_URL"/' /app/main.py

# Start the service via start.sh (as required by the task constraints)
/app/start.sh &

# Wait for service to be ready
for i in $(seq 1 30); do
    if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
        echo "[solve.sh] Service is up on port 8080."
        exit 0
    fi
    sleep 1
done

echo "[solve.sh] ERROR: Service did not come up in time."
exit 1