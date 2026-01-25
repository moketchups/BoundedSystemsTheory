from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from pathlib import Path
from typing import Dict, List

FILES: List[str] = [
    "brain_controller.py",
    "router_engine.py",
    "kernel_router.py",
    "kernel_contract.py",
    "boundary_gate.py",
    "hardware_executor.py",
    "run_demerzel.py",
    "run_router_repl.py",
    "tests/test_router_invariants.py",
]

LOCK_PATH = Path("baseline_lock.json")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def compute_hashes(repo: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for rel in FILES:
        p = repo / rel
        if not p.exists():
            raise FileNotFoundError(f"Missing required file: {rel}")
        out[rel] = sha256_file(p)
    return out

def hw_probe() -> Dict[str, str]:
    host = os.environ.get("DEMERZEL_PI_HOST", "").strip()
    user = os.environ.get("DEMERZEL_PI_USER", "").strip()
    if not host or not user:
        return {"ok": "skip", "out": "", "err": "DEMERZEL_PI_HOST/DEMERZEL_PI_USER not set"}
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=4", f"{user}@{host}", "echo OK"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        return {"ok": "true" if p.returncode == 0 else "false", "out": (p.stdout or "").strip(), "err": (p.stderr or "").strip()}
    except Exception as e:
        return {"ok": "false", "out": "", "err": str(e)}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--no-hw", action="store_true")
    args = ap.parse_args()

    repo = Path(".").resolve()
    hashes = compute_hashes(repo)

    if args.init:
        payload = {"repo": str(repo), "hashes": hashes}
        if not args.no_hw:
            payload["hw_probe"] = hw_probe()
        LOCK_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print("[OK] wrote baseline_lock.json")
        return 0

    if not LOCK_PATH.exists():
        print("[FAIL] baseline_lock.json not found. Run: python3 baseline_check.py --init")
        return 2

    locked = json.loads(LOCK_PATH.read_text(encoding="utf-8")).get("hashes", {})
    bad = [(k, locked.get(k), v) for k, v in hashes.items() if locked.get(k) != v]
    if bad:
        print("[FAIL] baseline hash mismatch:")
        for k, old, new in bad:
            print(f"  - {k}: LOCKED {old} != CURRENT {new}")
        print("If you EXPECTED changes, re-lock with: python3 baseline_check.py --init")
        return 1

    print("[OK] hashes match baseline_lock.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

