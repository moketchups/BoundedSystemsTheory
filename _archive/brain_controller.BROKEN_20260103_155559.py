cd ~/demerzel

python3 - <<'PY'
from pathlib import Path

p = Path("brain_controller.py")
t = p.read_text().splitlines()

# 1) After we create RouterState(), ensure awaiting_confirmation exists
needle = "self.router_state = RouterState()"
for i, line in enumerate(t):
    if needle in line:
        insert_at = i + 1
        break
else:
    raise SystemExit(f"Couldn't find: {needle}")

inject = [
    '        # Back-compat: some RouterState versions may not define this field',
    '        if not hasattr(self.router_state, "awaiting_confirmation"):',
    '            self.router_state.awaiting_confirmation = False',
]
# Only insert once (avoid duplicating if you run patch twice)
if not any('Back-compat: some RouterState versions' in x for x in t):
    t[insert_at:insert_at] = inject

# 2) Replace the direct attribute access with getattr
t = [
    line.replace(
        "if getattr(self.router_state, "awaiting_confirmation", False):",
        'if getattr(self.router_state, "awaiting_confirmation", False):'
    )
    for line in t
]

p.write_text("\n".join(t) + "\n")
print("✅ Patched", p)
PY

