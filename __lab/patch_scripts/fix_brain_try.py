from pathlib import Path

p = Path("brain_controller.py")
s = p.read_text()
lines = s.splitlines()

# Find the line that triggers the syntax error region (your logs show remainder routing)
targets = [
    "kr = self.engine.process(remainder)",
    "lines = self.engine.process(remainder)",
    "self.engine.process(remainder)",
]

idx = None
for i, ln in enumerate(lines):
    if any(t in ln for t in targets):
        idx = i
        break

if idx is None:
    print("[FIX] Could not find remainder routing call. No changes made.")
    raise SystemExit(1)

indent = len(lines[idx]) - len(lines[idx].lstrip(" "))

# Look backward for an orphan "try:" at the SAME indent level near this call
try_i = None
for j in range(max(0, idx-15), idx):
    if lines[j].strip() == "try:":
        indj = len(lines[j]) - len(lines[j].lstrip(" "))
        if indj == indent:
            try_i = j

if try_i is None:
    print("[FIX] No matching orphan try: found near remainder call. No changes made.")
    raise SystemExit(2)

bak = p.with_suffix(".py.pretryfix.bak")
bak.write_text(s)

del lines[try_i]
p.write_text("\n".join(lines) + "\n")

print(f"[FIX] Removed orphan try: at line {try_i+1}")
print(f"[FIX] Backup written to: {bak}")
