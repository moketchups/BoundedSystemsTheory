#!/usr/bin/env bash
set -euo pipefail

echo "=== DEMERZEL SMOKE TEST ==="
echo "PWD: $(pwd)"
echo

echo "[1/5] Python version"
python3 --version
echo

echo "[2/5] Kernel contract tests"
python3 test_kernel_contract.py
echo

echo "[3/5] Import sanity (router_engine + kernel_router)"
python3 - <<'EOF'
import router_engine, kernel_router
print("router_engine:", router_engine.__file__)
print("kernel_router:", kernel_router.__file__)
EOF
echo

echo "[4/5] Deterministic TIME_QUERY (text path)"
python3 - <<'EOF'
from router_engine import RouterEngine
e = RouterEngine()
lines = e.process("what time is it")
print("\n".join(lines))
EOF
echo

echo "[5/5] Hardware sanity (PING) — safe action, no confirmation"
if [ -f hardware_executor.py ]; then
  python3 hardware_executor.py "PING" || true
else
  echo "hardware_executor.py not found in this folder — skipping"
fi
echo

echo "=== SMOKE TEST COMPLETE ==="

